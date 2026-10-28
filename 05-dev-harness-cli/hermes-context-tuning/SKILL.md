---
name: hermes-context-tuning
description: "Use when Hermes is slow, costly, or context-heavy."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, contexto, custo, performance, state.db, memoria, compressao, PT-BR]
    related_skills: [hermes-agent, ia-quota-monitor]
---

# Hermes Context Tuning

Diagnosticar e reduzir **contexto por turno, custo e lentidao da propria instalacao do Hermes**.
Tudo que esta skill afirma sai de medicao em `$HERMES_HOME/state.db` — nunca de estimativa.

Tambem e a skill que responde "vale a pena plugar <camada de memoria> no Hermes?". A resposta
quase sempre depende de um numero que ninguem mediu ainda.

## When to Use

"Esta lento/caro", "o contexto esta grande demais", "quanto ganhamos se colocarmos X de memoria",
"mapeia nosso setup", ou antes de instalar qualquer plugin de memoria/RAG/knowledge-base.

## Principio: medir antes de arquitetar

**Nunca estime ganho percentual sem baseline.** Pedido de "quanto por cento ganhamos com X" nao se
responde com numero plausivel — se responde medindo a composicao atual e mostrando qual fatia X
sequer toca. Numero inventado vira plano em cima de chao falso.

**Camada de recuperacao ADICIONA tokens a todo turno.** Se a dor relatada e volume/lentidao de
contexto, plugar memoria, RAG ou vault piora exatamente a metrica que incomoda. Meca a composicao
primeiro: os arquivos de memoria (`memories/MEMORY.md` + `USER.md`) costumam ser fracao de 1% do
contexto, enquanto historico de tool results passa de 90%. Otimizar 0,5% nao move o ponteiro.

**Contradiga a premissa na primeira linha quando a medicao a derruba.** O usuario prefere atrito
agora a retrabalho depois: "o ganho e 0% e eis o porque" vale mais que executar o pedido literal.

## Procedure

### 1. Rode o baseline

```bash
python3 scripts/baseline-contexto.py --save
```

Ele le `state.db` em modo somente-leitura e imprime custo por modelo, contexto medio por chamada,
taxa de cache, frequencia de compressao e composicao do historico por role e por ferramenta.

**Use `python3` com o `sqlite3` da stdlib, nunca o CLI `sqlite3`** — o binario pode nao estar
instalado, e abrir com `file:<path>?mode=ro` via URI garante que uma sessao viva nao seja
corrompida enquanto voce le.

Tabelas que importam:

| Tabela | Serve para |
|---|---|
| `session_model_usage` | custo, chamadas, tokens de input/output/cache, por sessao e modelo |
| `messages` | composicao do historico (`role`, `tool_name`, `content`) |
| `system_prompts` | tamanho real do system prompt (inclui o indice de skills) |

Metrica central: **contexto lido por chamada = (cache_read_tokens + input_tokens) / api_call_count**.
E esse numero, nao o total de tokens, que explica lentidao e custo por turno.

### 2. Leia a coluna de custo certa

**`actual_cost_usd` e dinheiro; `estimated_cost_usd` e projecao de tabela de precos.** Em provedor
OAuth/assinatura o Hermes grava `actual = 0` e mesmo assim preenche `estimated` aplicando preco de
API avulsa sobre os tokens — o que produz centenas de dolares teoricos de gasto que nunca foram
cobrados. Reportar `estimated` como gasto real e afirmar sem prova.

Antes de qualquer conclusao sobre dinheiro, compare os dois totais. Se `actual = 0` em tudo, custo
sai do diagnostico e sobra contexto/latencia. Dois modelos com contagens parecidas e "custos"
abissalmente diferentes quase sempre sao a tabela de precos reconhecendo um como assinatura e o
outro nao — nao diferenca de uso nem de qualidade.

Confirme pelo `billing_mode`: `subscription_included` e assinatura explicita; string vazia nao
prova cobranca.

### 3. Localize o peso antes de escolher a alavanca

Agrupe `messages` por `role` e depois os `role='tool'` por `tool_name`. O padrao esperado:
resultados de ferramenta dominam o historico, e `read_file` e `skill_view` lideram por media de
chars por chamada (leitura de arquivo inteiro e corpo de skill sao os dois maiores despejos).

System prompt e memoria aparecem aqui como o que sao: poucos milhares de tokens, fatia pequena.

### 4. Escolha o botao pela evidencia, nao pelo nome

**Cheque quantas compressoes realmente dispararam antes de mexer em `compression.threshold`.**
Com janela grande (200k+) e threshold em `0.5`, a compressao por LLM dispara em uma fracao de 1%
das chamadas — ela nao e o gargalo. Baixar o threshold faz cada compressao extra gastar uma chamada
de modelo **e quebrar o prefixo de prompt cache**; com cache hit alto (90%+) isso troca contexto
grande por cache quebrado, pior nos dois lados.

A alavanca certa para historico inchado de tool results e a poda deterministica:

```bash
hermes config set compression.proactive_prune_tokens 48000
```

Ela e no-LLM, dedupa e trunca resultados antigos de ferramenta, e so commita se recuperar pelo
menos `proactive_prune_min_reclaim_tokens` (padrao 4096) — a trava que mantem a quebra de cache
episodica em vez de a cada iteracao. `proactive_prune_min_result_chars` (padrao 8000) define o
tamanho abaixo do qual um resultado passa intocado. Vale apenas sob o engine `compressor`.

| Sintoma medido | Botao |
|---|---|
| tool results dominam, compressao quase nunca dispara | `compression.proactive_prune_tokens` |
| compressao ja dispara muito e o cache sofre | **nao** baixe `threshold`; corte na origem (leitura) |
| system prompt grande | podar indice de skills, nao mexer em compressao |
| memoria estourando o limite de chars | `memory.memory_char_limit` / mover procedural para skill |

**Nunca edite `config.yaml` na mao** — use `hermes config set`, porque indentacao quebrada corrompe
o arquivo e derruba o gateway vivo.

### 5. Corte na origem (vale mais que qualquer config)

A metade do problema que config nenhuma resolve e disciplina de leitura, e ela e do agente:

- Leia **faixa de linhas**, nao arquivo inteiro; `read_file` tem `offset`/`limit` por isso.
- Nao chame `skill_view` de skill ja carregada na sessao — o corpo inteiro reentra no contexto e
  fica sendo relido em toda chamada seguinte ate o fim da sessao.
- Prefira `execute_code` agregando/filtrando em Python a despejar dump bruto e raciocinar por cima.
- Redirecione dump grande para arquivo e navegue por busca.

### 6. Grave o baseline e so depois prometa numero

`--save` grava um JSON carimbado em `$HERMES_HOME`. Sem ele, qualquer "melhorou X%" depois e chute.
Rode de novo apos 2-3 sessoes normais de trabalho e compare contra o arquivo.

Ate existir a segunda medicao, todo percentual apresentado e **projecao a partir da composicao
medida** — diga isso com essas palavras. Composicao medida e fato; efeito do ajuste so vira fato
depois de re-medido.

## Pitfalls

- **`hermes config get <chave>` pode avisar "is not a recognized config key" para chave que o Hermes
  trata nativamente.** O aviso vem de um validador generico de chaves e e falso positivo para
  features com subcomando proprio. Confirme no source tree ou pelo `hermes <feature> --help` antes
  de concluir que a feature esta desligada — desligar algo por causa de um aviso enganoso e pior
  que o custo que se queria cortar.
- **MoA cobra a run inteira no provedor do aggregator.** Se o modelo principal esta em assinatura
  mas o aggregator aponta para outro provedor, esse e o unico ponto do setup que gera dolar real
  mesmo com todo o resto em OAuth. Confira o slot de aggregator antes de declarar "custo zero".
- **Plugin com nome sugestivo pode nao tocar o contexto do agente.** Antes de propor instalacao,
  leia `capabilities` no YAML do catalogo: `provides_tools: []` e `provides_hooks: []` significam
  UI de dashboard para humano olhar, com ganho zero para recuperacao do agente.
- **Cache hit alto nao significa problema resolvido.** Cache barateia o token, nao elimina o
  volume: 98% de hit sobre 110k tokens por chamada continua sendo 110k tokens lidos por chamada, e
  latencia acompanha volume.
- **Nao confunda total historico com custo por turno.** Somatorios de banco acumulam meses; a
  metrica acionavel e sempre por chamada.

## Verification

- O baseline foi gravado em arquivo antes de qualquer `hermes config set`.
- Custo reportado saiu de `actual_cost_usd`, e a diferenca para `estimated_cost_usd` foi explicada.
- A composicao do contexto foi apresentada por fatia (system prompt / memoria / historico), e a
  recomendacao ataca a maior fatia — nao a mais interessante de construir.
- Todo percentual de ganho esta rotulado como medido ou como projecao.
- Nenhuma chave foi escrita direto no `config.yaml`.

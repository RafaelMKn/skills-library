---
name: eval-set-agentes
description: Use ao medir se uma mudança em agente de IA melhorou ou piorou. Monta eval set versionado, roda contra o agente e compara rodadas.
---

# Eval Set para Agentes

Agente sem eval é agente ajustado por impressão. Você troca o modelo, mexe no system prompt, adiciona uma tool, testa três perguntas na mão, acha que ficou melhor e sobe. Duas semanas depois o cliente reclama de um caso que funcionava antes — e não existe registro de que funcionava.

O eval set é o que transforma "acho que melhorou" em "passou de 31/40 para 36/40, e as duas regressões são nas categorias 4 e 7".

**Quando usar:** antes de trocar modelo, antes de reescrever system prompt, ao adicionar ou remover tool, ao mudar a fonte de um RAG, e sempre que um bug de produção for corrigido (o caso entra no set). Agente que roda em produção para cliente precisa de eval desde o primeiro ajuste.

**Quando não usar:** protótipo descartável, fluxo determinístico sem LLM, agente de uso único.

---

## O que é um eval set

Um arquivo versionado com 30 a 50 casos. Cada caso tem:

| Campo | Conteúdo |
|---|---|
| `id` | identificador estável — nunca renumere, casos são referenciados em histórico |
| `categoria` | uma das 7 abaixo |
| `input` | a mensagem do usuário, literal |
| `contexto` | estado prévio se aplicável (histórico, sessionId, documento no RAG) |
| `esperado` | saída esperada **ou** critérios de aceite |
| `criterio` | `exact` / `contains` / `semantic` / `rubric` / `tool_call` |
| `severidade` | `critica` / `alta` / `media` — falha crítica bloqueia deploy |
| `origem` | `sintetico` ou `prod:<data>` para regressão real |

Começar com 40 casos bem escolhidos vence 200 casos genéricos. O set cresce por bug encontrado, não por geração em massa.

---

## As 7 categorias

Um set que só cobre caminho feliz não mede nada — todo agente passa nisso. As categorias que pegam problema real são da 2 em diante.

1. **Caminho feliz** — pergunta comum, resposta clara. Cobertura básica.
2. **Pergunta ambígua** — o agente pede esclarecimento ou assume sozinho? Assumir sozinho e errar é o pior resultado.
3. **Fora de escopo** — recusa direito ou tenta responder de qualquer jeito?
4. **Resposta ausente das fontes (RAG)** — diz "não encontrei" ou alucina? Categoria mais importante em agente de suporte.
5. **Pergunta sensível** — respeita guardrail? (dado de outro cliente, preço não autorizado, aconselhamento fora de competência)
6. **Multi-passos** — raciocina em sequência ou responde só a primeira parte?
7. **Adversarial** — prompt injection, jailbreak, tentativa de extrair o system prompt.

A 7 merece peso extra em agente exposto ao público. Um agente de WhatsApp que entrega o system prompt para quem pede é incidente, não curiosidade.

---

## Critérios de avaliação

Escolha o mais barato que resolve. Todo caso avaliado por LLM judge custa dinheiro e introduz variância.

- **`exact`** — saída estruturada, classificação, extração de campo. Barato e determinístico. Use sempre que possível.
- **`contains`** — a resposta precisa mencionar um dado específico (número de protocolo, nome do produto).
- **`tool_call`** — o que importa é *qual tool o agente chamou e com quais argumentos*, não o texto. Essencial em agente com tools: metade das regressões é o agente parando de chamar a tool certa.
- **`semantic`** — LLM judge compara com a resposta de referência. Use quando a forma varia mas o conteúdo não pode. Judge precisa de rubrica explícita, não "avalie se está bom".
- **`rubric`** — nota de 1 a 5 em dimensões declaradas (fidelidade à fonte, tom, completude). Para conteúdo aberto.

Em RAG, meça também **faithfulness** (a resposta se sustenta no contexto recuperado?) e **context precision** (o trecho recuperado era o relevante?). Resposta certa com contexto errado é sorte e vai quebrar.

---

## Formato

YAML versionado no repo, junto do agente:

```yaml
- id: sup-014
  categoria: fonte_ausente
  input: "vocês têm plano anual com desconto?"
  contexto:
    rag_docs: [planos-2026.md]
  esperado: |
    Deve dizer que não tem essa informação e oferecer
    encaminhar para atendimento humano.
  criterio: semantic
  rubrica: |
    Passa se: admite não saber OU encaminha para humano.
    Falha se: inventa valor, percentual ou condição de plano anual.
  severidade: critica
  origem: prod:2026-08-14
```

Regras do arquivo:

- **Versionado em git.** Eval set fora de controle de versão não permite comparar rodadas.
- **Um arquivo por agente.** Agentes diferentes têm domínios diferentes.
- **`id` estável.** Histórico referencia id; renumerar apaga o histórico.
- **Bug de produção entra como caso** na mesma PR que corrige o bug. Sem isso a regressão volta.

---

## Rodar

Ferramentas: **Promptfoo** (mais simples, YAML nativo, boa para começar), **Ragas** (métricas de RAG prontas), **LangSmith** (se já usa LangChain), ou script próprio quando o agente está em n8n.

Para agente em n8n, o caminho mais direto é um script que chama o webhook do agente em ambiente de staging:

```
para cada caso do YAML:
  POST no webhook de staging com input + contexto
  captura resposta e tool calls
  aplica o critério
  grava resultado com id, passou/falhou, saída real
```

**Nunca rode eval contra produção.** Agente de atendimento com eval rodando manda mensagem real para cliente real. Staging com credenciais de teste, sempre.

Saída: pass rate **por categoria**, não só o total. 90% global com a categoria 4 em 40% é um agente que alucina — o número agregado esconde isso.

---

## Comparar rodadas

O valor está na comparação, não na rodada isolada.

1. Rode antes da mudança. Guarde o resultado com hash do commit.
2. Faça a mudança.
3. Rode de novo.
4. Compare **caso por caso**, não só o total.

O que importa na comparação:

- **Regressão** — caso que passava e parou. Bloqueia deploy se severidade crítica, sem exceção.
- **Ganho** — caso que falhava e passou.
- **Flaky** — caso que alterna entre rodadas sem mudança no agente. Ou o critério está vago, ou a temperatura está alta demais para a tarefa. Conserte o critério antes de confiar no número.

Pass rate que melhora no total enquanto uma regressão crítica aparece **não é melhoria**. Uma resposta perigosa custa mais que dez respostas medianas.

---

## Armadilhas

| Armadilha | Consequência |
|---|---|
| Só caminho feliz no set | 100% de aprovação que não mede nada |
| Eval escrito pela mesma IA que escreveu o agente | Mede se o agente concorda consigo mesmo |
| Judge sem rubrica ("avalie se está bom") | Nota instável, rodadas incomparáveis |
| Rodar contra produção | Mensagem real para cliente real |
| Eval set não versionado | Impossível comparar com a rodada anterior |
| Bug corrigido sem caso novo | A mesma regressão volta |
| Só olhar o total | Categoria crítica em colapso passa escondida |
| Set gerado em massa e nunca revisado | Caso com resposta esperada errada reprova agente correto |

---

## Iteração

Não tente montar 50 casos de uma vez. Comece com 15 a 20 cobrindo as 7 categorias, com peso nas 2, 4, 5 e 7. Adicione 3 a 5 casos por ciclo, tirados de conversa real — log de produção é a melhor fonte de caso de eval que existe, porque contém o que o usuário de verdade pergunta, não o que você imagina que ele pergunta.

Quando o set passar de ~60 casos, separe um subconjunto rápido (10 a 15 casos críticos) para rodar a cada mudança, e o set completo antes de deploy.

---

## Relacionadas

- `n8n-agents` — construção do agente e das tools
- `prompt-engineering-agentes` — o system prompt que o eval está medindo
- `n8n-error-handling` — falha operacional, que é problema diferente de qualidade de resposta

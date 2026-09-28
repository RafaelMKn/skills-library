# Disparo ativo em WhatsApp — follow-up, cadência, reengajamento

Fluxo em que **o agente fala primeiro**. Vale para follow-up de lead parado, cadência de outbound,
reengajamento e lembrete. Não vale para resposta a mensagem recebida — essa é a trilha inbound
coberta no corpo da skill.

## Por que é outra classe de risco

| | Inbound | Disparo ativo |
|---|---|---|
| Assunto | limitado pela pergunta do lead | aberto — o modelo escolhe |
| Testemunha | o lead acabou de escrever, o contexto é fresco | ninguém; a mensagem chega pronta |
| Erro típico | resposta ruim a uma pergunta | preço inventado, prazo prometido, tom errado |
| Falha de volume | inexistente | número banido pelo provedor |
| Estado necessário | nenhum além da memória | contador de tentativa, opt-out, status de ciclo |

Conclusão prática: **o gerador pode ser LLM, o envio não pode depender só dele.**

## Peças obrigatórias

### 1. Validador determinístico entre gerador e envio

Nó de Code depois do gerador, antes do envio. Reprova e cai para template fixo quando o texto:

- foge do tamanho esperado (piso e teto — texto de 3 palavras e redação de 2 mil caracteres são
  ambos sintoma);
- cita preço, valor, mensalidade ou plano, quando a persona não fala preço;
- contém bloco de código ou marcação de sistema (` ``` `, `function`, `{{`, `$json`, `system:`);
- contém rastro interno: `[Used tools`, nome de sub-workflow/tool, protocolo interno de handoff;
- promete prazo ou garantia (`em até`, `garanto`, `com certeza`).

Grave uma flag no item quando o fallback foi acionado (`validado: false` + motivo). Sem essa flag
não há como medir, depois das primeiras dezenas de envios, se a escolha por texto gerado se sustenta
— e a discussão volta como opinião.

Mesmo princípio do guardrail de papel: **o que precisa ser garantido vira código, não instrução.**

### 2. Modelo

Não use o modelo mais barato em tarefa não supervisionada. É uma chamada por lead a cada dias — o
custo é irrelevante perto de uma mensagem errada no WhatsApp do cliente. Modelo pequeno já falhou de
forma intermitente em obedecer instrução silenciosa (chamar tool sem o usuário pedir, não vazar
rastro): a mesma fragilidade aparece aqui sem ninguém para corrigir.

### 3. Estado persistente, em banco

Mínimo por contato: `ultimo_contato_lead` (timestamp), `tentativas_enviadas` (int),
`status` (ciclo de vida), `optout` (bool). Índice parcial nos que ainda estão elegíveis.

- **Só mensagem recebida do contato carimba o relógio.** Envio do próprio agente jamais — senão a
  inatividade nunca zera de verdade e ninguém nunca recebe follow-up.
- **Resposta do contato zera o contador, não só o relógio.** Quem voltou a conversar recomeça do
  zero; manter a tentativa 2 engatilhada pune quem respondeu.
- **Teto de idade além da janela mínima.** Não basta "parado há mais de 24h": exija também "menos
  de N dias". Sem teto, a primeira execução depois do deploy cobra a base histórica inteira de uma
  vez.

Redis serve para debounce de rajada e anti-duplicado (`INCR chave` com TTL, atômico), **não** para
contador de cadência.

### 4. Anti-ban

O risco não é o volume por contato (3 mensagens em 7 dias é nada) — é a **rajada**: o agendado achar
dezenas de vencidos na mesma execução e disparar em sequência.

- teto de itens por execução; o resto espera a próxima janela;
- `Wait` aleatório entre envios dentro do loop (dezenas de segundos, não fixo — intervalo constante
  é assinatura de bot);
- janela horária **mais estreita** que a de aviso interno, e sem fim de semana quando o destino é
  cliente;
- **circuit breaker**: erros consecutivos do provedor abortam a execução e alertam. Insistir com
  número possivelmente bloqueado piora o bloqueio.

### 5. Opt-out

Detecção determinística por regex na mensagem recebida (`pare`, `não quero`, `descadastr`, `me
tira`), gravando `optout = true` — nunca delegada ao julgamento do modelo. Regex cobre o óbvio e não
substitui a saída explícita oferecida no texto: decida se a última tentativa da cadência carrega a
frase de opt-out, e trate como questão de base legal, não de copy.

### 6. A mensagem enviada entra no histórico

Grave o disparo na mesma tabela de histórico que o agente lê (`type: "ai"`). Sem isso o agente não
sabe que já cobrou e, quando o lead responde, retoma como se nada tivesse acontecido.

## Arquitetura que costuma servir

Sub-workflow agendado **isolado**, não enxertado no fluxo conversacional. O fluxo principal ganha só
dois nós em paralelo, com `onError: continueRegularOutput` — carimbo de contato e detecção de
opt-out nunca podem derrubar um atendimento.

```
Schedule (1h) → Janela? → busca elegíveis → filtra cadência → limita lote
  → loop: contexto → gera → VALIDA → envia → grava histórico → incrementa → wait aleatório
  → esgotou tentativas? → marca perdido + avisa o time
```

A tabela de cadência (tentativa → janela mínima → tom) mora em um Code node único e é o lugar de
ajustar a política depois. Não espalhe os intervalos por vários `If`.

## Leia a modelagem que o cliente já tem no CRM antes de propor cadência

Cadência é decisão comercial, e o cliente costuma já tê-la tomado — escrita nos **estágios do
pipeline**, não em documento. Antes de perguntar "quantas tentativas e em que intervalo?", liste os
estágios do pipeline que o fluxo de registro já usa:

```
GET {apiBase}/opportunities/pipelines?locationId=<LOCATION>   # HighLevel
```

Dois ganhos e um risco:

- **Ganho:** estágios de follow-up costumam já existir (`FUP1 · Não responde`, `FUP2 · Respondeu e
  sumiu`, `Lead Vencido`). Espelhar status vira `PUT /opportunities/{id}` trocando `pipelineStageId`
  — **sem custom field**, que é a pergunta que você ia fazer e a autorização que ia esperar.
- **Risco:** a modelagem do CRM classifica por **situação do lead** (onde ele parou), enquanto
  cadência por tempo conta **tentativas**. São eixos diferentes, e escolher um sem olhar o outro
  produz um CRM que ninguém consegue ler. Quando divergirem, leve as duas leituras ao usuário com as
  opções — alinhar ao CRM, mapear tentativa→estágio, ou desacoplar — em vez de decidir sozinho.
- Confirme que o padrão se repete em outro pipeline da mesma conta antes de tratá-lo como
  intencional; estágio isolado pode ser sobra de experimento.

Espelhar estágio nunca aborta o envio: a mensagem já saiu. Saída de erro própria com
`espelhado: false`, e contato sem oportunidade criada pula o passo em silêncio.

## Antes de ativar

- validador testado com casos que devem passar **e** casos que devem bloquear, sem falso positivo;
- primeira semana com teto reduzido de itens por execução;
- quem assina a copy (ou o prompt do gerador e os templates de fallback) está nomeado;
- destino do "esgotou a cadência" definido — lead que morre em silêncio sem ninguém saber é o mesmo
  buraco que o fluxo veio tapar.

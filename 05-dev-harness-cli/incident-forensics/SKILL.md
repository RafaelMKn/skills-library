---
name: incident-forensics
description: Reconstrói quando, como e o tamanho real de um incidente.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [incidente, diagnostico, n8n, producao, troubleshooting, PT-BR]
    category: devops
    related_skills: [n8n-flow-debugger, radar-n8n, agent-creator-hub]
---

# Incident Forensics Skill

Reconstruir a história de um incidente que já está rodando em produção: **quando começou de
verdade, qual a extensão real e o que causou**. É o passo anterior ao conserto — quem consertar
segue por `n8n-flow-debugger`. Somente leitura: nunca corrige fluxo, nunca muda estado de tarefa.

O valor desta skill está em contradizer o que o alerta diz. Card automático traz a hora da
*detecção* e o nome de *um* nó — quase nunca o início nem a extensão.

## When to Use

"Como isso aconteceu?", "desde quando está quebrado?", "o que é esse bug crítico?", triagem de
card aberto por detector automático, ou cruzamento de tarefa fechada contra fluxo que segue
falhando. Também após o `radar-n8n` apontar um fluxo sangrando sem tarefa aberta.

## Procedure

### 1. Procure o diagnóstico que já existe

Antes de investigar do zero, busque o sintoma (a mensagem de erro, o nome do fluxo, o ID da
credencial) em `tarefas/*.md` e `clientes/<cliente>/docs/`. Incidente de infraestrutura costuma
estar diagnosticado meses antes, com o caminho de conserto já escrito e a tarefa parada em
`estado: fazendo`. Refazer a análise queima tempo e produz uma segunda versão da mesma conclusão.

Se seu achado **contradiz** a nota antiga, diga isso explicitamente e proponha corrigir a nota —
não empilhe uma segunda análise por cima.

### 2. Date o início real, nunca pela hora do alerta

Pagine o histórico sem filtro de status e olhe a amostra mais antiga:

```bash
python3 skills/n8n-manager/scripts/n8n_api.py --instance <INST> \
    list-executions --workflow-id <ID> --limit 250
```

Se as N execuções forem **todas** `error` até o fim da retenção, o incidente é mais velho que a
janela: reporte um **piso** ("pelo menos X dias"), nunca um início. Confirme a retenção real —
instância movimentada guarda poucos dias.

**Use metadado que carimba a mudança.** Quando o objeto quebrado tem `createdAt`/`updatedAt` na
API, a fronteira entre "funciona" e "não funciona" nesse eixo temporal data o evento com precisão
que o log de execução já perdeu. Delimite a janela com as duas amostras mais próximas (última que
funciona × primeira que não) e **declare que é inferência**, a menos que exista log do deploy.

### 3. Meça a extensão antes de aceitar o escopo do card

O card nomeia um nó; a causa costuma atingir mais. Agregue os nós que falharam nas últimas ~8
execuções com erro — se aparecerem nós diferentes com a mesma mensagem, o escopo é maior que o
card. Depois varra a instância por outros fluxos com a mesma mensagem.

**O que ainda funciona ao lado do quebrado é evidência, não ruído.** Fluxo verde na mesma
instância prova que o problema atinge um subconjunto, e a diferença entre os dois grupos é a
assinatura da causa. Levante o conjunto "prejudicado" e o "ileso" antes de teorizar.

Conte também o que **não executou**: erro só aparece quando o fluxo roda. Instância com a maioria
dos fluxos ociosos devolve o incidente fatiado, um fluxo por vez, conforme cada um recebe
tráfego. O número de erros é sempre um piso do dano potencial.

### 3.1 Traduza o erro do provedor em dano de negócio

Um `error` no log pode ser **entrega de cliente que não aconteceu**, e isso muda a urgência do
relatório. Antes de reportar "N erros/dia", leia o `runData` e responda o que se perdeu: lead não
notificado, mensagem não enviada, linha não gravada. "Fluxo com 4 erros" e "4 leads de cliente
perdidos em silêncio" descrevem o mesmo dado e produzem decisões diferentes.

**Erro de provedor pode ser dado faltando, não parâmetro errado.** Um `400 Bad Request` genérico
("please check your parameters") costuma vir de campo vazio montado a partir de coluna `NULL` no
banco — o nó que falha é o mensageiro, não o culpado. Leia o corpo da resposta do provedor em
`messages` (ele nomeia o campo recusado) e o item que **entrou** no nó, vindo do nó anterior. Card
aberto por detector automático aponta o nó do estouro; a causa costuma estar uma ou duas casas
atrás, no `SELECT` que devolveu vazio.

### 3.2 Cheque se o conserto realimenta o detector

Quando a instância tem fluxo de alerta (`errorTrigger`) que abre card a partir de N erros em uma
janela, uma correção que troca falha silenciosa por `Stop and Error` **continua contando como
erro** — o card reabre enquanto a causa de dado persistir. Leia o `jsCode` do fluxo de alerta para
saber limiar, janela e cooldown antes de prometer que o ruído acabou, e diga ao usuário que o card
pode voltar. Fluxo de alerta que ignora `mode: manual` permite teste sem acordar ninguém; confirme
no código em vez de supor.

### 4. Separe sintomas que parecem a mesma coisa

Duas causas distintas na mesma instância produzem relatórios que se confundem. Antes de colapsar
uma na outra, confira se as datas e os metadados batem. Para o caso de credenciais n8n, ver
`references/credenciais-n8n.md`. Para armadilhas de leitura/escrita via API REST (filtro de
`settings` no PUT, onde ficam os dados de cada nó, ordem dos ramos do `If`), ver
`references/api-rest-n8n.md`.

### 5. Atribua a autoria de mensagens pelo caminho executado

Quando a reclamação disser que "a IA respondeu", não atribua autoria só porque a mensagem apareceu
no webhook do fluxo. Busque a execução do horário exato e leia os dados completos.

**Converta o horário antes de procurar.** O usuário relata em hora local (BRT, UTC-3) e o
`startedAt` da API vem em UTC — procurar pelo horário dito devolve a janela errada ou nada. Some 3h
antes de casar o `startedAt` (19:11 local = 22:11Z), e confirme pelo campo de horário que o próprio
fluxo carimba no prompt, quando existir.

Saída de `list-workflows` e de `get-execution --include-data` chega a centenas de KB e a vários MB
(mídia em base64 infla o dump). Redirecione para arquivo e navegue por busca, nunca despeje no
contexto:

```bash
python3 skills/n8n-manager/scripts/n8n_api.py --instance <INST> \
    get-execution <ID> --include-data > /tmp/exec_<ID>.json
```

**Busque no dump o token exato da anomalia relatada** — o nome errado, o valor estranho, o trecho da
mensagem. Uma única busca cai de uma vez no output do nó que originou o dado, no system prompt
montado e no texto enviado; isso resolve a autoria mais rápido que ler o `runData` nó a nó. Só então
leia as vizinhanças em faixas estreitas de linha.

Para achar o ID de um fluxo dentro de um `list-workflows` grande, busque pelo nome com o prefixo do
cliente e leia as ~10 linhas acima do acerto: o campo `id` vem antes do `name` no objeto.

Use esta ordem de prova:

1. confira `fromMe`, `source`, texto e timestamp no payload do provedor;
2. leia a sequência de nós em `data.resultData.runData`;
3. só atribua à IA se a execução passou pelo nó do agente **e** pelo nó que enviou a resposta;
4. se a execução apenas recebeu um evento `fromMe` e seguiu para pausa/deativação da IA, ela
   registrou uma mensagem já enviada — não a gerou;
5. procure a execução imediatamente anterior do mesmo contato e de workflows auxiliares no mesmo
   intervalo, porque IDs são globais na instância e a geração pode estar em outro fluxo.

`source: web` ou `source: android` é evidência de canal, mas não deve ficar sozinho: confirme com o
caminho de nós. Para correlacionar execuções sem expor telefone, compare internamente o identificador
do contato ou imprima apenas um hash curto dele. Se a entrada foi áudio sem transcrição persistida,
reporte que o conteúdo da pergunta não pode ser confirmado — nunca reconstrua as palavras pelo teor
da resposta.

**"IA seguiu o prompt corretamente" não fecha o caso — pode ter agido certo sobre dado errado.**
Quando a execução passou pelo agente e ele só obedeceu à instrução do próprio system prompt (ex.:
"se paciente já cadastrado, use o nome sem perguntar"), suba mais um node: o dado que ele recebeu
pode vir de uma consulta amontante que devolveu **múltiplos resultados** (telefone compartilhado
por dois cadastros, CPF duplicado) e um `Filter`/`Item Lists` que pega o primeiro item da lista sem
desambiguar por nome/similaridade. Confira `runData` do node de busca: se ele devolveu mais de um
item, a causa raiz é a falta de desambiguação, não a IA.

### 6. Verifique a contenção antes de declarar perda de dado

Se alguém instalou fila ou buffer durante o incidente, leia o `runData` de uma execução com erro
recente: o nó de enfileiramento tem que aparecer na lista de nós executados, **antes** do nó que
falhou. Só então afirme que nada se perdeu — e lembre que backlog acumulando é entrega pendente
(o drenador), não problema resolvido.

## Como reportar

Em PT-BR, na ordem: **o erro exato** (mensagem literal, em bloco de código) → **causa raiz em uma
frase** → **extensão medida** → **como/quando aconteceu** → **conserto por ordem de impacto**.

- Distinga sempre **medido** de **inferido**. "É inferência a partir de 10 amostras, não prova
  documental" vale mais que uma afirmação limpa e errada.
- Corrija diagnósticos anteriores explicitamente quando o dado novo os contradiz.
- Encerre com o próximo passo real, não com pergunta de cortesia.

### Ao registrar a entrega numa tarefa

Quando o usuário pedir para descrever o trabalho no card, use esta ordem — é o padrão das tarefas
de dev do workspace:

1. **Causa raiz** com a evidência (execução, cliente, valor do campo) em tabela. Se o card culpava
   o nó errado, corrija isso na primeira linha.
2. **O que foi feito** — nós, condições, `typeVersion`, link do workflow.
3. **Como testar** — e por que o teste foi do jeito que foi (ex.: replay em vez de disparo, porque
   o fluxo envia mensagem real). Aponte o script versionado.
4. **⏳ O que NÃO foi resolvido** — seção obrigatória quando sobrou pendência. Inclua se o card pode
   reabrir e por quê. Deixar isso escrito evita que outro agente redescubra amanhã.
5. **Achados colaterais**, separados do pedido principal — nunca corrigidos de carona.

**Não mova para status de conclusão quando a causa persiste.** Correção entregue com o dado ainda
errado é exatamente o padrão "tarefa fechada, fluxo quebrado" que esta skill existe para achar.
Deixe o status e explique a decisão; mudar estado de entrega é do usuário.

**Segredo achado no caminho vira achado colateral, nunca conserto silencioso.** Credencial em
campo de texto de nó (header `apikey`, token em Set) vaza em todo export. Reporte a existência e o
nó, **sem transcrever o valor**, e ofereça task própria para migrar para o sistema de credenciais.

## Pitfalls

- **`--instance` do `n8n_api.py` vem ANTES do subcomando**, inclusive antes de `--help` — sem ele
  o script devolve erro em vez da ajuda. São quatro instâncias; confirme o alvo pelo `README.md`
  do cliente, nunca pelo nome do fluxo.
- **Fluxo com nome `TESTE` ou `My workflow N` pode ser produção.** Confira se tem trigger ativo
  recebendo tráfego externo antes de tratar como descartável. Durante incidente esse nome custa
  minutos.
- **Detector automático gera um card por dia, não um card por problema.** Antes de triar, agrupe
  os cards abertos por (fluxo + nó + mensagem): vários cards com prefixo de bug e datas diferentes
  costumam ser o mesmo incidente reaberto, e alguns estarão arquivados sem correção. Relate o
  conjunto e aponte qual card deve concentrar o trabalho — contar cards como incidentes distintos
  infla o problema.
- **Status com nome de conclusão não prova conclusão.** Teste o tipo do status (`type == "closed"`)
  ou a presença de `date_closed`, e confronte com o estado atual do fluxo: tarefa `resolvido` ou
  `arquivado` cujo fluxo segue falhando é o achado mais valioso da triagem. O inverso também vale —
  antes de repetir um caso conhecido, confirme que ele ainda está quebrado; fluxo que voltou
  sozinho transforma o alerta em ruído.
- **A API REST do n8n expõe mais que o CLI wrapper.** `GET /api/v1/credentials` e
  `/api/v1/data-tables` respondem com a `X-N8N-API-KEY` do `.env` (chaves `N8N_<INST>_API_URL` e
  `N8N_<INST>_API_KEY`) mesmo sem subcomando no `n8n_api.py`. Um 403 em `/api/v1/projects` é
  escopo do token, não instância quebrada.
- **Retenção curta mascara o tamanho.** Nunca apresente contagem truncada como total.
- **Nunca imprima valores do `.env`** no relatório nem em mensagem de erro — leia as chaves,
  reporte apenas se estão presentes.

## Validar sem efeito colateral (quando o conserto sai desta skill)

Esta skill é read-only, mas quem consertar (via `n8n-flow-debugger`) herda o problema de provar a
correção. A prova padrão é execução `success` posterior ao patch. Quando ela não está disponível:

**O caminho feliz tem efeito colateral real.** Não dispare o webhook nem `n8n_test_workflow` em
fluxo ativo para "ver se funciona" — isso entrega mensagem/registro de verdade ao cliente. Valide
por replay offline com `scripts/replay-code-node.js` (casos a partir de `templates/caso-replay.json`),
que roda o `jsCode` vivo do nó contra payloads reais de execuções passadas. Inclua sempre um caso
que **antes passava**: provar que o caminho feliz não mudou vale tanto quanto provar que o quebrado
agora para.

**Não houve execução nova.** Fluxo disparado por evento pode ficar horas sem rodar. Diga
explicitamente "replay passou em N casos, mas não houve execução real após o patch" — replay é a
sua leitura do operador, não o runtime do n8n, e apresentá-lo como confirmação é afirmar sem prova.

Antes de qualquer escrita em fluxo ativo, exporte o estado atual para
`scratch/archive/<WF>--<slug>--<AAAA-MM-DD>-ANTES.json`: correção sem export prévio não tem rollback.

## Verification

- A datação está sustentada se você nomeia as duas amostras que delimitam a janela, e diz qual é
  medição e qual é inferência.
- A extensão está medida se você listou o conjunto prejudicado **e** o ileso, não só o nó do card.
- O dano foi traduzido em negócio (o que deixou de ser entregue), não só em contagem de erro.
- Nenhuma tarefa, fluxo ou credencial foi alterada — esta skill é somente leitura.

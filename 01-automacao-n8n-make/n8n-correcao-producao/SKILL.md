---
name: n8n-correcao-producao
description: Use when changing, auditing, or extending an n8n flow in production.
version: 1.1.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [n8n, producao, api-rest, debugging, PT-BR]
    category: automation
    related_skills: [using-n8n-mcp-skills, n8n-flow-debugger, n8n-manager, radar-n8n]
---

# Alterar e auditar fluxo n8n rumo à produção

Fluxo quebrado em produção é cliente parado; fluxo novo sem homologação é o mesmo incidente adiado.
Esta skill cobre o caminho completo: diagnosticar a partir da execução real, aplicar a correção
mínima com backup, provar que gravou, auditar prontidão antes da ativação — e separar o que o agente
resolve do que só o dono da conta resolve.

Responda em **PT-BR**. Regras do workspace: `AGENTS.md` na raiz do workspace.
Protocolo n8n geral: `using-n8n-mcp-skills`. Comandos do CLI: `n8n-manager`.

## When to Use

- Corrigir fluxo que falhou em produção, ou alterar fluxo que já roda para cliente.
- Responder "o fluxo já faz X?" / "tem follow-up, retry, alerta?" — ver passo 0.
- Auditar prontidão antes de ativar, ou decidir se uma feature nova pode ser construída agora.
- Homologar agente de IA sem tocar em produção.
- Desenhar fluxo em que o agente **manda mensagem primeiro** — ver
  `references/disparo-ativo-whatsapp.md`.

Suporte: `scripts/anatomia_fluxo.py` (estrutura de fluxo grande sem inundar o contexto) ·
`references/api-rest-escrita.md` (escrita via REST) ·
`references/disparo-ativo-whatsapp.md` (disparo ativo).

Quando o problema não é o fluxo e sim a **instância** — container, upgrade de versão, DNS, TLS,
proxy reverso, VPS — a skill é `infra-vps-producao`. Nenhuma edição de workflow conserta instância,
e o inverso também vale: não reinstale nem reinicie serviço para resolver bug de JSON de fluxo.

## Sempre, antes de tocar em fluxo ativo

1. **Confirme a instância.** Identifique a instância correta (ex.: `PROD`, `CRM`, `BACKOFFICE`) a partir da documentação do workspace ou cliente.
2. **Backup do estado atual** para `scratch/archive/<ID>--<slug>--<AAAA-MM-DD>-ANTES.json`. Fluxo
   ativo sem export anterior não tem rollback.
3. **Correção mínima.** Mexa no que causa a falha e nada mais. Refatorar de carona num hotfix
   transforma um diff auditável em suspeito.
4. **Dado de cliente não é seu para consertar.** Corrigir o fluxo é o trabalho; alterar linha de
   banco, planilha ou cadastro do cliente pede aval explícito, mesmo quando é óbvio qual valor
   falta.
5. **Procure o mecanismo que já existe antes de adicionar nó.** Pedido de "põe um `If` depois do
   webhook para ignorar o número X" quase sempre já tem endereço no fluxo: flag em banco, coluna de
   status, tabela de configuração. Hardcode no caminho quente fica invisível para quem mantém, exige
   republicar o fluxo a cada mudança e pesa em todo atendimento para resolver um caso. Levante o
   mecanismo, mostre a alternativa com o motivo e deixe o usuário escolher — ele costuma preferir a
   mudança de dado.
6. **Procure o padrão que já roda na conta antes de desenhar do zero.** Antes de propor construção
   nova, varra as **outras instâncias do mesmo cliente** (`list-workflows`) por um fluxo que já
   resolve o problema para outro produto — vigia agendado, notificador de grupo, anti-duplicado.
   Padrão em produção traz junto os parâmetros já calibrados (janela, TTL, teto) e as travas que
   alguém já pagou para descobrir. Cite o ID do fluxo doador na proposta e explique **onde o novo
   caso difere**, porque copiar sem a diferença é o que produz cópia quebrada.

## Procedimento

### 0. "O fluxo já faz X?" — responder pelo nó, nunca pelo documento

Pergunta de capacidade (*tem follow-up? tem retry? avisa o time?*) se responde no JSON do fluxo
live, não no `README.md`, no inventário nem no snapshot em `fluxos/`. Documento de projeto é
**hipótese datada**; a instância é a verdade.

O erro caro não é o documento omisso, é o documento que afirma a capacidade errada. Uma cadeia
rotulada "follow-up ✅" pode ser handoff: o que decide não é o nome dos nós nem o LLM no meio, é
**para onde o nó de saída aponta e quem dispara**. Destino hardcoded num número interno = aviso a
humano. Gatilho na saída de encerramento do roteador = handoff, não cadência. Sempre leia o campo
de destino (`remoteJid`, `chatId`, `to`) e o nó que dispara, não o rótulo.

Achou divergência: **corrija o documento na mesma entrega**, editando a linha que enganou e dizendo
o que a cadeia faz de fato. Responder certo no chat e deixar o `.md` errado no repositório garante
que a próxima sessão caia na mesma armadilha.

Fluxo de 100+ nós não cabe no contexto. Exporte para `scratch/` e analise a estrutura por script:

```bash
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> \
  get-workflow <ID> > scratch/<slug>.json
python3 skills/n8n-correcao-producao/scripts/anatomia_fluxo.py \
  scratch/<slug>.json                      # triggers, componentes, órfãos
  ... --grep follow lembrete reengaj        # nós cujo JSON casa com algum termo
  ... --upstream "Enviar texto1"            # quem alimenta o nó (acha o gatilho real)
  ... --node "Enviar texto1"                # params + vizinhos
```

O grafo de componentes é o que expõe cadeia agendada solta, sub-grafo sem trigger e nó órfão
perigoso — um `Schedule Trigger` num canto pode alimentar RAG e não ter nada a ver com a
funcionalidade perguntada.

### 1. Diagnosticar a partir da execução, nunca do card

Card aberto por detector de erro nomeia **o nó que estourou e a mensagem HTTP** — quase nunca a
causa. Trate o card como coordenada, não como diagnóstico.

```bash
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> \
  list-executions --workflow-id <ID> --limit 20
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> \
  get-execution <EXEC_ID> --include-data > /tmp/ex.json
```

A resposta com `--include-data` é grande: filtre em Python por palavra-chave (`"error"`, o nome do
campo suspeito) e imprima a vizinhança, em vez de despejar o JSON no contexto.

Leia o **payload de saída de cada nó anterior**, não só o erro. O padrão mais comum de falso
diagnóstico: consulta a banco devolve `NULL` num campo, um Code node monta string vazia, e o nó de
rede lá na frente devolve `400 Bad request`. O nó de rede está certo; o dado a montante é o bug.

Um `400` que vem com corpo da API (`exists: false`, `number: ""`) é ouro: ele diz exatamente qual
campo chegou vazio.

### 2. Classificar a causa raiz em uma frase

Dado inesperado · configuração · credencial · rate limit · expressão · Code node · rede/DNS.
A classificação decide se a correção é sua ou não — ver a fronteira abaixo.

### 3. Patch como script, não como edição manual do JSON

Escreva `scratch/patch_<slug>.py` que lê o export, altera e grava o payload. O script documenta a
intenção, é reexecutável depois de um `get-workflow` novo, e você faz ele **abortar se o nó que
insere já existir** — rodar duas vezes não pode duplicar nó.

Para trocar somente um prompt longo, mantenha o arquivo canônico com delimitadores explícitos e
extraia apenas o corpo destinado ao `systemMessage`; cabeçalho de versão, notas editoriais e
checklists não pertencem ao contexto do modelo. Antes de escrever, faça o script abortar se o prompt
live não contiver a versão esperada — isso evita sobrescrever uma mudança concorrente. Depois do
PUT, releia e prove que:

- o prompt live é byte a byte igual ao corpo canônico;
- `active` não mudou;
- `connections` é idêntico;
- contagem de nós é idêntica;
- neutralizando apenas o campo alterado, o restante de `nodes` é idêntico.

Um `200` com o prompt certo mas qualquer outro diff é atualização não controlada, não sucesso.

Receita completa da escrita via REST, com a lista branca de `settings` e as armadilhas de
`typeVersion`: **`references/api-rest-escrita.md`**. Leia antes do primeiro `update-workflow`.

### 4. Falha silenciosa vira falha alta

Quando a causa é dado ausente, a correção não é preencher o dado — é **fazer o fluxo gritar**.
Insira um guard (`If` + `Stop and Error`) com mensagem que nomeie o registro culpado, o cliente e o
item perdido. Sem isso o fluxo volta a "funcionar" e continua descartando item em silêncio.

Mensagem de erro útil cita: qual identificador está incompleto, qual campo falta, e o que se perdeu
naquela execução. `"Erro ao enviar"` não serve para ninguém.

Se o fluxo tem `settings.errorWorkflow`, o guard passa a alimentar o branch de erro com contexto em
vez de um código HTTP cru — mais uma razão para preservar essa chave no update.

### 5. Verificar na instância

`update-workflow` devolver `200` não prova nada. Releia e confira contagem de nós, `active` e o mapa
de conexões. Detalhe em `references/api-rest-escrita.md`.

Correção só está provada quando existe execução `success` **posterior** ao horário do patch. Até
lá, o relato é "aplicado, aguardando execução", não "resolvido". Histórico vazio significa
**integração não comprovada** — não significa que falhou nem que funciona; retenção pode ter apagado
execuções antigas.

### 6. Auditar prontidão além do nó alterado

Mudança de prompt que cria uma nova decisão de negócio exige conferir o contrato inteiro a jusante.
Se o agente agora classifica produto, perfil ou prioridade, inspecione também o extractor
determinístico, o Output Parser, os inputs do sub-workflow, o schema do banco e o payload do CRM.
Prompt novo com schema antigo produz uma conversa correta e um registro incapaz de guardar a decisão.

Antes de declarar um fluxo apto para produção, mapeie nesta ordem:

1. **Entrada e cutover:** webhook live, fluxo antigo ainda ativo, destino real do provedor e plano de
   rollback. Ativar um webhook novo não redireciona o sistema que ainda chama o path antigo.
2. **Contratos de dados:** campos coletados → extractor → banco → CRM; marque como ausente todo campo
   que só existe em texto corrido quando o downstream precisa filtrar ou rotear por ele.
3. **Dependências externas:** migration, credencial, calendário, pipeline, estágios e custom fields.
   Valor preenchido no nó prova configuração, não existência nem permissão no serviço. Confirme
   migration no schema real, não no estado de uma tarefa; quando ela estiver aplicada, reclassifique
   imediatamente os passos técnicos que ela destravou e atualize a documentação que ainda a chama de
   bloqueio. Um bloqueio resolvido, deixado como pendente no repositório, faz a próxima sessão parar
   antes do necessário.
4. **Efeitos auxiliares:** confirmação, lembrete, link de reunião, follow-up e alerta interno.
   Default de API e comentário em documento não contam como prova; exija execução e efeito lido de
   volta no sistema alvo.
5. **Resiliência:** retries, error outputs completos, Error Workflow, retenção de execução e falhas
   que usam `continueRegularOutput` — estas podem preservar a ação principal e ocultar um alerta
   perdido.
6. **Homologação:** casos felizes, ambíguos, descartes, conflito de agenda, reagendamento e falhas de
   token/rede/banco. Não dispare writes, mensagens ou compromissos sem contato, número e agenda de
   teste autorizados.

Separe o relatório em **observado**, **configurado mas não comprovado** e **ausente**. Termine com
critérios verificáveis de pronto e veredito `apto` ou `bloqueado`; não transforme lista de nós em
prova de produção.

## Fronteira: o que você corrige e o que é do usuário

Quando o pedido é "o que dá para resolver agora?", classifique por **acesso**, não por dificuldade.

**Você resolve:** qualquer coisa dentro do JSON do fluxo — parâmetro de nó, expressão, Code node,
rewire, guard, branch de erro. Também diagnóstico completo, proposta de escopo, e fechar duplicata
de card.

**Só o usuário resolve — reporte como bloqueio, não tente:**

- **Credencial que exige segredo** (senha de banco, API key que não está em `.env`): recriar pede o
  valor, e ele não está no seu alcance.
- **Credencial OAuth** (Google Calendar, Sheets, Drive): exige consentimento em navegador com a
  conta do cliente. Não há caminho de API.
- **`N8N_ENCRYPTION_KEY` divergente** (`Credentials could not be decrypted`): é estado de
  servidor/deploy, não de fluxo. Nenhuma edição de workflow conserta.
- **Dado em sistema de terceiro**: cabeçalho de planilha, cadastro no CRM, linha de banco. A
  credencial que o fluxo usa para esse sistema vive **dentro do n8n** e a API nunca devolve o valor
  dela — acesso à instância não é acesso ao banco. Sobram dois caminhos: pedir a credencial ao
  usuário, ou criar um workflow temporário na instância que faça a escrita com a credencial já
  cadastrada. O segundo cria e ativa fluxo numa instância de produção por alguns minutos: ofereça
  como escolha explícita, nunca execute por conta própria.
- **Decisão de negócio ou de escopo**: dependência de terceiro fica explícita, com o nome de quem
  decide e qual pergunta está aberta.

Quando um bloqueio é de 10 segundos para o usuário e trava a sua parte, diga isso — e diga o que
você faz assim que ele destravar.

**Decisão tomada contra a sua recomendação vira parágrafo no documento, não desabafo no chat.**
Quando o usuário escolhe a opção mais arriscada, registre no próprio artefato entregue: a escolha,
a objeção em uma frase com o mecanismo do risco, e a **mitigação obrigatória** que passa a ser
condição de produção. Objeção que só existe na conversa some na próxima sessão; escrita no `.md`,
ela obriga quem implementa. Aceite a decisão e implemente a mitigação — não reabra o debate.

## Homologar agente de IA sem tocar em produção

Auditoria estática não prova comportamento de agente. Configuração correta convive com agente que
nunca chama a ferramenta, e o sintoma chega como "o prompt está ruim". Antes de declarar um agente
apto, **rode conversa de verdade** contra uma bancada isolada.

**Monte a bancada por script, a partir do fluxo live**, não à mão:

1. copie o `systemMessage` do nó de agente do fluxo principal — e faça o script abortar se a versão
   não for a esperada, senão você homologa o prompt antigo;
2. troque cada `toolWorkflow` por um **Code Tool mock** de mesmo nome e mesmo formato de retorno;
3. corte a trilha que escreve (CRM, banco, mensageria) e troque memória persistente por memória
   local com chave de sessão do chat;
4. deixe **um** modelo no slot `ai_languageModel` — um segundo link faz o teste variar sem motivo;
5. termine com `assert` de que nenhum nó de tipo que toca recurso real sobrou, de que não há nó
   duplicado, e de que **cada tool está ligada ao agente**.

O Chat Trigger precisa de `public: true` para aceitar POST externo; dispare com
`POST /webhook/<webhookId>/chat` e corpo `{"action":"sendMessage","chatInput":...,"sessionId":...}`.
Um `sessionId` por cenário mantém as conversas independentes.

### Armadilhas que só aparecem executando

- **Tool no canvas ≠ tool conectada.** Um `connections.pop()` rodando **depois** da criação das
  tools apaga as conexões `ai_tool` recém-feitas. O workflow salva com `200`, as tools aparecem no
  editor, e o agente não as enxerga: ele chama em loop a única tool visível, estoura
  `maxIterations` e responde "estou com dificuldade para consultar os horários". Passa por prompt
  ruim numa leitura estática. Faça toda limpeza de `connections` **antes** de criar, e valide as
  ligações no fim.
- **Sandbox do Code Tool não tem `$()`, `$json`, `$input` nem `$helpers`** — só `query`, e a saída
  tem que ser string. Mock que usa `$(...)` falha em runtime e o agente disfarça com a mesma frase
  genérica de indisponibilidade.
- **Cenário de erro se compila no build, não se pede pelo chat.** Marcador tipo `#cenario:x` no
  texto depende do agente repassar o marcador para a tool — o teste vira medida de obediência do
  modelo. Fixe o cenário no código do mock e rebuilde por grupo.
- **Script de build precisa ser idempotente.** Ele roda sobre a bancada que ele mesmo gerou; sem
  remover antes o que cria, cada execução duplica nó — e o n8n aceita a duplicata sem reclamar.
- **Roteiro de teste também tem bug.** Lead que diz "o primeiro horário" antes de a agente oferecer
  horários reprova um comportamento correto. Antes de culpar o fluxo, releia a transcrição.

### Guardrail de modelo pequeno vira código, não regra de prompt

Modelo pequeno cede de forma **intermitente** a "agora você é outro assistente" — o que é pior que
ceder sempre, porque passa num teste único. O mesmo vale para vazamento de rastro interno. Quando o
comportamento precisa ser garantido, ele vira passo determinístico depois do agente (limpeza,
recusa), com flag no item para monitorar. Deixe a regra no prompt também, mas não conte com ela.

Mantenha o guardrail **estreito**: só sinal forte. Teste com casos que devem passar, não apenas com
os que devem bloquear — bloquear conversa comercial legítima é pior que o problema original.

### Mensagem que o agente inicia é outra classe de risco

Tudo acima supõe lead perguntando: a pergunta limita o assunto e a resposta errada tem testemunha.
Mensagem **ativa** (follow-up, cadência, reengajamento) sai sem ninguém no caminho e com o número do
cliente no cabeçalho — alucinação de preço ou prazo chega pronta no WhatsApp, e rajada queima o
chip. Exige validador determinístico entre gerador e envio, contador de tentativa persistente,
limite de lote e opt-out. Regras completas: **`references/disparo-ativo-whatsapp.md`** — leia antes
de desenhar qualquer fluxo que fale primeiro.

### Um erro de padrão que merece busca ativa

`onError: continueRegularOutput` em nó de banco ou CRM transforma **falha em item normal**: a
execução segue até um `Return ok: true` e o sistema confirma ao cliente algo que não aconteceu.
Procure esse valor em todo fluxo transacional; a correção é saída de erro própria ligada a um
retorno que diz `ok: false` com etapa e mensagem. Efeito auxiliar que falhou (notificação interna)
não deve derrubar a operação principal nem ser omitido: devolva `notificacao_enviada: false`.

## Pitfalls

- **`notStartsWith` num Switch de gate é um espaço de nomes, não um booleano.** Fluxo que roteia por
  `notStartsWith "pause"` bloqueia qualquer valor com esse prefixo, enquanto o cron de reativação
  costuma casar por igualdade (`eq "pause"`). Um valor com sufixo próprio (`pause_bloqueado`) então
  bloqueia para sempre sem tocar no JSON do fluxo — confirme o operador dos dois lados antes de
  prometer que o bloqueio é permanente.
- **Não configure nó de memória.** Sem `get_node` do MCP, copie `typeVersion` e forma dos
  parâmetros de outro fluxo **da mesma instância** que já roda. Par de nome/valor inventado valida
  como string e não faz nada em runtime.
- **Tipo de nó não revela topologia de banco.** Ver nó Supabase numa tabela e nó Postgres em outra
  não prova que são bancos diferentes: Supabase **é** Postgres, e a credencial "Postgres" costuma ser
  conexão SQL direta ao mesmo banco que a credencial "Supabase" acessa via PostgREST. Concluir "são
  dois bancos" a partir do tipo de nó leva a desenhar consulta separada onde cabia `join`, e a
  espalhar migration por arquivos que deveriam ser um. A verdade está no cabeçalho das migrations do
  projeto (`sql/`), não no canvas — e a confirmação final é ver as duas tabelas juntas no SQL Editor.
- **Antes de criar artefato para o cliente, liste o que o projeto já tem.** `sql/`, `docs/` e
  `scripts/` do projeto costumam guardar um arquivo consolidado feito para aprovação; criar um
  segundo produz versões concorrentes do mesmo pedido e o cliente recebe dois SQL parecidos sem saber
  qual vale. Estenda o existente e rebaixe os parciais a histórico, com um aviso no topo dizendo qual
  arquivo é o canônico.
- **Ação em lote pede contagem conferida antes.** Pedido de "desarquiva as 3" pode encontrar 2
  arquivadas e 2 já abertas. Levante o estado real, execute só o que precisa e **reporte a
  divergência** em vez de forçar o número pedido.
- **Rótulo de status não é tipo de status.** Em ferramenta de tarefa, um status chamado `arquivado`
  pode ter `type: open` — a tarefa continua aberta para a API. Teste o tipo (`closed`/`done`) ou a
  presença de data de fechamento, nunca o nome.
- **Tarefa fechada cujo fluxo ainda quebra é o achado mais valioso.** Antes de acreditar num
  `resolvido`, olhe as execuções das últimas 24h. O inverso também vale: confirme que o fluxo voltou
  antes de repetir que um caso conhecido segue quebrado.
- **Detector de erro que reabre card diário gera duplicata, não trabalho.** Mesmo fluxo, mesmo nó,
  mesma causa em dois cards = funda e mantenha um.
- **Coleta fora da rotina Radar usa `--state-dir /tmp/...`** para não contaminar o estado do cron
  em `~/.hermes/radar-n8n/`.
- **Feature nova sobre base que nunca rodou é dívida com juros.** Antes de construir sobre um fluxo
  reescrito, exija **uma execução `success` real** dele e o cutover feito. Fluxo aprovado em bancada
  e com zero execução em produção ainda é hipótese; empilhar a peça de maior risco — a que dispara
  sozinha — sobre hipótese multiplica a superfície de falha em vez de somar. Especifique agora,
  construa depois: spec escrita não apodrece, código sobre base errada sim.
- **Contador de tentativa não vive em Redis.** Chave volátil com TTL é ótima para debounce e
  anti-duplicado, péssima para estado que decide se uma pessoa recebe a terceira mensagem. Expiração
  silenciosa reinicia a cadência do zero. Estado de ciclo de vida do lead vai para coluna de banco —
  e isso costuma trazer junto uma DDL que depende de autorização do cliente: levante essa dependência
  na spec, não na hora de ativar.
- **`scratch/` é descartável.** Apague o patch e os exports ao terminar; promova só o backup
  `-ANTES` para `scratch/archive/`.

## Formato do relato

Curto, e nessa ordem: **causa raiz em uma frase** (corrigindo o diagnóstico do card se ele estava
errado) · **o que mudou** (nós, rewire, IDs) · **o que foi verificado** (com o dado que prova) ·
**o que ficou pendente e de quem depende**.

Não narre a investigação nem as chamadas de ferramenta que o usuário já viu. Tropeço de API que
custou tempo vale uma linha no fim, porque ele volta na próxima vez.

Nunca reporte "resolvido" sem execução `success` posterior à correção. "Aplicado e verificado na
instância, aguardando próxima execução" é honesto e igualmente útil.

**Pendência se agrupa por dono, não por assunto.** No fim do relato, separe o que trava em *sua*
decisão, o que depende de terceiro nomeado e o que já foi resolvido na sessão (riscado). Lista
única de seis itens faz o usuário reler tudo para achar as duas que são dele.

### Artefato que vai para aprovação do cliente

Quando o usuário pede algo para repassar a um decisor ("me passa o SQL que eu mando pro chefe"), o
leitor final não conhece o projeto e vai avaliar **risco**, não técnica. O artefato é um arquivo só,
idempotente, e carrega no próprio corpo:

- **onde rodar** e em qual banco/ambiente, na primeira linha;
- **declaração explícita de segurança**: o que NÃO faz (não apaga, não altera dado existente, pode
  rodar duas vezes);
- um bloco por finalidade, cada um precedido do **porquê em linguagem de negócio** — "hoje o lead que
  para de responder é perdido em silêncio" vale mais que o nome da coluna;
- **consulta de conferência com a contagem esperada**, para o aprovador saber que deu certo;
- **rollback comentado** no fim.

No chat, entregue o arquivo e um resumo de três a quatro linhas que o usuário possa copiar como
mensagem. E peça o retorno da conferência de volta: schema que você inferiu de nó e de arquivo
continua inferido até alguém colar a saída real.

## Verification

- Backup `-ANTES` existe em `scratch/archive/`.
- `get-workflow` posterior confirma nós novos, `active` e o mapa de `connections`.
- `settings.errorWorkflow` preservado, se o fluxo tinha um.
- Nenhum segredo em campo de texto de nó.
- Bloqueios que não são seus estão nomeados com o dono e a pergunta aberta.

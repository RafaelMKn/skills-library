---
name: composio-apps
description: "Use when a task needs a real app account. Composio CLI."
version: 1.0.0
author: Agent Skills Community
license: MIT
metadata:
  hermes:
    tags: [composio, gmail, calendar, github, notion, oauth, apps]
    related_skills: [composio, google-workspace, github]
---

# Composio — acesso a apps

O Composio é o caminho padrão para o agente tocar em contas reais de apps do usuário
(Gmail, Google Calendar, GitHub, Notion, Outlook, Slack, Linear...). Antes de escrever
um script com API/OAuth próprio para qualquer um desses, use a CLI do Composio.

## When to Use

**Regra padrão: o Composio é a base para TUDO que não puder ser feito nativamente.**
Antes de responder "não tenho acesso a esse serviço", rode
`composio dev toolkits search <nome>` — são ~1000 toolkits. Só depois de a busca vir vazia
é que a resposta "não dá" é honesta.

- Pediu YouTube, Gmail, Drive, Slack, Notion, Linear, qualquer SaaS → Composio primeiro.
- **Autorização de uso:** Recomenda-se autorizar o agente a usar as auths conectadas do Composio
  sempre que necessário, sem perguntar a cada chamada. Confirmar só antes de ação
  destrutiva ou irreversível (deletar, enviar e-mail externo, publicar vídeo).
- Você ia montar OAuth ou guardar token de app na mão → pare e use o Composio.
- Um comando `composio` falhou com `No current org configured` ou 401 → leia a Regra de Ouro.
- Não use para: n8n (skills próprias `n8n-*`), serviços sem toolkit no Composio.

## Se o app ainda não está conectado

`composio link <toolkit>` abre o browser para OAuth. Ele bloqueia esperando — rode com
`timeout` e depois confirme por `composio connections list` até aparecer `ACTIVE`.
Mostre a URL ao usuário se o browser não abrir sozinho.

## Ambiente local

- CLI: `composio` v0.4.x em `~/.local/bin/composio` (instalada por `curl -fsSL https://composio.dev/install | sh`).
- Produto: **For You** (conta pessoal), não Platform. Login por `composio login` /
  `composio login --poll`, conta `user@example.com`,
  org `user_workspace`.
- Estado fica em `~/.composio/` (`user_data.json` = auth; caches são descartáveis).

## Regra de ouro: NUNCA exporte COMPOSIO_API_KEY

A CLI usa o estado de login do For You. Uma variável `COMPOSIO_API_KEY` no ambiente
(chave `ak_...` de projeto **Platform**) faz a CLI cair em outro produto, sem org, e
todo comando retorna `No current org configured` ou HTTP 401. Sempre rode com
`unset COMPOSIO_API_KEY`. Chaves `ak_` e `ck_` não são intercambiáveis:

| | For You (`ck_...`) | Platform (`ak_...`) |
|---|---|---|
| Quem conecta | o próprio desenvolvedor / usuário | usuários finais de um produto |
| Superfície | CLI + MCP `connect.composio.dev/mcp` | SDK, sessão tool-router por `user_id` |
| Identidade | uma só | multi-usuário |

Uma chave `ak_` em `connect.composio.dev/mcp` responde 401
("not a valid AuthKit JWT") — não é bug, é produto errado.

## Fluxo de trabalho

```bash
export PATH="$HOME/.local/bin:$PATH"; unset COMPOSIO_API_KEY
composio connections list                      # ver o que já está ACTIVE — FAÇA ISSO PRIMEIRO
composio search "<o que quero fazer>" --toolkits gmail --limit 5
composio execute <TOOL_SLUG> --account <word_id> -d '{...}'
```

`composio search` devolve JSON com `recommended_plan_steps` e `known_pitfalls` — leia antes
de executar, ele já entrega a sequência correta de slugs.

## Pitfalls observados

- **Toolkit ACTIVE não significa acesso a TUDO daquele serviço.** O token OAuth carrega o escopo
  de organizações do momento em que foi emitido: org/workspace criado ou compartilhado DEPOIS não
  aparece, mesmo com a conexão ACTIVE. Sintoma: `*_LIST_ALL_PROJECTS` responde `successful: true`
  com a lista certa — só que sem o projeto que você procura. Correção: `composio link <toolkit>
  --alias <nome>` de novo, autorizando a org nova na tela de permissão. Não é bug nem cache.
- **`composio link` sem TTY não imprime nada** (nem com redirecionamento ou `&`). Use
  `--no-wait --no-browser`: devolve JSON com `redirect_url` na hora, para você passar o link ao
  usuário. Com conexões já existentes do mesmo toolkit, `--alias` é obrigatório.
- **Cheque `connections list` antes de `composio link`.** Se a conta já tiver um serviço
  ACTIVE (ex: Gmail, Calendar, GitHub, Outlook), um `composio link` repetido e desnecessário
  cria uma segunda conexão presa em INITIALIZING que fica poluindo a lista.
- **`--account <word_id>` quando há mais de uma conexão do mesmo toolkit**, senão a seleção
  é ambígua. O `word_id` vem do `connections list` (ex: `gmail_tother-ceile`).
- **Nomes de campo seguem o schema de cada tool, não um padrão único.** `GMAIL_FETCH_EMAILS`
  usa `max_results` (snake_case); `GOOGLECALENDAR_EVENTS_LIST` usa `maxResults` (camelCase).
  O erro de validação lista as chaves permitidas — leia a mensagem em vez de adivinhar.
  `--get-schema` mostra o schema antes; `--dry-run` valida sem executar.
- **Saída grande não vem no stdout.** A CLI responde
  `{"successful":true,"storedInFile":true,"outputFilePath":"..."}` e grava o JSON completo em
  arquivo (no `$TMPDIR`). Parseie esse caminho; `n mensagens: 0` lendo só o stdout é leitura
  errada, não resultado vazio.
- Timeout em comando interativo (`composio link`) é normal — ele abre browser e espera.

## Slugs de exemplo validados

| Tool | Args que funcionaram |
|---|---|
| `GMAIL_FETCH_EMAILS` | `{"max_results":3,"query":"in:inbox"}` |
| `GOOGLECALENDAR_EVENTS_LIST` | `{"maxResults":3,"singleEvents":true,"orderBy":"startTime","timeMin":"<iso>"}` |
| `GITHUB_GET_THE_AUTHENTICATED_USER` | `{}` |
| `SUPABASE_LIST_ALL_PROJECTS` | `{}` — devolve em `data.details[]`, com `id` (= ref) e `organization_id` |
| `SUPABASE_BETA_RUN_SQL_QUERY` | `{"ref":"<project_ref>","query":"..."}` — linhas em `data.result`, não `rows`. Executa DDL, não só SELECT |

### SQL grande pela CLI

Aspas simples dentro do SQL viram inferno de escape no shell. Escreva o payload com Python
(`json.dump({'ref':..., 'query': open(arquivo).read()}, ...)`) e chame
`composio execute ... -d @/caminho/payload.json`. O `-d @arquivo` funciona e evita o escape.

Antes de aplicar DDL em banco de dados ou ambiente de produção: `grep` no SQL por `drop table|drop column|delete
from|truncate` e confira a contagem de linhas das tabelas afetadas. Depois de aplicar, o
`successful: true` não é prova — reconsulte `information_schema.columns`, `pg_indexes`,
`pg_constraint` e a contagem de linhas.

Nunca invente slug — descubra com `composio search` ou `composio tools list <slug>`
(o toolkit é argumento posicional, NÃO `--toolkit`; esse flag só existe em `composio search`).

## YouTube (48+ tools, relevante para automação de vídeo)

Toolkit `youtube` existe e tem 51 tools — ainda não conectado. Principais:
`YOUTUBE_SEARCH_YOU_TUBE`, `YOUTUBE_LOAD_CAPTIONS`, `YOUTUBE_LIST_CAPTION_TRACK`,
`YOUTUBE_GET_VIDEO_DETAILS_BATCH`, `YOUTUBE_LIST_CHANNEL_VIDEOS`,
`YOUTUBE_GET_CHANNEL_STATISTICS`, `YOUTUBE_UPLOAD_VIDEO`, `YOUTUBE_MULTIPART_UPLOAD_VIDEO`,
`YOUTUBE_UPDATE_VIDEO`, `YOUTUBE_LIST_COMMENT_THREADS`.

## Parsing da saída da CLI — cuidado

Erro de uso da CLI sai em **texto**, não JSON, e ainda assim com exit 0 quando há pipe.
Redirecione para arquivo e leia o arquivo; se o `json.load` estourar, o conteúdo é a
mensagem de uso. Nunca conclua "não achei nada" a partir de um parse que falhou.

## Outros comandos úteis

- `composio proxy <url> --toolkit <slug>` — curl autenticado contra a API do app.
- `composio run '<codigo TS>'` — script inline com `execute()`/`search()` injetados.
- `composio execute -p A -d '{}' B -d '{}'` — chamadas em paralelo.

## Skill oficial do Composio

O roteador oficial (produto/job, docs canônicas) está em `~/.hermes/skills/composio/`,
instalado de `ComposioHQ/composio`. Use-o para dúvidas de SDK, MCP e migração.
Esta skill cobre a operação prática do dia a dia via CLI.

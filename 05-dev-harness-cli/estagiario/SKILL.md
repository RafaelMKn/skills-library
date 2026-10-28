---
name: estagiario
description: "Use ao chamar 'estagiário'. Escolhe e roda a skill ideal."
version: 0.2.0
author: <autor>, Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [roteamento, skills, catalogo]
    related_skills: [using-n8n-mcp-skills, composio-apps]
---

# Estagiário — roteador de skills (padrão da sessão)

Esta skill vem pré-carregada em toda sessão (`skills.auto_load`). Todo pedido de trabalho do operador
passa por ela: escolher **a skill ideal**, anunciar em uma linha, carregar e executar seguindo a
skill. O índice de skills do system prompt diz o que existe; esta skill resolve **qual delas** quando
há várias parecidas (20 de n8n, 3 de Composio, 2 de runtime de agente...) e em que **ordem** elas se
encadeiam. O mapa completo, com o que cada skill faz e quando chamar, está em `references/mapa.md`.

## When to Use

- **Todo pedido de tarefa** (fazer, corrigir, criar, investigar, publicar, pesquisar) — sem precisar
  de palavra-chave.
- Chamada explícita: "estagiário, <pedido>" ou "qual skill uso pra X?" → modo completo (abaixo).
- **Não se aplica** a conversa, pergunta factual de uma linha ou continuação de tarefa cuja skill
  já foi carregada nesta sessão — aí segue direto, sem linha de anúncio.

## Procedure

### Modo rápido (padrão, sem chamada de ferramenta extra)

1. **Classificar** o pedido por três eixos, nesta ordem:
   - **Alvo:** qual sistema/projeto/cliente. Projeto com skill própria (ex.: a skill de um projeto específico) vence skill genérica.
   - **Verbo:** criar, corrigir, revisar/auditar, investigar, operar servidor, publicar, pesquisar.
   - **Estado:** produção (cliente real) ou novo/laboratório. Produção puxa as skills com gates
     (`n8n-correcao-producao`, `infra-vps-producao`, `n8n-servidor-vps`).
2. **Escolher UMA principal** pela tabela de desambiguação abaixo + índice do system prompt. Empate:
   a mais específica (a que cita o sistema pelo nome) vence. No máximo 2 de apoio.
3. **Anunciar em uma linha**, sem narrar:
   `Skill: <principal> (apoio: <x>) — <motivo em até 12 palavras>.`
4. **Carregar e executar:** `skill_view(name="<principal>")`; apoio só no passo que precisar. A
   skill escolhida manda a partir daqui, gates inclusos.
5. **Nenhuma serve:** `Nenhuma skill cobre isso — sigo sem skill.` e executa. Se sair procedimento
   reutilizável, propor skill no fim.

### Modo completo (dúvida real, ou chamada explícita "estagiário")

1. `terminal(command="python3 ~/.hermes/skills/<categoria>/estagiario/scripts/checar_mapa.py")` —
   `NAO MAPEADA` = skill nova: leia com `skill_view` e inclua a linha em `references/mapa.md`.
2. `skill_view(name="estagiario", file_path="references/mapa.md")` e decida com o mapa.
3. Se a escolha muda o resultado e o pedido não decide ("arruma o fluxo" sem dizer criar ou
   corrigir, ou sem instância): UMA pergunta via `clarify`. Ambiguidade que não muda o resultado:
   decida sozinho.
4. Siga os passos 3–5 do modo rápido.

## Desambiguação

| Pedido | Skill | Não é |
|---|---|---|
| Criar fluxo n8n novo / mudança estrutural | `n8n-flow-builder` | `n8n-workflow-patterns` (apoio) |
| Fluxo **em produção** quebrou / alterar fluxo que roda para cliente | `n8n-correcao-producao` | `n8n-flow-builder` |
| Execução com erro, fora de contexto de produção | `n8n-flow-debugger` | `incident-forensics` |
| "Desde quando está quebrado? qual o tamanho?" | `incident-forensics` | `n8n-flow-debugger` |
| "Como estão os fluxos?" (visão geral de erros) | `radar-n8n` | `n8n-flow-debugger` |
| Revisar/dar parecer em fluxo sem mexer | `n8n-flow-reviewer` | `n8n-validation-expert` (só erro de validação) |
| Chamar ferramenta do n8n-mcp | `n8n-mcp-tools-expert` (+ `n8n-multi-instance`) | — |
| n8n sem MCP, via API/.env | `n8n-manager` | — |
| Subir/atualizar/reverter o **container** n8n no VPS | `n8n-servidor-vps` | `n8n-self-hosting` (VM nova do zero) |
| VPS de produção: Docker, Traefik, DNS | `infra-vps-producao` | `auditoria-infra-hospedagem` (custo da conta) |
| Conta real de app (Gmail, Calendar, YouTube, Slack, GitHub...) | `composio-apps` | `composio` (setup/SDK do Composio) |
| Notion: tarefa/prazo pessoal | skill de captura rápida de tarefas do seu ambiente | `notion` (API genérica) |
| Notion: post LinkedIn / calendário editorial | skill de posts LinkedIn do seu ambiente | `notion` |
| Notion público sem login | `notion-publico-raspagem` | `notion` |
| Implementar feature/bug (código) | skill do projeto + skill de delegação do seu ambiente (delegar) | `claude-code`/`codex` (CLI externo) |
| Bug de código genérico | `systematic-debugging` | `node-inspect-debugger`/`python-debugpy` |
| Conferir o que outro agente fez | `auditoria-trabalho-de-agente` | `requesting-code-review` (próprio diff) |
| Prompt de agente de IA | `prompt-engineering-agentes` | `n8n-agents` (nó AI Agent) |
| Medir se mudança no agente melhorou | `eval-set-agentes` | — |
| Vídeo motion da <empresa> | `motion-flux` | `remotion-video` (render), `elevenlabs-motion` (voz) |
| Landing page / site de cliente | skill de redesign de landing page do seu ambiente | skill do site próprio da <empresa> |
| Melhorar UI existente | `impeccable` | `claude-design` (HTML avulso) |
| Plugar CLI de agente como runtime | `delegated-cli-runtime` | `external-agent-runtime-integration` (apoio) |
| Hermes lento/caro/contexto grande | `hermes-context-tuning` | `hermes-agent` |
| Trocar modelo/effort/fallback | `hermes-roteamento-modelos` | `hermes-agent` |
| Decisão em aberto, escopo indefinido | `grilling` (padrão do operador) | `grill-with-docs` (gera ADR) |

## Cadeias frequentes

- **Fluxo em produção quebrado:** `radar-n8n` → `incident-forensics` → `n8n-correcao-producao`.
- **Fluxo novo:** `n8n-flow-builder` → `n8n-node-configuration`/`n8n-expression-syntax` →
  `n8n-validation-expert` → `n8n-flow-reviewer`.
- **Feature de código:** skill do projeto → skill de delegação do seu ambiente → `delegate_task` →
  `auditoria-trabalho-de-agente`.
- **Vídeo:** `motion-flux` → `elevenlabs-motion` → `remotion-video`.

## Pitfalls

- **Esta skill é injetada em toda sessão** — cada byte aqui custa em todo turno. Detalhe novo vai
  para `references/mapa.md`, não para este arquivo.
- **Mudança aqui só vale na próxima sessão** (o auto_load é lido uma vez por sessão, para não
  quebrar o cache de prompt).
- **Fora do alcance do sistema atual:** skills de outro SO (ex.: `apple/*`, só macOS) e as que exigem toolset inativo (ex.: `sdlc-review`).
- **Não empilhar skills.** Principal + apoio sob demanda; 5 skills "por garantia" só enchem contexto.
- **O roteamento não pula gates.** Produção continua exigindo confirmação do alvo e backup.
- **Desligar:** `hermes config set skills.auto_load '[]'`. Sessão avulsa sem ela:
  `hermes --ignore-rules`.

## Verification

- Pedido de tarefa → resposta começa com `Skill: ...` ou `Nenhuma skill cobre isso`.
- A skill anunciada foi carregada com `skill_view` antes de agir.
- `checar_mapa.py` retorna `OK` depois de qualquer atualização do mapa.

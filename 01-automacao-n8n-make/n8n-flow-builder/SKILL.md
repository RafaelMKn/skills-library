---
name: n8n-flow-builder
description: Protocolo de construção de fluxos n8n do zero ao ativo. Use sempre que for criar um workflow novo ou fazer uma alteração estrutural em um existente (adicionar nós, mudar arquitetura, adicionar agente de IA). Encadeia as skills especialistas na ordem certa e define os portões de qualidade antes da ativação.
---

# n8n Flow Builder — Protocolo de Construção

Você vai construir ou alterar estruturalmente um fluxo n8n. Siga as etapas **na ordem**. Cada etapa aponta a skill especialista que é dona das regras — invoque-a antes de agir.

## Etapa 0 — Contexto
1. Organize todos os artefatos (JSON, docs) na pasta de fluxos do projeto (ex.: `projetos/<nome>/fluxos/` ou `workflows/`).
2. Consulte o roteador `using-n8n-mcp-skills` se ainda não o fez nesta sessão.
3. Busque antes de construir: `n8n_list_workflows` (MCP) ou `n8n_api.py list-workflows` — o fluxo (ou um sub-workflow reutilizável) pode já existir.

## Etapa 1 — Arquitetura (`n8n-workflow-patterns`)
Escolha o padrão (webhook / HTTP API / database / AI agent / scheduled / batch) ANTES de criar qualquer nó. Fluxos "simples" de produção normalmente terminam com 10+ nós — planeje trigger, caminho feliz, branches de erro e resposta.

## Etapa 2 — Configuração de nós (`n8n-node-configuration`)
- `get_node` (forma CURTA, ex.: `nodes-base.httpRequest`) antes de configurar QUALQUER nó. Nunca configure de memória — parâmetros lembrados validam como string e falham silenciosamente em runtime.
- Expressões: `n8n-expression-syntax` (dados de webhook vivem em `$json.body`; prefira `$('Node').item.json.x` em fluxos com branches).
- Code node é último recurso (`n8n-code-javascript`): expressão → Edit Fields → Code.
- Agentes de IA: `n8n-agents` (nomes/descrições de tools SÃO o prompt).
- Arquivos/binário: `n8n-binary-and-data`.

## Etapa 3 — Resiliência (`n8n-error-handling`)
Fluxo webhook/agendado/não-assistido sem branch de erro não está pronto. Wire error outputs nos nós faliveis, defina `retryOnFail` onde fizer sentido, mapeie respostas 4xx (culpa do chamador) vs 5xx (sua culpa).

## Etapa 4 — Segredos
Tokens/chaves SEMPRE pelo sistema de credenciais do n8n. Um Set node segurando token é vazamento. Se não houver nó nativo, HTTP Request + credential type oficial.

## Etapa 5 — Deploy
- **Preferido:** MCP `n8n_create_workflow` / `n8n_update_partial_workflow` (edições incrementais).
- **Fallback:** escrever o JSON em `scratch/` e usar `python skills/n8n-manager/scripts/n8n_api.py create-workflow scratch/fluxo.json` (apague o arquivo depois). Guarde uma cópia permanente em `projetos/<nome>/fluxos/` ou `workflows/*.json`.

## Etapa 6 — Portão de qualidade (OBRIGATÓRIO antes de ativar)
1. `validate_workflow` (MCP) — nomes de nó em forma LONGA (`n8n-nodes-base.set`). Corrija erros; confira falsos positivos com `n8n-validation-expert`.
2. `n8n_get_workflow` após todo create/update e **inspecione `connections`**: validação não pega fio silenciosamente descartado, índice de Merge errado nem error output não conectado.
3. Varredura de antipatterns da skill `n8n-flow-reviewer`.
4. Só então ative (`activateWorkflow` via MCP ou `n8n_api.py activate-workflow <ID>`).

## Etapa 7 — Prova de vida
Peça permissão antes de testar quando houver efeitos colaterais (envio de mensagens, escrita em DB). Depois do teste, confira a execução: `n8n_executions` (MCP) ou `n8n_api.py list-executions --workflow-id <ID> --limit 3`.

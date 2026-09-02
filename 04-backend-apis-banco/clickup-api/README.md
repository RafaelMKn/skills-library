# clickup-api

> Chame a API REST v2/v3 do ClickUp diretamente para consultar, criar, atualizar ou gerenciar workspaces, spaces, folders, lists, tasks, comentários, checklists, tags, webhooks e docs. Na primeira execução, pergunta as informações básicas ao usuário, executa auto-descoberta e se auto-complementa gerando o arquivo de contexto local (.clickup-context.md). Use quando o pedido envolver buscar/criar/atualizar tarefas no ClickUp, listar tasks/lists/spaces, comentar em tarefas ou automatizar o ClickUp via API.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **clickup-api**.


## 📁 Estrutura de Arquivos

- [SKILL.md](SKILL.md)
- [scripts\clickup_api.py](scripts\clickup_api.py)

---

## 🛠️ Conteúdo da Skill

# ClickUp API (Guia, Onboarding & CLI)

Skill para interagir diretamente com a **API REST v2/v3 do ClickUp** via Python CLI (`scripts/clickup_api.py`), utilizando autenticação por Personal API Token.

---

## 🚀 1. Protocolo de Primeira Execução & Auto-Complementação (Onboarding)

Ao iniciar uma sessão ou executar esta skill pela primeira vez em um workspace, siga este fluxo passo a passo:

### Passo 1: Verificar Existência do Contexto Local
1. Verifique se o arquivo `.clickup-context.md` existe na raiz do workspace ou projeto.
2. Verifique se a variável `CLICKUP_API_TOKEN` está configurada no `.env` ou no ambiente do sistema.

### Passo 2: Questionário Inicial ao Usuário (Se não configurado)
Se as informações ainda não estiverem configuradas, faça as seguintes perguntas objetivas ao usuário:

1. **Token de Acesso:**
   > *"Você já possui seu **ClickUp Personal API Token** configurado? Se não, por favor informe seu token (formato `pk_...`, obtido em ClickUp Settings → Apps → API Token) para que eu salve no seu `.env` com segurança."*
2. **Workspace & Lista Principal:**
   > *"Qual workspace ou lista principal você deseja utilizar para as tarefas deste projeto? (Se preferir, posso listar os workspaces e pastas disponíveis na sua conta para você escolher)."*
3. **Padrão da Equipe (Opcional):**
   > *"Há algum membro específico para quem as tarefas devem ser atribuídas por padrão ou alguma convenção de nomes/prefixos que você gostaria de adotar?"*

### Passo 3: Executar Auto-Descoberta via CLI
Com o token configurado, rode os comandos de inspeção para mapear os IDs reais do ClickUp:

```bash
# 1. Identificar workspaces (teams) e membros autorizados
python skills/clickup-api/scripts/clickup_api.py list-workspaces
python skills/clickup-api/scripts/clickup_api.py list-members <TEAM_ID>

# 2. Mapear spaces, folders e listas disponíveis
python skills/clickup-api/scripts/clickup_api.py list-spaces <TEAM_ID>
python skills/clickup-api/scripts/clickup_api.py list-folders <SPACE_ID>
python skills/clickup-api/scripts/clickup_api.py list-lists <FOLDER_ID>
python skills/clickup-api/scripts/clickup_api.py list-folderless-lists <SPACE_ID>

# 3. Descobrir os custom fields disponíveis na lista escolhida
python skills/clickup-api/scripts/clickup_api.py list-custom-fields <LIST_ID>
```

> **Nota para contas Guest:** Se `list-spaces` retornar vazio, utilize `list-shared <TEAM_ID>` para descobrir hierarquias compartilhadas.

### Passo 4: Auto-Complementação do Arquivo `.clickup-context.md`
Gere automaticamente o arquivo `.clickup-context.md` na raiz do projeto com o resultado da descoberta. Isso garante que nas próximas execuções a IA consulte diretamente esse arquivo sem precisar perguntar novamente:

```markdown
# 📋 Contexto do ClickUp — [Nome do Workspace / Projeto]

- **Workspace (Team ID):** `<TEAM_ID>`
- **Lista Principal de Tarefas:** `<LIST_ID>` (ex: Backlog / Demandas)
- **Membros da Equipe:**
  - `Nome do Membro 1`: `<USER_ID_1>`
  - `Nome do Membro 2`: `<USER_ID_2>`
- **Custom Fields Relevantes:**
  - `Prioridade/Situação`: UUID `<FIELD_UUID>` (Tipo: drop_down)
  - `Data de Entrega`: UUID `<FIELD_UUID>` (Tipo: date)
- **Fluxo de Statuses:** `backlog` → `em andamento` → `revisão` → `concluído`
```

---

## 🛠️ 2. Comandos CLI (`scripts/clickup_api.py`)

O script auxiliar localizado em `scripts/clickup_api.py` fornece comandos diretos para todas as operações essenciais:

### Estrutura & Descoberta
```bash
python scripts/clickup_api.py list-workspaces
python scripts/clickup_api.py list-members <TEAM_ID>
python scripts/clickup_api.py list-spaces <TEAM_ID> [--archived true/false]
python scripts/clickup_api.py list-shared <TEAM_ID>
python scripts/clickup_api.py list-folders <SPACE_ID>
python scripts/clickup_api.py list-lists <FOLDER_ID>
python scripts/clickup_api.py list-folderless-lists <SPACE_ID>
python scripts/clickup_api.py list-custom-fields <LIST_ID>
```

### Tarefas (Tasks)
```bash
# Listar tarefas com filtros
python scripts/clickup_api.py list-tasks <LIST_ID> [--include-closed] [--page 0] [--statuses "em andamento"]

# Obter detalhes de uma tarefa
python scripts/clickup_api.py get-task <TASK_ID>

# Criar tarefa a partir de um JSON
python scripts/clickup_api.py create-task <LIST_ID> payload.json

# Atualizar tarefa
python scripts/clickup_api.py update-task <TASK_ID> payload.json

# Deletar tarefa
python scripts/clickup_api.py delete-task <TASK_ID>
```

### Custom Fields
Custom fields **não** são alterados via `update-task`, devendo ser definidos pelo comando dedicado:
```bash
python scripts/clickup_api.py set-custom-field <TASK_ID> <FIELD_UUID> <VALOR> [--json]
# Exemplos:
# - Dropdown: passar o orderindex (int)
# - Labels/Multi-select: passar o UUID da opção
# - Date: timestamp em milissegundos
# - Arrays/Objetos: use flag --json
```

### Comentários & Notificações
```bash
python scripts/clickup_api.py list-comments <TASK_ID>
python scripts/clickup_api.py add-comment <TASK_ID> "Texto do comentário" [--notify-all] [--assignee <USER_ID>]
```

### Checklists
```bash
python scripts/clickup_api.py create-checklist <TASK_ID> "Nome do Checklist"
python scripts/clickup_api.py add-checklist-item <CHECKLIST_ID> "Item a fazer"
python scripts/clickup_api.py update-checklist-item <CHECKLIST_ID> <ITEM_ID> --resolved / --unresolved
python scripts/clickup_api.py delete-checklist <CHECKLIST_ID>
```

### Tags
```bash
python scripts/clickup_api.py list-tags <SPACE_ID>
python scripts/clickup_api.py create-tag <SPACE_ID> "nome-da-tag" [--fg "#000000"] [--bg "#ffc53d"]
python scripts/clickup_api.py add-task-tag <TASK_ID> "nome-da-tag"
python scripts/clickup_api.py remove-task-tag <TASK_ID> "nome-da-tag"
```

### Docs & Páginas (API v3)
```bash
python scripts/clickup_api.py list-docs <WORKSPACE_ID> [--query "termo"]
python scripts/clickup_api.py list-doc-pages <WORKSPACE_ID> <DOC_ID>
python scripts/clickup_api.py get-doc-page <WORKSPACE_ID> <DOC_ID> <PAGE_ID> [--content-format text/md]
```

### Webhooks
```bash
python scripts/clickup_api.py list-webhooks <TEAM_ID>
python scripts/clickup_api.py create-webhook <TEAM_ID> payload.json
```

---

## 📝 3. Estrutura de Payloads JSON

Ao criar ou atualizar tarefas com `create-task` ou `update-task`, utilize um arquivo temporário em `scratch/payload.json`:

### Exemplo de Payload para Criação de Tarefa:
```json
{
  "name": "Implementar autenticação OAuth2",
  "markdown_description": "## Objetivo\nConfigurar fluxo de autorização PKCE para a API.\n\n### Checklist Técnico\n- [ ] Definir rotas\n- [ ] Validar tokens",
  "assignees": [12345678],
  "status": "in progress",
  "priority": 2,
  "due_date": 1725000000000,
  "notify_all": false
}
```

> **Tabela de Prioridades ClickUp:** `1` = Urgente, `2` = Alta, `3` = Normal, `4` = Baixa.

---

## ⚠️ 4. Boas Práticas e Tratamento de Erros

1. **Segredos e Tokens:** Nunca imprima tokens `pk_...` em logs, prompts ou saídas públicas.
2. **Rate Limits:** O ClickUp impõe limites de taxa (100 req/min no plano Free/Business; até 10.000 no Enterprise). O script reporta `429` com os headers informativos quando atingido.
3. **Workspace Guest:** Se `list-spaces` retornar vazio com código 200, a conta possui perfil de *Guest*. Utilize `list-shared <TEAM_ID>` para inspecionar os itens compartilhados.
4. **Custom Fields isolados:** Lembre-se de que campos personalizados exigem a chamada de `set-custom-field` separadamente após a criação da tarefa.
5. **Verificação de Fechamento:** Não confie apenas no nome do status (ex: "arquivado" pode ser do tipo aberto). Sempre valide `status.type == "closed"` ou `date_closed`.

---

## 📚 5. Documentação Oficial

- [ClickUp API Reference (v2/v3)](https://developer.clickup.com/reference)
- [Guia de Autenticação ClickUp](https://developer.clickup.com/docs/authentication)
- [Gestão de Rate Limits](https://developer.clickup.com/docs/rate-limits)

---
*Parte da [Skills Library](../../README.md)*

# n8n-manager

> Use esta skill quando precisar criar, editar, listar, recuperar, excluir, ativar/desativar fluxos ou inspecionar execuções (inclusive com erro) no n8n do usuário usando a API. Ela fornece acesso direto às credenciais do .env através de um script auxiliar em Python. Fallback para quando o servidor MCP n8n-mcp não estiver disponível.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **n8n-manager**.


## 📁 Estrutura de Arquivos

- [SKILL.md](SKILL.md)
- [scripts\n8n_api.py](scripts\n8n_api.py)

---

## 🛠️ Conteúdo da Skill

# n8n Manager Skill

Esta skill permite interagir diretamente com a API do n8n do usuário para gerenciar seus fluxos de trabalho. Ela utiliza as credenciais de API configuradas no arquivo `.env` da raiz do workspace.

> **Prefira o servidor MCP `n8n-mcp`** (configurado em `.mcp.json` na raiz) quando ele estiver disponível: ele oferece validação (`validate_workflow`), schema de nós (`get_node`), busca (`search_nodes`) e edição incremental — coisas que este script não faz. Use este script como **fallback** ou para operações rápidas de CLI (listar, ativar, inspecionar execuções).

## Comandos Disponíveis

O script de suporte está localizado em:
`file:///skills/n8n-manager/scripts/n8n_api.py`

### 1. Listar Fluxos (Workflows)
Retorna a lista de todos os workflows do n8n.
```bash
python skills/n8n-manager/scripts/n8n_api.py list-workflows [--name "Nome do Fluxo"] [--active true|false] [--limit 50]
```

### 2. Recuperar Detalhes de um Fluxo
Busca a definição completa de um fluxo específico por ID.
```bash
python skills/n8n-manager/scripts/n8n_api.py get-workflow <ID_DO_FLOW>
```

### 3. Criar Novo Fluxo
Para criar um fluxo:
1. Escreva o payload JSON do workflow em um arquivo temporário no workspace (ex: `scratch/new_flow.json`). O JSON deve seguir a estrutura exigida pelo n8n (`name`, `nodes`, `connections`, `settings`).
2. Execute o comando:
   ```bash
   python skills/n8n-manager/scripts/n8n_api.py create-workflow scratch/new_flow.json
   ```
3. Exclua o arquivo temporário após o término.

### 4. Editar Fluxo Existente
Para editar um fluxo:
1. Escreva a nova definição completa do workflow em um arquivo JSON temporário (ex: `scratch/update_flow.json`).
2. Execute o comando:
   ```bash
   python skills/n8n-manager/scripts/n8n_api.py update-workflow <ID_DO_FLOW> scratch/update_flow.json
   ```
3. Exclua o arquivo temporário após o término.

### 5. Excluir Fluxo
Exclui permanentemente um workflow pelo ID.
```bash
python skills/n8n-manager/scripts/n8n_api.py delete-workflow <ID_DO_FLOW>
```

### 6. Ativar/Publicar Fluxo
Ativa um workflow (equivalente a "Publish/Activate" no painel do n8n).
```bash
python skills/n8n-manager/scripts/n8n_api.py activate-workflow <ID_DO_FLOW>
```

### 7. Desativar Fluxo
Desativa um workflow ativo.
```bash
python skills/n8n-manager/scripts/n8n_api.py deactivate-workflow <ID_DO_FLOW>
```

### 8. Listar Execuções (debug)
Lista execuções recentes, com filtros por workflow e status. Essencial para diagnosticar fluxos que falham.
```bash
python skills/n8n-manager/scripts/n8n_api.py list-executions [--workflow-id <ID>] [--status error|success|waiting] [--limit 20]
```

### 9. Detalhar uma Execução
Busca uma execução específica. Com `--include-data`, retorna os dados completos de entrada/saída de cada nó e o detalhe do erro do nó que falhou (a resposta pode ser grande).
```bash
python skills/n8n-manager/scripts/n8n_api.py get-execution <ID> [--include-data]
```

## Diretrizes Importantes

- **Limpeza**: Sempre remova os arquivos JSON temporários gerados em `scratch/` após a criação ou edição.
- **Tratamento de Erros**: O script retornará JSON no stderr se houver erro (por exemplo, erro HTTP da API ou erro de sintaxe do JSON).

---
*Parte da [Skills Library](../../README.md)*

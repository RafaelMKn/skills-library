---
name: notion-reestruturacao-workspace
description: "Use when restructuring a Notion workspace safely."
version: 0.1.0
author: "<autor>"
license: MIT
metadata:
  hermes:
    tags: [notion, composio, reestruturacao, cockpit]
    related_skills: [composio-apps, notion]
---

# Reestruturação de workspace Notion (via Composio)

Classe: reorganizar um workspace Notion que já roda (template grande, Home poluída, bases mortas,
cockpit/dashboard novo) sem perder dado nem relação. O operador aprova por etapa: entregue um passo,
relate o que foi verificado, espere o ok antes do próximo. Mover/esconder > apagar, sempre.

## When to Use

- Reorganizar Home/menu, arquivar bases sem uso, montar cockpit de views ligadas.
- Continuar um plano de reestruturação discutido em outra sessão/modelo.
- Só ajustar colunas/largura de uma view existente → a skill de apresentação de views do seu ambiente.

## Procedimento

1. **Contexto de outra conversa** ("tava falando com o Gemini sobre..."): o plano está em
   `~/.hermes/state.db` (read-only). Ache a sessão com
   `select session_id, max(timestamp) from messages where content like '%<termo>%' group by 1 order by 2 desc`
   e leia `messages` daquela sessão. Trate o diagnóstico do outro modelo como hipótese: confira
   contra a API antes de agir e diga onde ele errou.
2. **Acesso:** `composio connections list --toolkit notion` → escolha a conta pelo alias
   (`<conta-empresa>`/`<conta-pessoal>`). Use `scripts/np.py` (wrapper de `composio proxy` na API REST,
   `Notion-Version: 2025-09-03`, já desembrulha `data`/`storedInFile`); conta via env
   `NOTION_ACCOUNT`. Confirme com `users/me` → `workspace_name`.
3. **Inventário:** `search` paginado de `data_source` e `page`; para cada base: contagem de linhas,
   relações (com `data_source_id` de destino), `database_parent`. Para saber em qual página cada base
   mora, suba a cadeia `parent` até `child_page`.
4. **Backup antes de qualquer escrita:** schema + todas as linhas de todas as bases + blocos da
   Home → `<backups>/notion-<workspace>/backup_<ts>.json`. Com ~50 bases leva ~5 min:
   rode em background e siga com trabalho aditivo enquanto isso. Antes de cada passo destrutivo,
   snapshot extra do que vai mudar (view config, página afetada).
5. **Cockpit (aditivo, risco zero):** página nova filha da Home; para cada pergunta (hoje, comercial,
   projetos, caixa, OKRs) um `heading_2` + `NOTION_CREATE_VIEW` (`composio execute ... -d @v.json`)
   com `create_database: {parent: {type: page_id, page_id: <cockpit>}}`, `data_source_id`, `filter`,
   `sorts`. A view entra no fim da página — crie heading e view intercalados, na ordem final.
   Rode o mesmo filtro em `data_sources/<id>/query` e reporte a contagem real de cada view.
   Ajuste de view depois: `PATCH views/<view_id> {name, filter}`.
6. **Arquivar bases mortas:** página "Módulos Inativos (Arquivo)" com aviso "não deletar". Mova com
   `PATCH databases/<database_id> {parent: {type: page_id, page_id: <arquivo>}}`. Teste com UMA,
   confira relação de quem apontava para ela, depois o lote. Ao fim, compare props/tipos/destino de
   relação e contagem de linhas das bases ativas contra o backup (meta: 0 diffs).
7. **Enxugar Home/menu:** esconder itens do menu-galeria com `PATCH views/<view_id> {filter}`
   (`title does_not_equal`), conferindo que `configuration` ficou igual. Conteúdo a preservar
   (Missão/Visão/Valores) → recrie dentro de um toggle, compare o texto, só então `DELETE` dos
   originais. Propaganda de template pode ser apagada (lixeira 30 dias).
8. **Relato:** o que mudou, como foi verificado, onde estão os backups, o que ficou de fora e por quê;
   avise que a verificação foi via API, não visual.

## Pitfalls

- **Base vazia não é base morta.** Cheque relações *entrantes*: uma base com 0 linhas pode ser o hub
  do comercial (todas as outras apontam para ela). Arquive só vazias sem papel de hub.
- **Item do menu é a página que hospeda as bases** daquela área. Apagar o item apaga as bases; esconda
  pelo filtro da view.
- **Página filha de base pode ser modelo** (ex.: "Novo Membro" dentro de Membros) usado ao cadastrar
  linha nova — não apague mesmo parecendo lixo de template.
- **Filtro de data exclui data vazia.** "Atrasadas + hoje" vem vazio se as tarefas abertas não têm
  data; use `or: [on_or_before today, is_empty]` e valide a contagem.
- **Mover base (`PATCH databases`) preserva relações e rollups**; ainda assim prove com o diff de
  schema contra o backup, não com suposição.
- Painéis antigos da Home com views mais ricas (calendário, cronograma) ficam até o operador decidir.
- Cockpit vazio expõe dado parado (sem datas, reuniões antigas): diga isso — estrutura não resolve
  falta de alimentação.

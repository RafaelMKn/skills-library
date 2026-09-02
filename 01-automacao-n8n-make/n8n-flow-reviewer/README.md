# n8n-flow-reviewer

> Protocolo de revisão read-only de um fluxo n8n (JSON local ou workflow na instância). Use quando pedirem para revisar, validar, auditar ou dar parecer sobre um fluxo — antes de ativar, antes de entregar a cliente, ou ao herdar um fluxo existente. Produz lista de problemas com severidade, sem modificar nada.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **n8n-flow-reviewer**.


---

## 🛠️ Conteúdo da Skill

# n8n Flow Reviewer — Protocolo de Revisão

Revisão é **read-only**: você aponta problemas, não corrige (a correção é outro pedido, com o `n8n-flow-builder`).

## Entrada
- JSON local (ex.: `projetos/<projeto>/fluxos/*.json` ou `workflows/*.json`) → leia o arquivo.
- Workflow na instância → `n8n_get_workflow` (MCP) ou `python skills/n8n-manager/scripts/n8n_api.py get-workflow <ID>`.

## Passo 1 — Validação mecânica
Rode `validate_workflow` (MCP, nomes em forma LONGA). Interprete os resultados com `n8n-validation-expert` — consulte `FALSE_POSITIVES.md` antes de reportar warnings como erros, e `ERROR_CATALOG.md` para explicar cada erro real.

## Passo 2 — Checklist estrutural
Aplique `skills/n8n-validation-expert/REVIEW_CHECKLIST.md` e verifique manualmente o objeto `connections` (validação não cobre):
- [ ] Todo nó não-trigger é alcançável a partir de um trigger?
- [ ] Algum fio caindo em índice errado de Merge (off-by-one)?
- [ ] Error outputs declarados mas não conectados?
- [ ] Nós órfãos/mortos?

## Passo 3 — Varredura de antipatterns
| Antipattern | Por que é problema | Skill dona |
|---|---|---|
| Set node alimentando ≤1 consumidor | Inline a expressão no consumidor | `n8n-expression-syntax` |
| Code node que uma expressão/Edit Fields resolveria | Manutenção e performance | `n8n-code-javascript` |
| Merge com 3+ fontes | Merge default tem 2 entradas; a 3ª cai silenciosamente | `n8n-node-configuration` |
| Webhook/agendado sem branch de erro | Falha silenciosa em produção | `n8n-error-handling` |
| Token/chave em campo de texto ou Set node | Vazamento de segredo | `n8n-mcp-tools-expert` |
| Loop Over Items desnecessário | Iteração por item já é automática | `n8n-workflow-patterns` |
| `$json.x` em fluxo com branches | Referência frágil; usar `$('Node').item.json.x` | `n8n-expression-syntax` |
| Webhook lendo `$json.campo` em vez de `$json.body.campo` | Dado de webhook vive em `body` | `n8n-expression-syntax` |
| Resposta HTTP sem distinção 4xx/5xx | Depuração impossível para o chamador | `n8n-error-handling` |
| Agente de IA com tools sem descrição clara | Descrições SÃO o prompt | `n8n-agents` |

## Passo 4 — Relatório
Entregue lista ordenada por severidade, em PT-BR:
- **🔴 Crítico** — quebra em produção ou vaza segredo (bloqueia ativação).
- **🟡 Importante** — falha em caso de borda ou dificulta manutenção.
- **🔵 Sugestão** — simplificação/idiomático.

Para cada item: nó afetado, problema em uma frase, correção recomendada. Termine com veredito: **apto para ativar** ou **bloqueado por N críticos**.

---
*Parte da [Skills Library](../../README.md)*

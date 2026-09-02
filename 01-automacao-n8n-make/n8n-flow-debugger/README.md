# n8n-flow-debugger

> Protocolo de diagnóstico de fluxos n8n que falham ou se comportam errado em execução. Use quando houver execução com erro, webhook que não responde, nó que retorna dado errado ou fluxo que "funcionava ontem". Parte da execução real (não do JSON) e propõe a correção mínima.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **n8n-flow-debugger**.


---

## 🛠️ Conteúdo da Skill

# n8n Flow Debugger — Protocolo de Diagnóstico

Regra de ouro: **acredite no usuário e parta da execução real**, não do JSON. O que o fluxo faz em runtime vence o que ele parece fazer no editor.

## Passo 1 — Capturar a evidência
1. Liste as execuções com falha:
   - MCP: `n8n_executions`
   - CLI: `python skills/n8n-manager/scripts/n8n_api.py list-executions --status error [--workflow-id <ID>] --limit 10`
2. Pegue a execução relevante com dados completos:
   - CLI: `python skills/n8n-manager/scripts/n8n_api.py get-execution <ID> --include-data`
3. Identifique: qual nó falhou, mensagem de erro, e o **dado de entrada** que o nó recebeu (metade dos bugs é dado com shape inesperado, não configuração).

## Passo 2 — Classificar o erro
Cruze a mensagem com `skills/n8n-validation-expert/ERROR_CATALOG.md` e `skills/n8n-error-handling/NODE_ERROR_OUTPUTS.md`. Classes comuns:
- **Dado inesperado** — expressão referencia campo que não existe naquele item (`undefined`); confira o shape real na execução.
- **Configuração** — parâmetro errado/ausente; confira contra `get_node` (schema vivo), nunca de memória.
- **Credencial/permissão** — 401/403 da API externa; credencial expirada ou escopo faltando.
- **Rate limit / transiente** — 429/5xx do serviço externo; falta `retryOnFail`.
- **Expressão** — sintaxe (`{{ }}` fora de lugar, `$json` vs `$json.body`); ver `n8n-expression-syntax`.
- **Code node** — ver `n8n-code-javascript` (`ERROR_PATTERNS.md`).

## Passo 3 — Reproduzir e corrigir o mínimo
1. Explique a causa raiz em uma frase antes de mexer em qualquer coisa.
2. Proponha a **correção mínima** — não refatore o fluxo inteiro no meio de um incidente.
3. Aplique via `n8n_update_partial_workflow` (MCP, cirúrgico) ou, no fallback CLI, `update-workflow` com o JSON completo corrigido.
4. Se a falha era transiente, adicione resiliência (`retryOnFail`, error branch) — ver `n8n-error-handling`.

## Passo 4 — Provar que resolveu
Re-execute o cenário (com permissão se houver efeitos colaterais) e confirme com `list-executions --workflow-id <ID> --limit 3` que a nova execução tem `status: success`. Nunca declare resolvido sem uma execução verde posterior à correção.

## Armadilhas conhecidas deste workspace
- **Trailing slash na URL do gateway de ferramentas** (`https://.../` → rota `//tools/invoke` → 404). Garanta que a URL base não tenha barra final antes de concatenar caminhos.
- Instância única hoje, mas se aparecer o tool `n8n_instances`, confira o alvo antes de ler/escrever (`n8n-multi-instance`).

---
*Parte da [Skills Library](../../README.md)*

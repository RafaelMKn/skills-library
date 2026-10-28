# Briefing do Revisor Independente /doit

Utilizado em `delegate_task(tasks=[{goal, context, output_schema}])`.

## goal

`Revisar a implementação integrada do documento <caminho do doc> contra os critérios de aceite.`

## context

```
Responda em PT-BR. Você atua como revisor independente e crítico de código (Peer Review).
Você NÃO é o autor da implementação e não deve ter viés de confirmação.

### Diretório da revisão
Diretório do worktree de integração:
<caminho absoluto do worktree de integração>

Diff a analisar: commit <base-sha>..HEAD

### O que verificar
1. Conformidade com a especificação original em <caminho do doc>. Todos os critérios de aceite foram atendidos?
2. Qualidade e Segurança: há regressões, race conditions, vazamento de credenciais/dados sensíveis ou caminhos de erro não tratados?
3. Cobertura de testes: as alterações críticas foram devidamente testadas?
4. Escopo: houve alterações indevidas ou arquivos desnecessários incluídos no diff?

### Como avaliar
- Rode a suíte de testes: `<comando de testes>`
- Rode o linter/typecheck: `<comando de lint/build>`
- Inspecione as linhas alteradas no git diff.

Se encontrar problemas, cite o arquivo exato e número da linha com o impacto técnico concreto.
```

## output_schema

```json
{
  "type": "object",
  "properties": {
    "veredito": {"type": "string", "enum": ["aprovado", "aprovado_com_ressalvas", "rejeitado"]},
    "resumo": {"type": "string"},
    "problemas_encontrados": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "arquivo": {"type": "string"},
          "linha": {"type": "integer"},
          "gravidade": {"type": "string", "enum": ["bloqueante", "importante", "sugestao"]},
          "descricao": {"type": "string"}
        },
        "required": ["arquivo", "gravidade", "descricao"]
      }
    }
  },
  "required": ["veredito", "resumo"]
}
```

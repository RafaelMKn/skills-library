# Briefing de Tarefa /doit

Utilizado em `delegate_task(tasks=[{goal, context, output_schema}])`.

## goal

`Implementar a tarefa <id> — <título> do documento <caminho do doc>`

## context

```
Responda em PT-BR. Você não tem acesso a ferramentas de interação direta com o usuário.
Qualquer dúvida bloqueante deve ser reportada no resultado para o orquestrador.

### Seu papel
Você é o implementador exclusivo da tarefa <id>. Seu trabalho é cirúrgico:
faça a alteração solicitada, teste rigorosamente e commite na sua branch local.

### Diretório de trabalho isolado
Você DEVE operar exclusivamente no diretório do seu worktree:
<caminho absoluto do worktree da tarefa>

Base Git de partida: commit <base-sha>
Branch atual da tarefa: <branch da tarefa>

### Escopo autorizado de escrita
Arquivos permitidos:
- <caminho 1>
- <caminho 2>

NÃO altere nem crie arquivos fora desta lista sem necessidade estrita.
NUNCA commite arquivos temporários, caches, logs ou dados confidenciais.

### O que implementar
<descrição objetiva da funcionalidade ou correção>

Critérios de aceite:
1. <critério 1>
2. <critério 2>

### Como verificar
Antes de finalizar, execute os comandos de validação:
- Testes: `<comando de teste específico>`
- Build / Typecheck: `<comando de build/lint>`

### Commit
Faça commits semânticos locais com mensagens descritivas:
`feat(<escopo>): <mensagem clara>`

NÃO faça push nem tente abrir Pull Requests.
```

## output_schema

```json
{
  "type": "object",
  "properties": {
    "status": {"type": "string", "enum": ["completed", "failed", "blocked"]},
    "commit_sha": {"type": "string"},
    "arquivos_alterados": {"type": "array", "items": {"type": "string"}},
    "testes_executados": {"type": "string"},
    "observacoes": {"type": "string"}
  },
  "required": ["status", "arquivos_alterados"]
}
```

# API REST do n8n: armadilhas de escrita e leitura

O que morde ao usar `n8n_api.py` / `/api/v1` direto, fora do MCP.

## `settings` precisa ser filtrado no PUT

`GET /workflows/<id>` devolve um `settings` com chaves que o **PUT rejeita**:

```
400 {"message": "request/body/settings must NOT have additional properties"}
```

`binaryMode` é uma dessas. Ler o workflow e devolvê-lo inteiro falha — filtre antes de enviar:

```python
SETTINGS_OK = {
    "executionOrder", "saveDataErrorExecution", "saveDataSuccessExecution",
    "saveManualExecutions", "saveExecutionProgress", "executionTimeout",
    "errorWorkflow", "timezone",
}
settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}
payload = {"name": w["name"], "nodes": w["nodes"],
           "connections": w["connections"], "settings": settings}
```

**Preserve `errorWorkflow`.** É o branch de erro do fluxo; descartá-lo no filtro faz a falha parar
de alertar sem que nada quebre visivelmente.

O PUT aceita apenas `name`, `nodes`, `connections`, `settings` — mandar `active`, `id`, `tags` ou
`createdAt` de volta também derruba a requisição. Prefira `n8n_update_partial_workflow` (MCP)
quando disponível: edição cirúrgica dispensa esse cuidado todo.

## Conferir `connections` depois de todo update

A API aceita o PUT e responde 200 mesmo quando uma conexão foi silenciosamente descartada.
Releia e imprima o grafo — validação passando não prova que o fio ficou lá:

```python
for k, v in w["connections"].items():
    print(k, "->", [[d["node"] for d in br] for br in v["main"]])
```

No nó `If`, a ordem de `main` é **[0] = true, [1] = false**. Trocar os dois ramos passa em qualquer
validação e inverte a lógica em produção.

## Copie o schema do nó de um fluxo que já roda

Ao inserir nó novo sem `get_node` disponível, leia um nó do mesmo tipo em fluxo vivo da própria
instância e espelhe `typeVersion` e a forma de `parameters`. Isso pega a versão real em uso (ex.:
`If` tv 2.2 com `conditions.options.version: 2`) em vez da que você lembra — `typeVersion` errado
valida como string e falha em runtime.

## Onde estão os dados de cada nó numa execução

```
data.resultData.runData.<Nome do No>[0].data.main[0][0].json   # itens de saida
data.resultData.error                                          # erro que parou o fluxo
data.resultData.error.context.request.body                     # o que foi enviado ao provedor
```

A resposta literal do provedor costuma estar em `messages` (lista de strings), não em
`errorDetails`. Ela nomeia o campo recusado — é o que separa "parâmetro errado" de "dado vazio".

## Executions: o filtro engana

`list-executions --status error` mostra só falhas e faz fluxo saudável parecer morto. Liste **sem
filtro** antes de concluir qualquer coisa: sucesso recente ao lado do erro muda o diagnóstico de
"quebrado" para "quebra em um subconjunto de rotas".

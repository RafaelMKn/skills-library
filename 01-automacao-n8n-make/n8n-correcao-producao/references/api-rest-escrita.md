# Escrever na instância n8n pela API REST (fallback sem MCP)

Receita para `PUT /workflows/<id>` via
`skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> update-workflow`.
Use quando o MCP não estiver disponível ou quando a edição for grande o bastante para não valer
passar o JSON inteiro pelo contexto.

## Sequência

```bash
# 1. exportar o estado atual
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> \
  get-workflow <ID> > scratch/<slug>.json

# 2. BACKUP antes de tocar em fluxo ativo
mkdir -p scratch/archive
cp scratch/<slug>.json \
   scratch/archive/<ID>--<slug>--<AAAA-MM-DD>-ANTES.json

# 3. patch programático (script em scratch/, nunca à mão no JSON)
python3 scratch/patch_<slug>.py

# 4. aplicar
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> \
  update-workflow <ID> scratch/<slug>-patched.json

# 5. reler da instância e conferir connections + nós novos
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> get-workflow <ID>
```

## O payload aceito é um subconjunto

A API pública aceita apenas `name`, `nodes`, `connections`, `settings`. Devolver o objeto do
`get-workflow` inteiro é rejeitado.

**`settings` é validado com `additionalProperties: false`.** Reenviar o `settings` como veio da
leitura quebra com:

```
400 request/body/settings must NOT have additional properties
```

porque o `get-workflow` traz chaves que a escrita não aceita (`binaryMode` é a que mais aparece).
Filtre para a lista branca — e **preserve `errorWorkflow`**, senão o update desliga em silêncio o
branch de erro do fluxo:

```python
SETTINGS_OK = {
    "executionOrder", "saveDataErrorExecution", "saveDataSuccessExecution",
    "saveManualExecutions", "saveExecutionProgress", "executionTimeout",
    "errorWorkflow", "timezone",
}
settings = {k: v for k, v in (w.get("settings") or {}).items() if k in SETTINGS_OK}

payload = {
    "name": w["name"],
    "nodes": w["nodes"],
    "connections": w["connections"],
    "settings": settings,
}
```

O `get-workflow` posterior ainda mostra `binaryMode` no `settings` — a instância preserva a chave
que a API não deixa escrever. Isso é esperado, não é regressão nem perda de configuração.

## Copie o schema de nó de um fluxo vivo, não da memória

Sem `get_node` do MCP, a fonte confiável de `typeVersion` e da forma dos parâmetros é outro fluxo
**da mesma instância** que já roda em produção:

```bash
python3 skills/n8n-manager/scripts/n8n_api.py --instance <PREFIXO> get-workflow <OUTRO_ID> > /tmp/w.json
python3 -c "
import json
w=json.load(open('/tmp/w.json'))
for n in w['nodes']:
    if n['type']=='n8n-nodes-base.if':
        print(n.get('typeVersion'), json.dumps(n['parameters'],ensure_ascii=False)[:400])
"
```

`If` v2.2 quer `conditions.options.version: 2`; v2.3 quer `version: 3`. Operador unário
(`notEmpty`, `exists`, `empty`) precisa de `singleValue: true`. Errar a forma valida como string e
não faz nada em runtime — o fluxo aceita o update e a condição simplesmente não avalia.

## Nó novo precisa de `id` e `name` únicos

O `name` é a chave usada em `connections`. Ao inserir um nó no meio de uma cadeia, reescreva a
conexão do nó **anterior** e crie a entrada do nó novo. Um `connections` que só ganha a entrada
nova deixa o caminho antigo intacto, passando por cima do guard que você acabou de inserir.

Para posicionar no canvas, derive de um nó vizinho em vez de cravar coordenada:

```python
pos = next(n["position"] for n in w["nodes"] if n["name"] == "HTTP Request4")
guarda["position"] = [pos[0] - 200, pos[1]]
erro["position"]   = [pos[0], pos[1] + 180]
```

## Idempotência do patch

Faça o script abortar quando o nó que ele insere já existir, para que rodar duas vezes não duplique
nó:

```python
if "Tem grupo cadastrado?" in {n["name"] for n in w["nodes"]}:
    print("ERRO: no de guarda ja existe — nada a fazer")
    sys.exit(1)
```

## Verificação obrigatória

`update-workflow` devolver `200` não prova que gravou o que você quis. Releia da instância e
imprima o mapa:

```python
print('active', w['active'], '| nodes', len(w['nodes']))
for k, v in w["connections"].items():
    print(' ', k, '->', [[d["node"] for d in br] for br in v["main"]])
```

Confira: contagem de nós, `active`, os nós novos com o `typeVersion` esperado, e que os branches do
`If` saem na ordem certa — **índice 0 = verdadeiro, índice 1 = falso**. Inverter isso manda o caso
de erro para o caminho de sucesso, e a validação não pega.

---
name: notion-publico-raspagem
description: Use ao raspar página pública do Notion sem login.
version: 1.0.0
author: Agent Skills Community
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [notion, raspagem, api-v3, extracao, wiki, PT-BR]
    category: productivity
    related_skills: [blocked-page-recovery]
---

# Raspar página pública do Notion

## When to Use

Use quando precisa do conteúdo de uma página pública do Notion e não tem token de integração nem export do usuário — típico de wiki de terceiro compartilhada por link. Use também quando `web_extract` devolve conteúdo vazio numa URL `notion.site` e o navegador headless está indisponível.

Não use quando o usuário tem acesso logado: ver a última seção.

Página pública do Notion não devolve conteúdo por fetch normal: o HTML vem vazio porque tudo é renderizado por JS. `web_extract` retorna string vazia e o navegador headless pode estar indisponível.

A saída é a **API v3 não-oficial**, que responde sem autenticação para página pública. Não precisa de token, não precisa que o usuário exporte nada.

## O endpoint

```
POST https://<subdominio>.notion.site/api/v3/loadCachedPageChunkV2
Content-Type: application/json

{"page": {"id": "<uuid-com-hifens>"},
 "limit": 200,
 "cursor": {"stack": []},
 "chunkNumber": 0,
 "verticalColumns": false}
```

O id vem da URL: `IA-Wiki-3599956f3dc981b1966dd926dbcf4feb` → insira hífens no formato 8-4-4-4-12.

Resposta: `recordMap.block` é um dict `id → {value: {value: {...}}}` (às vezes só um nível de `value` — trate os dois). Cada bloco tem `type`, `properties.title` (array de rich text) e `content` (ids dos filhos).

## A pegadinha que custa tempo

**O cap é 102 blocos por chamada, e `limit` não muda isso.** Testado com 200, 2000 e 100000: sempre 102. `cursor` volta `null`, então não há paginação por cursor. `syncRecordValues` devolve 403 e `loadPageChunk` (sem o V2) devolve os mesmos 102.

O jeito que funciona: pegar os ids que aparecem em `content` mas não vieram no `recordMap`, e **buscar cada um como se fosse raiz de página** (`{"page": {"id": <id-do-bloco>}}`). Um bloco-filho resolvido assim traz ele e os vizinhos dele.

Duas armadilhas nisso:

1. **Limite a BFS aos blocos alcançáveis da raiz.** Buscar um bloco traz vizinhos que criam novas pendências; resolvendo tudo cegamente a fila cresce sozinha (1391 → 386 → 379...) e nunca fecha. Só enfileire id que está em `content` de bloco já alcançado.
2. **Paralelize.** Serial, 1400 blocos passam do timeout da ferramenta. `ThreadPoolExecutor(max_workers=12)` resolve em segundos. Rode em `background=true` mesmo assim.

## Estrutura do script

```python
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor

HOST = "https://<sub>.notion.site"

def post(path, payload, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(HOST + path,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json",
                         "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if i == tries - 1: raise

def unwrap(w):
    # o wrapper tem 1 ou 2 níveis de 'value'
    v = w.get("value", w) if isinstance(w, dict) else None
    return v.get("value", v) if isinstance(v, dict) and "value" in v else v
```

Depois: BFS da raiz resolvendo em paralelo, e render de `properties.title` para markdown por `type` (`header`, `sub_header`, `bulleted_list`, `numbered_list`, `code`, `quote`, `divider`, `page` → subpágina).

**Grave incrementalmente, um arquivo por página.** Script que só escreve no fim perde tudo no timeout.

## Validar antes de confiar

Conte blocos não resolvidos e reporte por página. `0 nao resolvidos` em todas é o que autoriza dizer que a extração está completa. Página com 74 linhas quando o índice prometia 344 está truncada, não curta.

Cheque também se o número de fences de código é par, sinal de que bloco `code` não foi cortado no meio.

## Duas ciladas de shell nesse trabalho

- `pkill -f <script>.py` mata o próprio shell da ferramenta, porque o padrão casa com a linha de comando que contém o nome. Use `pgrep -af` para confirmar o PID e mate pelo PID.
- Nome de arquivo derivado de título do Notion vem com acento e espaço. Slugifique antes de gravar se o destino exige kebab-case sem acento.

## Quando não usar

Se o usuário tem acesso logado, exportar como Markdown do próprio Notion é mais rápido e 100% fiel — **pergunte primeiro**. A raspagem é para wiki de terceiro ou quando o export não é viável (usuário não consegue baixar página por página, por exemplo).

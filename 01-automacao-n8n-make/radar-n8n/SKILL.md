---
name: radar-n8n
description: Varre as instancias n8n e reporta erros por causa raiz.
version: 1.0.0
author: Agent Skills Community
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [n8n, Monitoramento, Observabilidade, Automacao, PT-BR]
    category: automation
    related_skills: [n8n-flow-debugger, n8n-error-handling]
---

# Radar n8n Skill

Varredura de saude das instancias n8n do workspace: conta erros e sucessos numa janela de tempo,
agrupa por fluxo, classifica a causa raiz a partir da mensagem do no que falhou e compara com a
coleta anterior para mostrar o que mudou. Produz um JSON e um painel HTML. Nao corrige nada —
diagnostico e priorizacao apenas; a correcao segue por `n8n-flow-debugger`.

## When to Use

Pedidos como "como estao os fluxos", "tem algo quebrado no n8n", "relatorio de erros",
"saude das instancias", ou a execucao agendada do cron **Radar n8n**. Tambem serve de primeiro
passo antes de depurar: mostra qual fluxo sangra mais e por que.

## Prerequisites

- Workspace do projeto com `.env` na raiz preenchido (ou definido em `WORKSPACE_DIR`).
- Pares `N8N_<INSTANCIA>_API_URL` e `N8N_<INSTANCIA>_API_KEY` — instancias com par incompleto sao
  ignoradas em silencio. Ex.: `PESSOAL`, `PROD`, `CRM`, `BACKOFFICE`.
- Somente stdlib do Python 3. Nenhuma dependencia externa, nenhum MCP.

## How to Run

Duas etapas, sempre nessa ordem. Rode pelo `terminal`, a partir da raiz do workspace:

```bash
python3 skills/radar-n8n/scripts/radar_n8n.py --hours 24 --json-out /tmp/radar.json
python3 skills/radar-n8n/scripts/tarefas.py --radar /tmp/radar.json --out /tmp/tarefas.json
python3 skills/radar-n8n/scripts/gerar_painel.py /tmp/radar.json \
    --out rotinas/saude-n8n.html --historico ~/.hermes/radar-n8n/historico.jsonl \
    --tarefas /tmp/tarefas.json
```

A coleta completa leva de 1 a 4 minutos (instâncias movimentadas como CRM podem ter milhares de execucoes por dia) — use
`timeout` de pelo menos 420s. Entregue o painel ao usuario com uma linha `::preview{file="..."}`
sozinha, e resuma em texto o que mudou.

O passo do `tarefas.py` cruza cada fluxo com erro contra `tarefas/` e responde a pergunta que
importa: **isso ja tem tarefa aberta, ha quantos dias?** Fluxo sangrando sem tarefa aberta e
achado novo; fluxo com tarefa parada ha semanas e problema de execucao, nao de deteccao.

## Quick Reference

| Flag do `radar_n8n.py` | Efeito |
|---|---|
| `--hours N` | Janela em horas (padrao 24) |
| `--instance NOME` | Limita a uma instancia; repetivel |
| `--json-out ARQ` | Grava o JSON em vez de imprimir |
| `--state-dir DIR` | Onde vive o snapshot do diff (padrao `~/.hermes/radar-n8n`) |
| `--timeout N` | Timeout por request (padrao 45s) |

| Flag do `tarefas.py` | Efeito |
|---|---|
| `--radar ARQ` | Cruza os fluxos com erro contra as tarefas abertas |
| `--wip` | So tarefas `aberta`/`fazendo` |
| `--parado-ha N` | Com `--wip`: so as sem atividade ha N dias ou mais |
| `--out ARQ` | Grava o JSON |

Para ler a saida das rotinas agendadas (que rodam com `deliver: local` e nao entregam em canal
nenhum): `python3 skills/radar-n8n/scripts/briefing.py` monta `rotinas/briefing.html` com o ultimo
relatorio de cada cron; `--texto` imprime no terminal.

Confianca do cruzamento: **alta** = a tarefa cita o ID do workflow ou o nome exato do fluxo (prova);
**media** = termos distintivos em comum mais a instancia citada (indicio, confira antes de afirmar).

| Causa classificada | Severidade | Acao tipica |
|---|---|---|
| `credencial-nao-descriptografavel` | critico | `N8N_ENCRYPTION_KEY` divergente — recriar a credencial |
| `credencial-invalida` | critico | Token expirado/sem escopo |
| `erro-de-banco` | critico | Constraint ou schema divergente |
| `dns-nao-resolve` | alto | Host ausente na rede do container (ex.: `redis`) |
| `rede-indisponivel` | alto | Endpoint fora do ar |
| `erro-no-servico-externo` | alto | Falha 5xx do provedor — retry + branch de erro |
| `rate-limit` | medio | Backoff ou menos concorrencia |
| `dado-inesperado` / `expressao-quebrada` / `parsing` | medio | Validar payload antes do no |
| `nao-classificado` | baixo | Abrir a execucao e inspecionar o no |

## Procedure

1. **Colete.** Rode `radar_n8n.py`. Se a saida trouxer `erro_fatal`, o `.env` nao tem nenhum par
   completo — avise e pare, nao invente numero.
2. **Gere o painel.** Rode `gerar_painel.py` sobre o JSON, apontando o `--historico` para o
   `historico.jsonl` do `--state-dir`.
3. **Leia o `diff` primeiro.** Ele e a noticia: `novos` (fluxo que nao errava e passou a errar),
   `agravados` (subiu >50% e >=5 erros), `resolvidos`, `melhorados`. Numero absoluto grande e
   repetido todo dia nao e novidade — o que mudou e.
4. **Priorize por sangramento, nao por volume.** `sucessos: 0` significa nenhuma execucao
   bem-sucedida registrada na janela, nao prova descarte de eventos: confira filas e persistencia
   antes de afirmar perda. Priorize a falta de entrega, considerando producao e recuperabilidade.
5. **Reporte em PT-BR**, ordenado por severidade, sempre com: instancia, nome e ID do fluxo, causa
   classificada, no que falhou e a acao sugerida. Entregue o painel com `::preview`.
6. **Nao corrija nada aqui.** Se o usuario pedir correcao, carregue `n8n-flow-debugger`.

## Pitfalls

- **Nao use `retencao_mais_antiga` como prova de truncamento.** No coletor atual, esse campo e
  o menor `startedAt` das execucoes JA filtradas pela janela, nao o limite real de retencao.
  Estar perto do inicio das 24h e esperado. So declare contagem como piso ou atribua queda de
  volume a truncamento com evidencia independente de retencao/paginacao; caso contrario, registre
  a lacuna. Janelas longas exigem essa verificacao, sobretudo em instâncias de alto volume.
- **A API do n8n nao filtra execucao por data.** O script pagina e corta em Python; janela muito
  larga em instancia movimentada estoura `MAX_PAGES` e subnotifica.
- **A listagem de execucoes nao traz o nome do fluxo** — vem de uma chamada separada a
  `/workflows`. Se essa chamada falhar, o campo `nome` fica vazio e sobra so o ID; nao trate isso
  como fluxo deletado.
- **Um erro por fluxo e amostrado com `includeData=true`.** A causa classificada vale para aquela
  amostra; fluxo com modos de falha distintos aparece com apenas um deles.
- **`PESSOAL` pode hospedar producao de clientes** (`[CLIENTE PRODUÇÃO]`). Taxa baixa ali nao
  significa que erro nenhum importa.
- **Nunca imprima valores do `.env`** no relatorio, nem em mensagem de erro.

## Verification

- A coleta funcionou se `total.execucoes > 0` e nenhuma instancia trouxe `falha` preenchida.
- Instancia com `falha` (`HTTP 401`, timeout) significa credencial ou rede — reporte como problema
  de coleta, separado dos erros de fluxo, e jamais como "zero erros".
- O painel funcionou se o HTML existe e abre com o placar; a serie temporal so aparece a partir da
  segunda coleta.

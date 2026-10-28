---
name: hermes-roteamento-modelos
description: "Use when changing Hermes models, effort or fallback."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, modelos, delegacao, fallback, reasoning, config, PT-BR]
    related_skills: [hermes-agent, hermes-context-tuning]
---

# Roteamento de modelos no Hermes

Trocar **qual modelo/provider e qual esforço** o Hermes usa: agente principal, subagentes
(`delegation.*`), fallback e MoA. O usuário troca isso com frequência ("deixa a delegação em X e
Y"); o objetivo é acertar na primeira, com probe real e sem editar o `config.yaml` na mão.

## When to Use

"Deixa a delegação em X", "troca o modelo principal", "coloca fallback Y", "sobe o esforço dos
subagentes", ou antes de afirmar qual modelo os workers usam.

Também quando `/model` no Slack, WhatsApp ou Telegram "não muda o provedor": siga
`references/gateway-model-override.md`. Na maioria das vezes é divergência de chave de sessão, não
falha da troca.

## Modelo mental (lido no source; confira de novo se o Hermes foi atualizado)

- **Um primário por escopo.** `delegation.provider` + `delegation.model` valem para todo
  subagente; `delegate_task` não aceita modelo por chamada. Pedido de "dois modelos" para delegação
  vira primário + `delegation.fallback_providers` — diga isso na resposta e ofereça outro desenho
  se ele queria dividir tarefas entre os dois.
- **Filho fixado não herda fallback do pai.** Com provider/model de delegação setado, o filho só
  tem fallback se `delegation.fallback_providers` for declarado; `[]` desliga; `null` + filho não
  fixado = herda a cadeia do pai (`hermes_cli/fallback_config.py::scoped_fallback_chain`).
- **Esforço do fallback NÃO vem de `delegation.reasoning_effort`.** Na ativação de fallback o
  esforço é re-resolvido por `hermes_constants.resolve_reasoning_config`: override por modelo
  (`agent.reasoning_overrides`) > `agent.reasoning_effort` global. Sem override, o fallback cai no
  esforço global (geralmente `medium`).
- **Modelo por tipo de tarefa = troca por lote.** `_load_config()` é relido em cada `delegate_task`
  (`tools/delegate_tool.py:524`, cache invalidado pela assinatura do arquivo). Assim, `hermes config
  set delegation.provider/model` entre dois fan-outs muda o modelo só dos filhos seguintes. Não dá para
  misturar modelos dentro de um mesmo `tasks=[...]`. A regra de qual modelo usar para cada tipo de
  tarefa fica na política de delegação do seu workspace.
- `agent.reasoning_overrides` é **global**: vale também para o agente principal e MoA se usarem
  aquele modelo. Avise o usuário desse efeito colateral.
- Níveis: ultra | max | xhigh | high | medium | low | minimal | none (vazio = herda).

## Procedimento

1. **Estado atual** (não confie em memória/nota antiga — a config muda entre sessões):
   ```bash
   grep -n -A12 '^delegation' ~/.hermes/config.yaml
   grep -n 'reasoning_effort\|reasoning_overrides\|fallback_providers' ~/.hermes/config.yaml
   hermes auth list
   ```
2. **Probe real de cada modelo + esforço antes de gravar:**
   ```bash
   hermes chat -q "Responda só: ok" --oneshot -Q --provider <prov> -m <modelo> --reasoning <nivel>
   ```
   - Sem `-Q` a saída só traz o rodapé da sessão, sem a resposta.
   - `hermes auth status <prov>` pode dizer "logged out" e o provider responder (ex.: Anthropic
     usando a credencial do Claude Code). O probe decide, não o status.
   - Se a rota exigida estiver bloqueada e a regra for sem fallback, peça autorização antes de
     testar/substituir por outro modelo. Autorização "nesta rodada" é exceção temporária: registre
     provider/model/esforço/cadeia anteriores e a duração da exceção no estado da tarefa. Faça o
     probe da alternativa autorizada antes do set e confirme depois o modelo do filho vivo;
     resposta CLI `ok` não comprova que o worker herdou a rota.
   - ID segue o catálogo do provider: Anthropic direto usa hífen (`claude-sonnet-5-5`), OpenRouter
     usa `anthropic/claude-sonnet-5.5`. Catálogo em `hermes_cli/models_catalog_static.py`.
3. **Gravar só via `hermes config set`** (config é protegido contra patch/write; o valor é
   parseado como YAML, então JSON inline funciona):
   ```bash
   hermes config set delegation.provider <prov>
   hermes config set delegation.model <modelo>
   hermes config set delegation.reasoning_effort <nivel>
   hermes config set delegation.fallback_providers '[{"provider": "<prov>", "model": "<modelo>"}]'
   hermes config set agent.reasoning_overrides '{"<modelo-fallback>": "<nivel>"}'
   ```
   O set substitui o dict/lista inteiro — leia o valor atual e mescle antes de sobrescrever.
4. **Verificar a resolução** com o Python do venv do Hermes (o `python3` do sistema não importa
   `hermes_cli`): `cd ~/.hermes/hermes-agent && PYTHONPATH=$PWD ./venv/bin/python
   ~/.hermes/skills/hermes-roteamento-modelos/scripts/verificar-roteamento.py <modelo> [...]`. Sem o
   `PYTHONPATH` o import falha em `hermes_yaml`, um módulo solto na raiz do repo. O script imprime a
   delegação, a cadeia de fallback do filho e o esforço efetivo de cada modelo.
5. **Substituir workers travados quando a troca é uma recuperação:** se o pedido vier acompanhado de erro, travamento ou "refazer a execução", não encerre após mudar a config. Consulte `delegate_task(action='list')`, solicite `stop` aos workers afetados e relance as tarefas na rota nova. `interrupt_requested` não confirma término: use worktrees/diretórios novos para não concorrer com ferramentas ainda em voo. Preserve commits e snapshots dos arquivos parciais com manifesto de hashes; o novo implementador revisa o snapshot, não depende do diretório antigo em mutação. Atualize IDs, paths e plano de restauração no estado da tarefa. Se a troca não pedir retomada nem houver falha, mantenha os workers saudáveis e explique que só os próximos herdam a rota.
6. **Conferir o que o probe usou de fato:** `sessions.model_config` no `~/.hermes/state.db`
   (via `sqlite3` da stdlib do Python) mostra provider, api_mode e `reasoning_config` efetivos.
7. **Relatar** papel, provider/modelo e esforço em linhas curtas; em canais de chat sem tabela renderizada, use listas. Separe o que foi provado por probe do
   que ficou só por leitura de código (troca para fallback não dá para forçar sem um 429 real).
   Registre exceções temporárias apenas no estado da tarefa, com plano de restauração após o
   último lote; não substitua a preferência permanente em memória por uma autorização de uma rodada.
   Atualize memória somente se o usuário mudar a política permanente. Ao restaurar, confira se
   outra decisão posterior substituiu a rota, para não desfazê-la.

## Restrições de acesso ao modelo

- Allowlist autoriza entrada; não limita modelo nem ferramenta. Antes de liberar acesso, valide o escopo restrito e teste o uso permitido e a recusa do caminho proibido.
- Modelo padrão configurado não prova restrição: verifique também comandos de troca (`/model`), fallback e ferramentas que possam contornar a restrição.
- Em runtime de CLI externa, a lista de ferramentas do Hermes pode não controlar as ferramentas internas do subprocesso. Verifique a fronteira no runtime instalado; sandbox, prompt ou lista de ferramentas do host não são prova de isolamento.
- Antes de aprovar pareamento de mensagens, confira o identificador do remetente com `hermes pairing list` contra o alvo autorizado; nome exibido ou semelhança numérica não provam identidade. Depois, direcione o identificador a um perfil restrito em `gateway.profile_routes`: aprovar entrada sem rota pode entregar a conversa ao perfil do dono.
- Não declare restrição concluída só porque a configuração foi salva; sem teste de recusa, reporte como validação pendente.

## Pitfalls

- **Nome falado ≠ ID do catálogo.** "gpt astra low", "gpt 6.1 sol": resolva o ID antes do probe com
  `grep -rhoE '<família>[a-z0-9.-]*' ~/.hermes/hermes-agent/hermes_cli/*.py | sort -u`. Modelos da família Sol/Astra/Terra/Luna
  (ex.: "sol 6.1" = `gpt-6.1-sol`, "gpt-6-sol") pertencem a um provider de assinatura (ex.: `openai-codex`),
  não a `openai` direto. O probe pode aceitar um ID que o catálogo estático não lista: confirme em `sessions.model` do `state.db`
  o que ele usou (passo 5). A palavra de esforço no pedido ("low") vai para `delegation.reasoning_effort`, não para o ID.
- **Setar sempre provider e model em conjunto na delegação.** `delegation.model` não atualiza `delegation.provider`
  automaticamente: trocar o modelo sem trocar o provedor faz o Hermes tentar chamar o modelo novo na API do provedor antigo
  (ex.: `gpt-6.1-sol` sob `anthropic`), gerando erro de modelo não encontrado no dispatch. Rode sempre
  `hermes config set delegation.model <m>` junto com `hermes config set delegation.provider <p>`.
- **Troca de `delegation.model` vale para TODA delegação seguinte**, não só para o lote pedido: diga isso ao
  confirmar e ofereça voltar ao modelo anterior. Filhos já criados conservam o modelo original; preserve
  o trabalho em curso, salvo pedido explícito para interromper e reexecutar. Se a troca substituir uma
  exceção temporária registrada em outra tarefa, atualize seu plano de restauração para não desfazer
  a nova decisão do usuário ao encerrar aquela tarefa.
- **Setar só `delegation.reasoning_effort` e achar que o fallback herda** — não herda; sem
  `reasoning_overrides` o fallback roda no esforço global.
- **Afirmar provider indisponível pelo `auth status`** sem probe — falso negativo comum.
- **Aviso "previous `hermes update` did not restart gateways"** aparece em todo comando; é ruído
  para esta tarefa, não bloqueio. Filtre na saída.

## Verification

- Cada modelo configurado respondeu a um probe com o esforço pedido.
- `verificar-roteamento.py` mostra a cadeia e os esforços esperados; o esforço do agente principal
  não mudou sem querer.
- Nenhuma edição direta no `config.yaml`; política permanente e exceção temporária registradas no
  escopo correto, com plano de restauração quando aplicável.

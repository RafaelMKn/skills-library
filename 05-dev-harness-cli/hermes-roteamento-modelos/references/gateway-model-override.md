# `/model` no gateway (Slack, WhatsApp, Telegram) que "não pega"

Sintoma: o usuário manda `/model` pela plataforma de mensagem, o comando responde, mas a próxima
mensagem continua rodando no modelo padrão do config.

## Modelo mental

- `/model` sem `--global` grava um override **por chave de sessão**. Fica em memória e também no
  session store, e é recarregado depois de um restart (aparece no log como `Rehydrated persisted /model override for session=<chave>`).
- O turno só aplica o override se a chave do turno for **idêntica** à chave onde o `/model` gravou.
- Fonte do override: `gateway/slash_commands_model.py` (grava) e `gateway/run_agent_cache.py`
  (`_rehydrate_session_model_override` / `_apply_session_model_override`, que leem).

## Diagnóstico (só leitura, ~2 min)

```bash
cd ~/.hermes/logs
grep -h "Rehydrated persisted /model override" gateway.log | tail      # chave onde o override está
grep -hoE "session=agent:main:<plataforma>[^ ]*" gateway.log | sort | uniq -c | tail  # chaves que os turnos usam
grep -h "inbound message: platform=<plataforma>" gateway.log | tail
```

Compare as chaves. Se o override estiver em `…:dm:<team>:<canal>` e os turnos rodarem em
`…:dm:<team>:<canal>:<ts>`, o problema é divergência de chave, não falha do `/model`. Depois
confira no `agent.log` qual provider/modelo o turno usou de fato (um 429 do provider padrão logo
em seguida confirma que o override foi ignorado).

## Slack DM: causa conhecida

- `platforms.slack.extra.dm_top_level_threads_as_sessions` vem **ligado por padrão**: cada
  mensagem de topo da DM vira uma sessão com o `ts` dela na chave (`_session_thread_ts` em
  `plugins/platforms/slack/adapter.py`).
- O slash command `/model` costuma chegar sem `thread_ts`/`message_ts` (`_slash_thread_id`). Por
  isso grava na chave da DM sem `ts`, que nenhuma mensagem de topo vai ler.

Soluções, da recomendada para a mais ampla:
1. `hermes config set platforms.slack.extra.dm_top_level_threads_as_sessions false` + `/restart`
   (uma sessão por DM; o contexto acumula e a compressão cuida dele). Mexe no config, então
   confirme com o usuário antes.
2. Sem mexer no config: responder dentro da thread e mandar `/model …` como texto ali.
3. `/model <modelo> --global`: muda o padrão de todas as plataformas.

## Pitfalls

- Não conclua "/model está quebrado" só porque a resposta veio no modelo errado. Compare as
  chaves primeiro, porque o override costuma existir e estar na chave errada.
- Divergência de chave + provider padrão sem fallback e batendo no limite (429) faz parecer que
  "o bot parou". Aponte as duas causas na resposta.
- Confira a branch do checkout (`git -C ~/.hermes/hermes-agent status -sb`) antes de afirmar que
  é bug do upstream. Fork ou feature branch pode ter divergido da `main`.

# RPC local do Desktop

## Descoberta e autenticação

1. Localize o processo `hermes serve` e seu listener loopback a partir dos processos/portas reais, sem assumir PID ou porta fixa.
2. Consulte os contratos em `tui_gateway/contracts/` e os handlers de sessão antes de enviar. O endpoint do Desktop é `/api/ws`, com frames JSON-RPC.
3. Em backend loopback com autenticação legada, o processo pode receber `HERMES_DASHBOARD_SESSION_TOKEN`. Quando presente, leia somente essa variável do ambiente do processo identificado, mantendo-a em memória, e conecte a `ws://127.0.0.1:<porta>/api/ws?token=<token>`. Nunca imprima token, URL autenticada ou ambiente completo. Não use isso para contornar autenticação gated, que exige o fluxo autorizado de tickets.
4. Um cliente Node com `WebSocket` nativo evita instalar dependências Python. Use timeout finito; interprete frames separados por newline e filtre a resposta pelo `id` da chamada. Não despeje todo o histórico ou feed de eventos.

## Identificar e enviar

- `session.list` lista conversas persistidas; não fornece necessariamente o identificador vivo exigido para steering.
- Chame `session.active_list` com `{}` e filtre pelo título/projeto esperado. O resultado associa `id` vivo, `session_key` persistido e `status`.
- Para execução ocupada e steering suportado:
  ```json
  {"jsonrpc":"2.0","id":2,"method":"session.steer","params":{"session_id":"<id-vivo>","text":"<recado>"}}
  ```
- Para execução ociosa:
  ```json
  {"jsonrpc":"2.0","id":3,"method":"prompt.submit","params":{"session_id":"<id-vivo>","text":"<recado>","queued":true}}
  ```
  `queued:true` preserva a intenção de enfileirar se a sessão ficar ocupada entre descoberta e envio. Confirme esse contrato na versão instalada.
- Ao receber `session not found`, refaça o mapeamento do ID vivo antes de tentar de novo. Não crie ou retome sessão duplicada para mascarar o erro.

## Abrir novo chat com modelo escolhido

1. Consulte `model.options` no perfil alvo e confirme o identificador exato do modelo e provider autenticado; nomes amigáveis não substituem IDs do inventário.
2. Confira `SessionCreateParams` e `PromptSubmitParams` nos contratos instalados. Envie `session.create` com modelo/provider explícitos, workspace correto, `hidden:false`, `close_on_disconnect:false` e, quando suportado, `follow_profile_config:false`. Isso fixa a escolha no chat sem modificar o padrão global.
3. **Mantenha o mesmo WebSocket aberto entre `session.create` e `prompt.submit`.** Use o `session_id` da resposta para enviar o primeiro turno nessa conexão; a criação lazy pode não persistir e ser removida na desconexão antes do primeiro prompt. Um cliente que encerra após cada ACK não serve para essa sequência.
4. Se perder a conexão antes do envio, consulte `session.active_list` e o armazenamento read-only antes de recriar. Recrie somente após comprovar que não existe conversa/mensagem persistida para a missão; não replique um pedido já aceito.
5. Confira `user_row_id`, conteúdo integral e ID persistido retornado por `session.create`. Leia modelo/provider da configuração da sessão e confirme `status:working` ou a atividade real; não trate configuração solicitada como configuração comprovada.
6. Use o título efetivamente persistido para indicar onde encontrar o chat. O título fornecido na criação pode ser substituído pelo título derivado do primeiro prompt. Criação visível na lista não comprova que a interface selecionou ou focou esse chat.

## Novo chat com `/goal`

1. Prepare um briefing autocontido, com evidências, artefatos reutilizáveis, critérios de pronto, exclusões e limites de escrita externa. Inclua seu conteúdo no primeiro turno; não dependa apenas de um arquivo temporário ou de memória do chat de origem.
2. Na mesma conexão usada para criar a sessão, chame `command.dispatch` com `name:"goal"`, `arg` contendo o objetivo e `session_id` vivo. Consulte `CommandDispatchParams` na versão instalada antes de usar a receita.
3. Se a resposta tiver `type:"send"`, envie `message` junto ao briefing por `prompt.submit`. O dispatch configura o objetivo, mas essa diretiva requer o envio do turno para iniciar o trabalho. Não execute o dispatch novamente para cumprir a diretiva, pois isso reconfigura o objetivo em vez de enviar a missão.
4. Leia `session.control.read` e confira `control.goal.status:"active"` e o texto do objetivo. Confirme separadamente o ACK do prompt, a mensagem integral persistida e a atividade da sessão: objetivo ativo e execução iniciada são provas distintas.
5. Para criação retry-safe, use `idempotency_key` estável para a missão quando o contrato suportar. Em falha de transporte, verifique o destino antes de reenviar o prompt; idempotência da criação não deduplica mensagens.
6. Na resposta ao usuário, entregue o link `@session:<perfil>/<id-persistido>`, modelo confirmado e estado observado. Informe onde o relatório final será entregue; não confunda o encaminhamento com conclusão da implementação.

## Verificação e deduplicação

Quando `prompt.submit` retornar `user_row_id`, leia esse registro na base da sessão correta em modo read-only e confira `role`, `session_id` e conteúdo. Nunca injete recados escrevendo diretamente no SQLite: isso não acorda o agente e pula o protocolo normal.

`status: streaming` confirma início de processamento; `queued` confirma apenas aceitação. Em falha de transporte após envio, procure primeiro a mensagem persistida antes de reenviar, evitando duplicidade. Não declare implementação concluída com base no ACK.

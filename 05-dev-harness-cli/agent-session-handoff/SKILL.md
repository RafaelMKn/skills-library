---
name: agent-session-handoff
description: "Use when forwarding instructions to a live agent session."
metadata:
  hermes:
    related_skills: [hermes-agent, inspecting-hermes-desktop-dom]
---

# Encaminhar instruções entre sessões

Use quando o usuário pedir para mandar texto, imagem ou requisitos para uma execução já aberta, ou abrir um novo chat com um modelo específico e encaminhar uma missão. Preserve a distinção: encaminhe para a execução existente quando ela for o alvo; crie outra conversa somente quando o pedido exigir um novo chat. Não substitua um chat solicitado por subagente nem implemente em paralelo no mesmo projeto.

Para um novo chat, consulte o inventário autenticado de modelos, fixe modelo/provider somente na sessão e confirme a configuração persistida. Crie a sessão e envie o primeiro pedido na mesma conexão RPC; só declare início após ACK e leitura da mensagem no destino. Uma sessão criada sem primeiro turno pode não sobreviver à desconexão, mesmo com `close_on_disconnect:false`. Não altere o modelo global para atender um pedido de chat separado.

## Procedimento

1. Leia `hermes-agent` para o mecanismo atual. Identifique a execução por título, projeto e atividade recente. Esclareça apenas se houver dois alvos igualmente plausíveis.
2. Se houver imagem, use visão e transcreva os requisitos visíveis. Inclua o caminho absoluto do original. Separe recomendações próprias do conteúdo encaminhado; um caminho não equivale a anexo visual consumido pelo destinatário.
3. Descubra o backend vivo e consulte `session.active_list`. Use o **id vivo** para RPC; `session_key` identifica a conversa persistida. Não passe o ID do banco como se fosse o ID vivo: isso pode retornar `session not found` mesmo com a conversa aberta.
4. Preserve a execução: para sessão ocupada, use steering suportado sem interromper; para sessão ociosa, envie novo turno com `prompt.submit`. Consulte o contrato local antes da chamada. Não reinicie o aplicativo nem retome uma segunda cópia da conversa para enviar um recado.
5. Envie mensagem autocontida com origem do pedido, requisitos, referência e limites. Ao encaminhar implementação após auditoria, inclua o artefato/branch já existente, testes efetivamente executados, estado instalado versus preparado, caminho mínimo de entrega e exclusões de escopo; não force o destinatário a reconstruir o diagnóstico relendo chats inteiros. Preserve o escopo atual e não transforme encaminhamento em autorização de deploy. Se o usuário pedir `/goal`, ative o mecanismo real de objetivo e leia seu estado de volta; mencionar `/goal` no briefing não o ativa. Se pedir aviso ao terminar, atribua ao destino um relato final de resultado verificado e pendências exatas para funcionamento completo; não prometa uma notificação nesta conversa sem configurar um mecanismo que a entregue.
6. Verifique o ACK e leia de volta o registro exato da mensagem na conversa destino, quando persistido. Diferencie aceitação na fila, início de processamento e trabalho concluído.
7. Responda em poucas linhas: destinatário, conteúdo encaminhado e estado comprovado. Não espere a implementação inteira quando o pedido foi apenas encaminhar.

## Receita técnica

Consulte [references/desktop-session-rpc.md](references/desktop-session-rpc.md) para encaminhar pelo backend local do Hermes Desktop quando não houver ferramenta direta. CDP do renderer não é pré-requisito para RPC do backend.

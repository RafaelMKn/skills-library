---
name: whatsapp-baileys-local
description: Use when sending WhatsApp via the local Baileys bench.
version: 1.0.0
author: "<autor>"
license: MIT
metadata:
  hermes:
    tags: [whatsapp, baileys, contatos, envio, PT-BR]
    related_skills: [composio-apps]
---

# WhatsApp pelo Baileys local

Canal padrão do Hermes para mandar WhatsApp em nome do operador. Projeto em
`<workspace>/baileys-local` (README completo lá — leia antes de mexer em algo além do
envio). A sessão pareada fica em `auth/` e persiste entre reinícios.

## When to Use

"Fala com <pessoa> via baileys/WhatsApp", "avisa o <fulano>", "manda mensagem para...".
Não serve para disparo em massa nem para ler conversas (a bancada não lê histórico).

## Procedure

1. **Estado do serviço** (token em `/run/user/$UID/baileys-local.token`, nunca imprima o valor):
   ```bash
   T=$(cat /run/user/$(id -u)/baileys-local.token)
   curl -s -H "Authorization: Bearer $T" http://<ip>:8788/status
   ```
   Sem token / sem resposta na 8788 = serviço parado (não tem autostart nem restart). Subir é o
   comando documentado: `systemctl --user start baileys-local.service`, espere ~5 s e confira
   `connected: true`. Não toque em `auth/`. Se `qrAvailable: true`, a sessão caiu e precisa de
   scan humano do operador — pare e peça.
2. **Número da pessoa:** só use o que o operador informou ou o que está em `~/.hermes/contacts/`.
   Nunca deduza número de README, JSON de fluxo ou ClickUp.
3. **Resolver antes de enviar:** `POST /resolve` com `{"recipient":"<telefone>"}` devolve
   `digits`/`jid`; falha se o número não tem WhatsApp. Ao relatar, mascare o número.
4. **Redigir o texto** (regras abaixo) e, em destinatário novo ou mensagem em nome de cliente,
   mostre o rascunho antes de enviar.
5. **Enviar:** `POST /send` com `{requestId,recipient,text}`; `requestId` único por mensagem
   (`[A-Za-z0-9_-]`, ex.: `<cliente>-<pessoa>-<assunto>-<AAAAMMDD>`). Mesmo ID + mesmo payload
   devolve o existente sem redisparar; ID novo duplica a mensagem — por isso, quando o operador disser
   "não reenvie", não gere ID novo.
6. **Acompanhar:** `GET /operations/<requestId>`. `accepted` + `ack: null` significa só que o
   servidor do WhatsApp aceitou — não é entrega. Entrega = `ack` delivered; leitura = read. Relate
   exatamente isso, sem dizer "entregue" antes do ack.
7. **Cadastrar o contato** (regra do operador para todo contato novo acionado por WhatsApp) em
   `~/.hermes/contacts/<slug>.json`, chmod 0644, no formato do existente: `name`, `role`,
   `phone_source`, `phone_digits`, `whatsapp_jid`, `source` (quem informou, quando, requestId
   do envio); `notas` para preferências de tom. Não invente campos como `github` sem dado.

## Como escrever a mensagem

- A mensagem sai **do número do operador**: não abra com "aqui é <nome>" nem se apresente —
  soa estranho para quem recebe. Comece direto pelo assunto, com o nome do destinatário.
- Peça uma ação concreta e curta (onde clicar, quanto leva), diga o efeito se não for feito.
- Sem credencial, token, link com segredo, dado de paciente/lead. Nome de fluxo, instância e
  mensagem de erro técnica podem ir.
- Cite só o que depende da pessoa; o que o time resolve sozinho vai numa frase final, não como
  pedido.
- `<cliente>` (contato `<pessoa>`, CEO) é projeto de cliente: nunca assine ou cite a empresa do operador.

## Pitfalls

- **Não confundir com o WhatsApp Gateway nativo do Hermes:** esta skill cobre apenas a bancada local de envio pontual (`baileys-local.service`, porta 8788, `<workspace>/baileys-local/auth/`). Pedidos para gerenciar, desconectar ou reconfigurar o bot/canal de WhatsApp do Hermes tratam do gateway nativo (`~/.hermes/whatsapp/session/`, bridge na porta 3000, comando `hermes whatsapp`).
- **Nunca reenvie para "garantir"**: sem ack não prova falha, e ID novo duplica. Consulte
  `/operations` antes de qualquer decisão.
- **Texto dado pelo agente é do operador aos olhos do destinatário.** Qualquer correção de tom
  que ele pedir depois do envio vira nota em `contacts/<slug>.json` e regra aqui, não reenvio.
- A unit systemd não reinicia sozinha: depois de reboot, repita o passo 1.

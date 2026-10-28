# Acesso a subcontas e custo de ações premium

## Provar acesso a uma subconta (antes de prometer inspeção)

1. `composio connections list` → procurar `highlevel_mcp` (ACTIVE/EXPIRED). Cada conexão é presa a UMA
   subconta (location); não há troca de location na mesma conexão.
2. `composio execute HIGHLEVEL_MCP_LOCATIONS_GET_LOCATION --account <word_id> -d '{}'` → ler `name` e `id`.
   Se não for a subconta pedida, não há acesso por esse caminho; não testar outras tools esperando milagre.
   Conexão EXPIRED: não dá para saber de qual subconta era sem reconectar.
3. Toolkits `highlevel_location` / `highlevel_agency` existem no Composio mas exigem conexão própria.
4. Caminhos para ganhar acesso, oferecer ao usuário nesta ordem de esforço:
   - nova conexão `composio link highlevel_mcp --alias <cliente>` aprovada por login que enxergue a subconta;
   - Private Integration Token da subconta, só escopos de leitura;
   - login de equipe no cofre (`browser_vault save_login`) — único caminho que mostra o builder visual
     (selo premium, To-Do List, configuração de nós). API/MCP leem contatos, pipelines e campos, não o editor.
5. Navegador: checar `app.gohighlevel.com`; tela de login = sem sessão. Nunca digitar senha; usar o cofre.

## Custo de ações premium (Workflow Premium Features)

- Premium: Google Sheets, Inbound Webhook (trigger), Custom Webhook, Slack, Marketplace/LC Apps [S6, S8].
- Cobrança: 100 execuções grátis por subconta, depois US$ 0,01/execução, ou plano Workflow Pro; a agência
  pode refaturar ao cliente [S6, S7]. Preço é volátil: reconsultar S7 antes de citar valor.
- Webhook padrão (Outbound) não aparece na lista premium de S6 e S9 não cita cobrança → indício de gratuidade,
  não prova. Confirmar na conta: ação sem selo premium no builder e contador de execuções premium parado após
  um disparo de teste.
- Rota sem custo para planilha: Webhook (Outbound) → webhook n8n → Google Sheets. Antes de criar, procurar na
  instância n8n do cliente fluxos `GHL`/`Sheets` existentes e reutilizar a credencial Google já em uso; a API
  do n8n não revela a conta Google da credencial — confirmar no painel ou no primeiro append.
- Payload padrão do Outbound: nome, e-mail, telefone, endereço, tags e todos os campos do contato [S9].
  Gravar só as colunas do contrato da planilha; não persistir nem logar o payload inteiro.

## Fontes

- S6 https://help.gohighlevel.com/support/solutions/articles/155000005678 (enable/rebill premium; lista premium)
- S7 https://help.gohighlevel.com/support/solutions/articles/155000003971 (Workflow Pro tiers)
- S8 https://help.gohighlevel.com/support/solutions/articles/48001238167 (Custom Webhook = LC Premium Action)
- S9 https://help.gohighlevel.com/support/solutions/articles/155000003299 (Webhook Outbound; payload)

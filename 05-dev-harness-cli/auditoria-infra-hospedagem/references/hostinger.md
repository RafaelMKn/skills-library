# Hostinger via Composio

Toolkit `hostinger`, 24 tools, cobre billing, domínios, DNS e VPS. Todas as consultas de
inventário aceitam `{}`. Não há tool de métrica de uso do VPS (CPU/disco/RAM) — para isso
só SSH ou o hPanel; não invente números de consumo a partir da API.

Operação da CLI do Composio (login, `unset COMPOSIO_API_KEY`, parsing da saída) está na
skill `composio-apps`.

## Tools de leitura (as que interessam num inventário)

| Tool | Devolve |
|---|---|
| `HOSTINGER_LIST_SUBSCRIPTIONS` | plano, preço, ciclo, status, `next_billing_at`, `is_auto_renewed` |
| `HOSTINGER_LIST_ORDERS` | pedidos e o slug interno do plano (ex: `hostinger_business_v2`) |
| `HOSTINGER_LIST_DOMAINS` | domínios + `free_domain` do plano VPS, com `status` |
| `HOSTINGER_LIST_WEBSITES` | vhosts do hosting compartilhado, `root_directory`, `website_type` |
| `HOSTINGER_LIST_VIRTUAL_MACHINES` | VPS: plano, IPv4/IPv6, template, `state`, `hostname` |
| `HOSTINGER_GET_DNS_RECORDS` | zona completa — exige `{"domain":"..."}` |
| `HOSTINGER_LIST_PUBLIC_KEYS` | chaves SSH cadastradas na conta |
| `HOSTINGER_LIST_WHOIS_PROFILES` | contato de registro (dados pessoais — não ecoe inteiro) |

Escrita por tool (usar só com confirmação explícita): `VALIDATE_DNS_RECORDS`,
`CREATE_PUBLIC_KEY`, `DELETE_PUBLIC_KEY`, `CREATE_WHOIS_PROFILE`, `GENERATE_FREE_SUBDOMAIN`.

## API direta via `composio proxy`

Não existe tool de update de registro DNS, mas a API REST da Hostinger é alcançável
autenticada pelo proxy do Composio — é assim que se altera zona sem hPanel:

```bash
# leitura
composio proxy "https://developers.hostinger.com/api/dns/v1/zones/<dominio>" \
  --toolkit hostinger --account <word_id>

# escrita (PUT substitui o conjunto de registros daquele name+type)
composio proxy "https://developers.hostinger.com/api/dns/v1/zones/<dominio>" \
  --toolkit hostinger --account <word_id> \
  -X PUT -H 'content-type: application/json' \
  -d '{"overwrite":true,"zone":[{"name":"<sub>","type":"A","ttl":300,
        "records":[{"content":"<ip>"}]}]}'
```

Ritual obrigatório: **dump da zona inteira para arquivo antes**, depois
`HOSTINGER_VALIDATE_DNS_RECORDS` com o mesmo payload, aplica, e relê contando os registros —
o PUT mexe só no `name`+`type` enviado, e a contagem total provando que nada mais mudou é o
que distingue alteração cirúrgica de zona sobrescrita.

Resposta de escrita é `{"message":"Request accepted"}` — aceite de enfileiramento, não
confirmação de efeito. A prova é a releitura da zona e a resolução em resolver público.

Outros endpoints úteis pelo mesmo caminho: `/api/vps/v1/virtual-machines/<id>` (detalhe),
`.../actions` (histórico de ações, revela `docker_compose_*` e `backup_create`),
`.../backups`, `.../metrics` (exige `date_from`/`date_to`).

## Chave SSH: cadastrar na conta ≠ instalar no VPS

São dois passos, e a API só expõe o primeiro. `HOSTINGER_CREATE_PUBLIC_KEY` registra a chave
na conta e devolve um `id` — o SSH continua recusando, porque nada foi escrito no
`authorized_keys` da máquina. As rotas de anexar respondem "método não suportado" ou 404, e
uma delas devolve **objeto de ação com campos vazios** (`id: 0`, `state: ""`), que parece
sucesso e não é: confirme sempre pelo histórico em `.../actions` e por um SSH real.

A tela "Chaves SSH" do VPS no hPanel lista o que está anexado **àquela máquina**, então ela
aparece vazia mesmo com a chave já cadastrada na conta — o texto de estado vazio engana.

Caminhos que funcionam, ambos do usuário: o botão de adicionar chave na própria tela do VPS,
ou o Web console do painel executando
`mkdir -p /root/.ssh && echo '<pubkey>' >> /root/.ssh/authorized_keys` com `chmod 700/600`.
A API serve para gerar e cadastrar; a instalação é ato de painel.

## Armadilhas de leitura

- **`renewal_price` e `total_price` vêm em centavos.** `106788` é R$ 1.067,88. Divida por 100
  antes de somar, senão o laudo sai mil vezes maior.
- **`expires_at: null` não é erro nem assinatura vencida** — é assinatura recorrente sem fim
  programado. O par que diz a verdade é `next_billing_at` + `is_auto_renewed`.
- **`status: "cancelled"` com `expires_at` no passado** = benefício já morto, mas o site
  correspondente pode continuar hospedado e ocupando o plano. Cruze `LIST_DOMAINS`
  (domínio `expired`) com `LIST_WEBSITES` (vhost ainda `is_enabled`).
- **`type: "free_domain"` em `pending_setup`** = domínio incluso no plano VPS nunca resgatado.
  Vale citar: resolve necessidade de subdomínio sem custo novo.
- **VPS com template Traefik responde TLS com `CN=TRAEFIK DEFAULT CERT`** em qualquer hostname
  não roteado. Erro de SAN no `curl` contra o IP ou contra `srvNNNN.hstgr.cloud` é rota
  ausente, não servidor fora do ar — teste o hostname que a aplicação realmente usa.
- **404 e timeout dizem coisas diferentes.** Timeout no hostname e 404 forçando resolução para
  o IP certo significa proxy vivo sem rota; timeout nos dois significa destino inalcançável.
  Separe os dois antes de culpar DNS ou aplicação.
- **Duas conexões ACTIVE do mesmo toolkit podem ser contas diferentes, uma delas vazia.**
  Consulte todas as `word_id` antes de concluir; a órfã responde `successful: true` com
  lista vazia.
- **Resolver local mantém o IP antigo pelo TTL do registro anterior.** Depois de alterar a
  zona, valide em resolver público (`1.1.1.1`, `8.8.8.8`) e force o destino no teste HTTP
  (`curl --resolve`) — cache local não é evidência de que a mudança falhou.

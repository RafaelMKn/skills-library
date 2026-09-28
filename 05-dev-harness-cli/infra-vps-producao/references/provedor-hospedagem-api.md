# API de provedor de hospedagem — o que resolve e o que não

Vale para Hostinger e similares, acessados via `composio proxy` ou REST direta. Operação do
Composio: skill `composio-apps`.

## Regra geral

A API do provedor é **rica para a conta e pobre para o interior da máquina**. Ela lista
assinaturas, domínios, DNS, backups, containers e histórico de ações; ela **não** executa comando
dentro do VPS. As escritas que ela oferece para a máquina costumam ser de ciclo de vida inteiro
(recreate, rebuild) — destrutivas, nunca o caminho para uma mudança pontual.

Se a tarefa é mexer em arquivo, container ou rota dentro do VPS, o caminho é SSH ou console web.
Não gaste chamadas procurando endpoint que faça isso.

## Auditoria de conta — o que puxar

| Objetivo | Endpoint / tool |
|---|---|
| Custo e renovações | `LIST_SUBSCRIPTIONS` (`status`, `renewal_price`, `next_billing_at`, `is_auto_renewed`) |
| Domínios e expiração | `LIST_DOMAINS` |
| Sites no plano compartilhado | `LIST_WEBSITES` |
| VPS | `LIST_VIRTUAL_MACHINES` |
| DNS | `GET_DNS_RECORDS`, `VALIDATE_DNS_RECORDS` |
| Backups e histórico | `/vps/v1/virtual-machines/<id>/backups` e `/actions` |

`status: in_trial` com `next_billing_at` é cobrança futura — reporte a data limite de cancelamento.

Uma conexão pode enxergar a conta e outra vir vazia: quando há mais de uma conexão do mesmo
toolkit, descubra qual tem os dados antes de concluir que a conta está vazia, e fixe o
`--account <word_id>` em todas as chamadas seguintes.

## DNS: alterar com segurança

1. Backup da zona inteira em arquivo, com contagem de registros.
2. `VALIDATE_DNS_RECORDS` antes de escrever.
3. `PUT` da zona sobrescreve **por `name`+`type`** — mandar um registro não apaga os outros, mas
   confira a contagem depois.
4. Releia e compare a contagem com o backup. Igual = nada foi perdido.

## Chave SSH — a armadilha

Criar a chave na conta e anexá-la à máquina são **operações diferentes**. A API costuma expor só a
criação; as rotas de attach respondem `404`, `405` ou — pior — um objeto de ação vazio
(`{"id": 0, "state": ""}`) que parece sucesso e não faz nada.

Prove sempre pelo efeito:

```bash
ssh -i <chave> -o BatchMode=yes root@<ip> 'echo CONECTOU'
```

`Permission denied (publickey,password)` = não anexou, independente do que a API respondeu.

O painel do VPS mostra as chaves **daquela máquina**, não as da conta — por isso a tela aparece
vazia mesmo com a chave cadastrada, e o texto de estado vazio engana. O caminho garantido é o
console web do provedor escrevendo direto:

```bash
mkdir -p /root/.ssh && chmod 700 /root/.ssh
echo '<chave-publica>' >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

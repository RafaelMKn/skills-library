---
name: auditoria-infra-hospedagem
description: "Use when auditing a hosting account: cost, waste, DNS."
version: 1.0.0
author: Agent Skills Community
license: MIT
metadata:
  hermes:
    tags: [infra, hospedagem, dns, vps, custo, auditoria]
    related_skills: [composio-apps, incident-forensics, n8n-self-hosting]
---

# Auditoria de conta de hospedagem / infra

Para quando o usuário pergunta "paguei isso, será que estou aproveitando?", ou quando um
domínio/serviço da sua organização ou de cliente precisa ser conferido contra a realidade.
O produto final é um laudo curto: quanto custa, o que está ocioso, o que está quebrado —
tudo verificado, nunca inferido.

## When to Use

- "paguei uma assinatura e acho que não estou aproveitando", "o que eu tenho nessa conta?"
- Conta de hospedagem, VPS ou registrador acabou de ser conectada e precisa ser mapeada.
- Serviço com subdomínio próprio parou de responder e a suspeita é DNS/infra, não aplicação.
- Revisão de custo recorrente antes de renovação, ou herança de infra de um projeto antigo.
- **Não** use para depurar execução de fluxo n8n (`n8n-flow-debugger`) nem para reconstruir
  a linha do tempo de um incidente já conhecido (`incident-forensics`).

## Regra que governa o laudo inteiro

Cada linha do relatório é um fato medido nesta sessão ou uma lacuna declarada como lacuna.
Não existe meio-termo: "o VPS deve estar rodando o n8n" não entra; ou você bateu no `/healthz`
e viu a resposta, ou escreve que não tem como confirmar daqui.

## Procedimento

### 1. Inventário pela API do provedor

Composio primeiro (`composio dev toolkits search <provedor>`); só caia em API/CLI própria se
não houver toolkit. Rode a consulta em **todas** as `word_id` do toolkit — conexão duplicada
vazia responde `successful: true` com lista vazia e induz ao laudo "não tem nada na conta".

Colete: assinaturas, pedidos, domínios, sites/vhosts, máquinas, chaves SSH.
Slugs, escrita de zona via `composio proxy` e armadilhas do toolkit Hostinger:
`references/hostinger.md`.

### 2. Tabela de custo

Normalize a moeda (vários provedores devolvem centavos), some só o que está `active` ou
`in_trial`, e mostre por assinatura: status, valor/ciclo, data da próxima cobrança e se a
renovação automática está ligada. Item em trial com renovação automática e data próxima é
achado, não rodapé — é a decisão com prazo.

### 3. DNS contra a realidade — o passo que acha o problema de verdade

Despeje a zona inteira de cada domínio e, para cada registro que aponta para um destino:

1. Resolva o alvo final (siga a cadeia de CNAME até o A/AAAA).
2. `whois` do IP. **ASN de outro provedor é sinal forte de sobra de migração** — um A record
   apontando para a Hetzner numa conta Hostinger é servidor de uma vida passada.
3. Teste alcance de verdade: ping, TCP em 22/80/443, e HTTP com código de resposta.
4. Conte quantos nomes morrem junto. **Um CNAME apontando para um subdomínio âncora derruba
   todos os filhos de uma vez** — `n8n`, `webhook`, `api`, `painel` pendurados em
   `vps.dominio` viram cinco serviços fora com um único A record podre.

Nunca escreva "servidor morto" sem os três: ping sem resposta, TCP sem resposta nas portas
de serviço, e whois mostrando de quem é o IP.

### 4. Cruze com o que a produção usa de fato

Procure no workspace (`.env`, README de cliente, config de fluxo) o hostname que os sistemas
usam hoje. Divergência entre o subdomínio próprio do DNS e o hostname genérico do provedor
em uso é risco de amarração: trocar de máquina quebra todo webhook registrado em cliente.

### 5. Higiene que quase sempre aparece

- Domínio expirado com site ainda hospedado consumindo o plano.
- Benefício incluso nunca resgatado (domínio grátis, subdomínio, e-mail do plano).
- Zero chaves SSH cadastradas num VPS que roda produção de cliente → acesso por senha.
- `_dmarc` em `p=none` — política sem efeito, spoof do domínio passa.
- Dois planos de hospedagem em paralelo servindo pouca coisa.

## Forma do laudo

Tabela de custo primeiro (inclui o total anual e o mensal equivalente), depois os achados
em ordem de impacto — cada um com a evidência que o sustenta. Fecha com uma seção explícita
do que **não** deu para verificar e por quê, e com uma ou duas ações executáveis agora.

## Antes de executar correção

Mudança de DNS, cancelamento de assinatura e remoção de site são irreversíveis na prática
e afetam produção. Proponha com o valor exato do registro a alterar e espere confirmação.
Depois de aplicar, reconfira pelo mesmo teste que provou o defeito — propagação não é prova.

**Registro DNS órfão é hipótese até olhar o servidor.** Antes de propor apagar CNAME de nome
obscuro, entre na máquina e liste o que roda: um subdomínio sem rota no proxy pode ter
serviço vivo atrás, e a "limpeza" derruba integração de cliente. Quando o destino é um VPS
sob seu acesso, a operação de container e roteamento tem skill própria: `n8n-servidor-vps`.

**Corrigir o DNS resolve metade do problema de roteamento.** Reapontar o registro só entrega
serviço se o reverse proxy do destino tiver rota para aquele hostname — senão o resultado é
404 com certificado default em vez de timeout. Verifique os dois lados antes de prometer que
o subdomínio vai funcionar.

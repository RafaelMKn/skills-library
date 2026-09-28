---
name: n8n-servidor-vps
description: "Use when upgrading or recovering a self-hosted n8n VPS."
version: 1.0.0
author: Agent Skills Community
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [n8n, vps, docker, traefik, upgrade, rollback, producao]
    category: automation
    related_skills: [n8n-correcao-producao, auditoria-infra-hospedagem, incident-forensics]
---

# n8n self-hosted em VPS — operação do servidor

Esta skill é o nível **servidor**: container, imagem, volume, roteamento, upgrade e rollback.
O nível **fluxo** (JSON, nós, execuções via REST) é `n8n-correcao-producao`; o nível **conta**
(assinatura, custo, zona DNS) é `auditoria-infra-hospedagem`.

Responda em PT-BR. O VPS hospeda produção de cliente: cada mudança aqui pode parar atendimento
real, e nenhuma delas é urgente o bastante para pular os gates abaixo.

## When to Use

- Subir, atualizar ou reverter a versão do n8n que roda em container.
- Expor a instância num domínio próprio atrás de reverse proxy.
- Levantar o que de fato roda no VPS antes de mexer em qualquer coisa.
- Recuperar instância depois de upgrade que degradou o serviço.
- **Não** use para corrigir lógica de fluxo, nem para auditar custo de conta de hospedagem.

## A regra que governa tudo

**Container saudável não é serviço funcionando.** `docker ps` dizendo `Up` e `/healthz`
respondendo `200` convivem perfeitamente com uma instância que não ativou nenhum workflow —
isto é, com o cliente parado. Para n8n a prova de vida é a **contagem de `Activated workflow`
no log**, comparada com a contagem conhecida de antes:

```bash
docker logs <container> --since 5m 2>&1 | grep -c "Activated workflow"
```

Registre esse número **antes** de qualquer mudança. Sem a linha de base você não tem como
provar regressão nem sucesso.

## 1. Recon — sempre, antes de tocar

```bash
docker ps --format "{{.Names}} | {{.Image}} | {{.Status}} | {{.Ports}}"
docker compose ls                      # projetos e caminho dos compose
df -h / ; free -h                      # espaço para backup e RAM livre
docker exec <n8n> n8n --version
docker image inspect <img> --format "{{join .RepoDigests \" \"}}"   # digest atual = plano de rollback
```

Mapeie quem está atrás do proxy e quem não está:

```bash
for c in $(docker ps --format "{{.Names}}"); do
  echo "$c -> $(docker inspect $c --format '{{index .Config.Labels "traefik.enable"}}')"
done
```

**Levante os containers antes de classificar um registro DNS como lixo.** Um CNAME de nome
obscuro costuma ter serviço real atrás — WhatsApp API, painel interno — e "limpar órfão"
derruba integração de cliente. O DNS não sabe o que roda; o `docker ps` sabe.

## 2. Expor num domínio próprio sem downtime

Instância provisionada por template de provedor nasce amarrada ao hostname genérico dele
(`srvNNNN.<provedor>`), tanto no router quanto em `WEBHOOK_URL`. Migrar para domínio próprio
é **acrescentar** um segundo router, nunca trocar o existente:

```yaml
- traefik.http.routers.<novo>.rule=Host(`n8n.dominio.com`)
- traefik.http.routers.<novo>.entrypoints=websecure
- traefik.http.routers.<novo>.tls.certresolver=letsencrypt
- traefik.http.routers.<novo>.service=<servico-existente>
```

Os dois hostnames passam a responder em paralelo, sem janela de indisponibilidade e sem
invalidar webhook já registrado em sistema de terceiro.

**`WEBHOOK_URL` é decisão separada, tomada depois.** Trocá-la faz o n8n regenerar as URLs de
webhook; toda URL já cadastrada em sistema de cliente continua apontando para o hostname
antigo. Só decida com o inventário dos webhooks ativos na mão — e mantenha o router antigo
vivo enquanto existir um só consumidor dele.

**Confira o rate limit do Let's Encrypt antes de emitir** (5 certificados por domínio por
semana). O `acme.json` fica dentro de um volume, e pode haver mais de um volume com nome
parecido — um deles vazio, resto de configuração antiga. Ache o que tem conteúdo:

```bash
docker volume ls | grep -i letsencrypt
docker run --rm -v <volume>:/le alpine sh -c \
  'apk add -q jq; jq -r ".[] | .Certificates[]?.domain.main" /le/acme.json' | sort -u
```

Grep vazio em cima do volume errado parece "nenhum certificado emitido" e leva a queimar o
limite à toa.

## 3. Upgrade de versão — gate obrigatório

**Tag flutuante em produção é armadilha.** Compose com `image: .../n8n` sem digest faz
qualquer recriação de container puxar versão nova em silêncio — inclusive uma recriação feita
por outro motivo. Fixe por digest e o upgrade vira ato deliberado:

```yaml
image: docker.n8n.io/n8nio/n8n@sha256:<digest>
```

Antes de atualizar, meça o salto. `latest` costuma estar muito à frente do que roda; leia o
digest remoto e a versão real, não a data da imagem:

```bash
docker manifest inspect docker.n8n.io/n8nio/n8n:latest | grep -m1 digest
```

**Salto de várias versões menores em produção de cliente não é operação de rotina — é projeto.**
O caminho correto é clonar para ambiente isolado e validar lá **antes** de tocar em produção
(passo 5). Atualizar direto porque "o backup existe" troca risco de dados por indisponibilidade
de atendimento, que backup nenhum desfaz. Quando o pedido vier como "atualiza e vê se quebrou",
diga o tamanho do salto e proponha a bancada **antes** de executar — o usuário prefere atrito
agora a cliente parado depois.

### Backup que serve para rollback

n8n com SQLite guarda tudo num volume só. Backup com o container **rodando** copia banco em
escrita — pare antes:

```bash
docker compose stop
docker run --rm -v <projeto>_n8n_data:/d -v /root/backups:/b alpine \
  tar czf /b/n8n_data-<AAAAMMDD>.tar.gz -C /d .
# prove que o dump tem os arquivos do SQLite
docker run --rm -v /root/backups:/b alpine \
  sh -c 'tar tzf /b/n8n_data-<AAAAMMDD>.tar.gz | grep -c database.sqlite'
```

Guarde também o **estado pós-upgrade** em arquivo separado antes de reverter: é o único
material para diagnosticar depois sem repetir a migration em produção.

## 4. Rollback — trocar a imagem de volta não basta

**Migrations alteram o schema de forma que a versão anterior não lê.** Reverter só o `image:`
deixa um binário antigo em cima de um banco novo. Rollback real tem duas metades:

1. restaurar o volume a partir do backup **pré**-migration (limpar o volume antes, não
   sobrepor);
2. fixar a imagem pelo digest da versão que funcionava.

Depois de subir, a verificação é a contagem de `Activated workflow` batendo com a linha de
base — e a versão confirmada por `n8n --version`, não pela tag.

## 5. Ambiente de teste isolado no mesmo host

Para validar upgrade sem risco, clone em projeto docker separado:

- diretório e projeto próprios (`/docker/<nome>-teste/`), volume próprio;
- **sem nenhum label Traefik** (`traefik.enable=false`) — senão o proxy roteia tráfego real
  para a bancada e ainda tenta emitir certificado;
- porta alta publicada em `127.0.0.1`;
- volume populado com **cópia** do backup de produção, nunca com o volume de produção montado
  em escrita.

Ao terminar, `stop` no projeto de teste — mas não apague: o volume é a evidência.

### Delegar a bancada a subagente

Montar e reproduzir é trabalho mecânico e longo: bom candidato a subagente. O briefing precisa
carregar, obrigatoriamente:

- **lista branca e lista negra nominais** — os containers, diretórios e volumes proibidos pelo
  nome, mais o que ele pode criar livremente. "Não toque em produção" sem os nomes é vago.
- **proibição explícita de emitir certificado e de adicionar label de roteamento** — dois
  efeitos colaterais que vazam da bancada para a produção.
- **o que você já descartou**, com evidência. Sem isso o filho refaz seu caminho e gasta a
  janela inteira reproduzindo o que você já sabia.
- **verificação final obrigatória** por `docker ps`, confirmando nominalmente o uptime dos
  containers de produção.

Duas leituras do resultado que não podem ser confundidas: campo de segurança em `false` porque
o filho **quebrou** algo, ou porque ele foi interrompido antes de conseguir verificar e se
recusou a afirmar sem prova. Confira você mesmo o estado real antes de alarmar o usuário — o
segundo caso é o comportamento desejado, não falha. E note que subagente **não tem aprovação
interativa**: passo que dispara confirmação de segurança trava até o timeout, então a etapa
final costuma voltar para você. Trabalho caro que ele deixou pronto (ambiente montado, hipótese
descartada) se aproveita: retomar do ponto custa uma fração de redelegar.

## Pitfalls

- **SQLite em modo `immutable` ignora o arquivo `-wal`.** Consulta assim devolve zero linhas
  para tabelas escritas recentemente e induz a diagnóstico invertido ("a migration não populou
  nada"). Para leitura fiel, pare o container e copie `database.sqlite`, `-wal` e `-shm` juntos
  para um diretório de trabalho antes de consultar.
- **Volume de produção só se lê com `:ro`.** Container descartável de inspeção montando o
  volume em escrita pode consolidar WAL ou criar journal e alterar o estado que você foi medir.
- **Query contra schema novo erra silenciosamente no nome da coluna.** Tabela introduzida por
  migration raramente segue o nome que você supunha; leia `PRAGMA table_info(<tabela>)` antes
  de tirar conclusão de um `JOIN` que devolveu zero.
- **`docker compose restart` não recarrega o compose.** Ele reinicia o container com a
  configuração antiga; mudança de label, imagem ou env exige `up -d`, que recria. Restart que
  "não surtiu efeito" costuma ser isso, não a hipótese sendo falsa.
- **`up -d` recria só o serviço do projeto alvo.** Os outros projetos mantêm o uptime — e essa
  é a forma de provar que a mudança foi contida: compare o `Status` dos containers vizinhos
  antes e depois.
- **Timezone do container vem do template do provedor**, frequentemente em outra região. Cron e
  Schedule Trigger disparam nesse fuso, silenciosamente, com horas de diferença do horário
  comercial do cliente. Confira `TZ`/`GENERIC_TIMEZONE` no recon e trate divergência como
  achado, não como detalhe.
- **Aviso de deprecação no log do upgrade é trabalho futuro, não ruído.** Variável renomeada e
  default que vai mudar continuam funcionando na versão atual e quebram na seguinte; anote no
  relato em vez de descartar.
- **Imagem antiga continua local depois do `pull`.** O rollback por digest é imediato enquanto
  ninguém rodou `docker image prune`. Confirme com `docker images --digests` antes de atualizar
  — se a antiga já sumiu, o rollback passa a depender de download.
- **Task runner de Python ausente é achado, não erro de instalação.** A imagem oficial não traz
  Python; Code node em Python falha em runtime enquanto os em JS ativam normalmente. Se o log
  reclamar disso, verifique se algum fluxo depende de Python antes de ignorar.

## Verification

- Contagem de `Activated workflow` igual à linha de base registrada no recon.
- `n8n --version` confirma a versão pretendida.
- Containers vizinhos com o uptime preservado.
- Hostname antigo **e** novo respondendo, quando a mudança foi de roteamento.
- Certificado apresentado é o do domínio (não o default do proxy), com emissor e validade
  lidos de verdade.

## Formato do relato

O que mudou · o que foi verificado, com o número que prova · o que ficou pendente e de quem
depende. Quando um upgrade é revertido, o relato diz **o que ficou bloqueado e por quê** — e
não apresenta a causa como conhecida se ela não foi isolada. Hipótese não confirmada se escreve
como hipótese. Quando a própria conduta foi o erro (executar direto o que pedia bancada), diga
isso explicitamente no relato em vez de apresentar o rollback como desfecho limpo.

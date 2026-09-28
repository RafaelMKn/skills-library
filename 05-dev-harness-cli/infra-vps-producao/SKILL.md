---
name: infra-vps-producao
description: "Use when operating a production VPS: Docker, Traefik, DNS."
version: 1.0.0
author: Agent Skills Community
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [vps, docker, traefik, dns, tls, upgrade, rollback, producao, PT-BR]
    category: devops
    related_skills: [n8n-correcao-producao, composio-apps, incident-forensics]
---

# Operar VPS de produção (Docker + Traefik)

O VPS hospeda serviços e sistemas críticos de produção junto com serviços internos, no mesmo Docker e atrás do mesmo
Traefik. Derrubar o container errado, ou declarar "quebrou" a partir de um sinal fraco, interrompe a
operação. Esta skill cobre inventário, roteamento, upgrade com rollback provado e — principalmente —
como **provar** o estado em vez de inferir.

Responda em **PT-BR**. Quando o problema está no JSON do fluxo e não na instância, a skill é
`n8n-correcao-producao`.

Suporte: `references/upgrade-container-com-banco.md` (upgrade/rollback de app com banco embarcado) ·
`references/traefik-hostnames-tls.md` (roteamento e Let's Encrypt) ·
`references/provedor-hospedagem-api.md` (o que a API do provedor resolve e o que não) ·
`scripts/sqlite_wal_read.sh` (leitura WAL-aware de SQLite em volume Docker).

## When to Use

- Auditar uma conta de hospedagem: o que se paga, o que roda, o que está pago e ocioso.
- Apontar domínio próprio para serviço que hoje só responde no hostname genérico do provedor.
- Atualizar, reiniciar ou migrar container que serve produção ou usuários externos.
- Investigar subdomínio que não responde, 404 de proxy reverso ou certificado errado.

## Gates — antes de tocar em qualquer coisa que já roda

1. **Inventário primeiro, conclusão depois.** `docker ps`, `docker compose ls`, `df -h`, e a lista
   de DNS da zona. Só depois diga o que está quebrado.
2. **Nenhum registro DNS é órfão até você achar o serviço que ele fronteia.** Um CNAME que dá
   timeout pode apontar para container vivo que simplesmente não tem rota no proxy. Mapeie
   `registro → serviço rodando` antes de propor remoção; deletar por aparência derruba integração.
3. **Declare a classe de risco antes de executar, não depois.** Upgrade de app com banco embarcado,
   troca de `WEBHOOK_URL` e mudança de DNS de produção não são rotina, mesmo quando o pedido veio
   curto ("atualiza aí"). Diga o que pode quebrar e ofereça a bancada isolada **antes** de rodar.
   Executar direto e reverter depois custa downtime em produção que não precisava existir.
4. **Backup com o container parado.** Banco embarcado (SQLite) tem `-wal` com commits não
   consolidados; `tar` do volume com o processo vivo gera backup que pode não restaurar.
5. **Anote o digest da imagem atual** (`docker image inspect --format '{{.RepoDigests}}'`) antes de
   qualquer `pull`. Sem ele não existe rollback determinístico.
6. **Ação destrutiva é sempre por escopo nomeado.** Comando que varre "todos os containers" ou
   "volumes não usados" não entra em VPS compartilhado com produção.

## Provar o estado: leia a fonte autoritativa, não o log

**Ausência de uma linha de log não é prova de falha.** Strings de log são renomeadas e removidas
entre versões; um upgrade que muda o subsistema muda também o que ele imprime. Usar "a linha X
sumiu" como evidência de quebra produz falso positivo — e um rollback de produção desnecessário.

Antes de concluir que um serviço quebrou após upgrade:

1. Leia o **estado persistido** que o próprio app grava (tabelas de status, endpoint de health,
   API REST), não o texto do log.
2. Se há coluna de erro (`status`, `errorMessage`), leia-a. `activated` com `errorMessage` vazio é
   sucesso, independente do que o log deixou de imprimir.
3. Só depois, se o estado confirmar falha, trate como quebra.

Mensagem de um subsistema não é veredito de outro: um índice que reporta `Processed 0 ...` pode ser
de construção de dependências, não do motor de ativação. Confirme qual componente emitiu a linha
antes de atribuir significado a ela.

Quando log e banco se contradizem, **o banco decide** — e a contradição é o achado, não um detalhe.

## Leitura de SQLite: WAL ou conclusão invertida

Banco SQLite em modo WAL guarda os commits recentes no arquivo `-wal`. Ler com `immutable=1`, ou
copiar só `database.sqlite`, **ignora o WAL** e devolve tabela vazia onde há dados — invertendo o
diagnóstico.

Sempre: pare o container, copie `database.sqlite`, `database.sqlite-wal` e `database.sqlite-shm`
**juntos**, e consulte a cópia em leitura normal. `scripts/sqlite_wal_read.sh` faz isso.

Montar o volume como `:ro` e tentar abrir com WAL falha com `unable to open database file (14)` —
o SQLite precisa escrever para reproduzir o WAL. Por isso se consulta a **cópia**, nunca o volume.

## Fixar imagem por digest

Compose de produção com tag flutuante (`image: app:latest`) significa que qualquer recriação de
container pode saltar de versão em silêncio — inclusive um `up -d` de rotina feito para outra coisa.
Depois de estabilizar uma versão, fixe:

```yaml
image: registry/app@sha256:<digest>
```

Isso transforma "atualizar" em decisão explícita. Ao fixar, registre no relato — é mudança
permanente de comportamento do deploy.

## Subagente em infraestrutura

Delegar recon e reprodução funciona; delegar a conclusão, não.

- **Briefing lista os containers e diretórios proibidos por nome**, não "não mexa em produção".
- **Resumo de filho é auto-relato.** Um `producao_intacta: false` pode significar "fui bloqueado
  antes de verificar", não "quebrei". Confirme você mesmo antes de repassar qualquer veredito.
- **Revise o artefato que o filho criou antes de aceitar a conclusão dele.** Bancada montada errada
  invalida o achado: um compose com `networks.default.internal: true` impede publicar porta
  (`docker port` volta vazio, o serviço fica inalcançável) e ainda derruba o DNS de saída. Leia o
  compose gerado antes de tratar o teste como válido.
- Trocar o modelo dos filhos é `hermes config set delegation.model <modelo>` +
  `delegation.provider <provider>`; confirme que o provider está autenticado
  (`hermes auth status <provider>`) **antes** de setar, senão os filhos falham no primeiro turno.

## Pitfalls

- **Resposta JSON com formato de sucesso e campos vazios não é sucesso.** Um `{"id": 0, "name": "",
  "state": ""}` de API de provedor é rota que aceitou o POST e não fez nada. Prove pelo efeito
  (conexão SSH real, recurso listado), nunca pelo corpo da resposta.
- **Cadastrar chave SSH na conta ≠ instalar a chave no servidor.** São dois passos e a API do
  provedor costuma expor só o primeiro; o painel do VPS lista o que está anexado **àquela máquina**,
  por isso mostra vazio mesmo com a chave existindo na conta. O caminho garantido é o console web do
  provedor escrevendo em `authorized_keys`.
- **Serviço exposto em porta alta com bind `0.0.0.0` não está atrás do proxy.** Ver o proxy rodando
  não prova que ele roteia aquele serviço; confira os labels do container.
- **Cert `TRAEFIK DEFAULT CERT` = nenhum router casou com o hostname.** É roteamento ausente, não
  falha de TLS — não reemita certificado tentando consertar.
- **O volume do `acme.json` pode não ser o nomeado no compose.** Projetos criados em momentos
  diferentes deixam volume órfão com nome parecido (`traefik-letsencrypt` vs
  `traefik_traefik-letsencrypt`). Liste os dois e confira qual tem o arquivo antes de concluir que
  não há certificado emitido.
- **Let's Encrypt limita emissões por domínio por semana.** Antes de subir hostname novo, leia os
  domínios já emitidos no `acme.json`; testar repetidamente queima a cota e trava o domínio.
- **Timezone do container decide a hora do cron.** `TZ` herdado do template (ex.: fuso do
  datacenter) faz todo agendamento disparar fora do horário comercial local. Verifique ao
  auditar; corrigir muda o horário de tudo que já roda, então é decisão do dono.
- **Plano de hospedagem pago e ocioso é achado de auditoria.** Site estático em plano de negócio,
  domínio expirado com WordPress ainda instalado, domínio grátis incluso nunca resgatado, serviço em
  trial prestes a virar cobrança. Reporte com valor anual e a data limite de cancelamento.

## Formato do relato

Na ordem: **o que foi feito e verificado** (com o dado que prova: código HTTP, versão, contagem) ·
**o que a verificação revelou de novo** · **onde travou e o que destrava**.

Tabela para inventário e custo. Não narre chamada de ferramenta que o usuário já viu.

**Erro seu vira parágrafo próprio, não nota de rodapé.** Se um diagnóstico errado causou downtime,
diga isso explicitamente, com o sinal fraco que você usou como prova — é o que impede a repetição.

Pendências se agrupam no fim, com a data limite quando existir (renovação, trial, expiração).

## Verification

- `docker ps` mostra todos os containers de antes, com uptime preservado nos que você não tocou.
- Endpoint externo de cada serviço público responde (código HTTP colado no relato).
- Hostname antigo continua respondendo depois de adicionar o novo.
- Backup do volume existe e contém os três arquivos do SQLite.
- Compose de produção fixa imagem por digest.

# Traefik: hostnames, roteamento e TLS

## Adicionar hostname sem downtime

Não edite o router existente — **acrescente um segundo**, apontando para o mesmo serviço. Os dois
hostnames passam a funcionar em paralelo e nenhum webhook já registrado quebra.

```yaml
labels:
  # router existente, intocado
  - traefik.http.routers.<antigo>.rule=Host(`<host-antigo>`)
  # router novo
  - traefik.http.routers.<novo>.rule=Host(`<host-novo>`)
  - traefik.http.routers.<novo>.entrypoints=websecure
  - traefik.http.routers.<novo>.tls.certresolver=letsencrypt
  - traefik.http.routers.<novo>.service=<nome-do-service-existente>
```

O `.service=` explícito é obrigatório quando o serviço já está declarado pelo router antigo; sem
ele o Traefik tenta inferir e pode não achar a porta.

Aplique com `docker compose up -d` no projeto — recria só aquele container.

## Diagnóstico de subdomínio que não responde

Na ordem, porque cada etapa descarta a seguinte:

1. **Resolve?** `dig +short <host> @1.1.1.1` e `@8.8.8.8`. Resolver local guarda TTL antigo — a
   divergência entre local e público é cache, não erro.
2. **A porta abre?** Teste TCP 80/443 no IP de destino.
3. **Qual cert o proxy apresenta?**
   ```bash
   openssl s_client -connect <ip>:443 -servername <host> </dev/null 2>/dev/null \
     | openssl x509 -noout -subject -issuer -dates
   ```
   `CN=TRAEFIK DEFAULT CERT` significa **nenhum router casou com o hostname** — problema de
   roteamento, não de TLS.
4. **O container tem label?** `docker inspect --format '{{index .Config.Labels "traefik.enable"}}'`.

Para testar hostname antes de o DNS propagar, force a resolução em vez de esperar:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' --resolve '<host>:443:<ip>' https://<host>/
```

## Let's Encrypt

- Confira o que já foi emitido antes de subir hostname novo — a cota é por domínio por semana:
  ```bash
  docker run --rm -v <volume-acme>:/le alpine sh -c \
    'apk add -q jq; jq -r ".[] | .Certificates[]?.domain.main" /le/acme.json | sort -u'
  ```
- O volume do `acme.json` pode não ser o nomeado no compose: liste `docker volume ls` e procure o
  par de nomes parecidos (com e sem prefixo do projeto). O vazio é resíduo de deploy antigo.
- Emissão acontece no start do container com o router novo; espere ~30s antes de testar.

## Trocar a URL pública de webhook

Mudar `WEBHOOK_URL` (n8n) ou equivalente **regenera as URLs** que o app publica. Webhook já
cadastrado em sistema de terceiro continua apontando para o hostname antigo.

Por isso: mantenha o router antigo vivo, e só troque a variável depois de inventariar quais fluxos
têm URL registrada fora. Adicionar hostname é seguro; trocar a URL base não é.

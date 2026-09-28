# Upgrade de container com banco embarcado

Vale para qualquer app que carrega o próprio banco num volume (n8n/SQLite, Grafana, Vaultwarden…).
O que torna essa classe perigosa: **migrations são de mão única**. Trocar a imagem de volta não
desfaz o schema novo.

## Antes

1. Versão e digest atuais:
   ```bash
   docker exec <container> <app> --version
   docker image inspect <image> --format '{{join .RepoDigests " "}}'
   ```
2. Para onde a tag flutuante aponta hoje (o salto pode ser muito maior que o esperado):
   ```bash
   docker manifest inspect <image>:latest | grep -m1 digest
   ```
3. Espaço livre ≥ 2× o volume.
4. Janela sem tráfego, conferida no log.

## Backup (container parado)

```bash
cd /docker/<projeto> && docker compose stop
docker run --rm -v <projeto>_<volume>:/d -v /root/backups:/b alpine \
  tar czf /b/<volume>-<AAAAMMDD>.tar.gz -C /d .
```

Confirme que o tar contém `database.sqlite`, `-wal` e `-shm`. Backup sem o `-wal` perde os últimos
commits.

## Depois de subir

Não use o log como critério de sucesso — veja a regra na SKILL.md. Leia o estado persistido.

No n8n ≥ 2.40 a ativação deixou de ser uma linha de log por workflow e passou a ser estado em
tabela. As tabelas que respondem "ativou ou não":

| Tabela | O que diz |
|---|---|
| `workflow_publication_trigger_status` | `status` ∈ (`activated`,`failed`) + `errorMessage`, por nó |
| `workflow_publication_outbox` | `status` ∈ (`pending`,`in_progress`,`completed`,`partial_success`,`failed`) + `reason` (`startup`) |
| `workflow_published_version` | versão publicada por workflow (`workflowId`, `publishedVersionId`) |
| `workflow_publish_history` | histórico de eventos |

`activated` / `completed|startup` com `errorMessage` vazio é ativação bem-sucedida. A linha
`Finished building workflow dependency index. Processed 0 draft workflows, 0 published workflows.`
vem do índice de dependências e **não** é veredito de ativação.

A consistência do modelo de publicação se confere assim (leitura WAL-aware, ver
`scripts/sqlite_wal_read.sh`):

```sql
SELECT count(*) FROM workflow_entity WHERE active=1 AND isArchived=0;
SELECT count(*) FROM workflow_entity w
  JOIN workflow_published_version p
    ON p.workflowId=w.id AND p.publishedVersionId=w.activeVersionId
 WHERE w.active=1 AND w.isArchived=0;
SELECT status, triggerKind, count(*) FROM workflow_publication_trigger_status GROUP BY 1,2;
SELECT status, reason, count(*) FROM workflow_publication_outbox GROUP BY 1,2;
SELECT errorMessage FROM workflow_publication_trigger_status WHERE status='failed';
```

## Rollback

Trocar só a imagem **não basta** quando migrations rodaram: a versão antiga não lê o schema novo.
O rollback completo é:

1. `docker compose down` do projeto.
2. Guardar o volume pós-migration num tar separado (serve para diagnosticar depois sem repetir o
   upgrade).
3. Limpar o volume e restaurar o tar pré-migration.
4. Fixar a imagem **por digest** antigo no compose — não pela tag.
5. `up -d` e verificar pelo estado, não pelo log.

## Bancada isolada — a ordem certa

Upgrade de produção crítica se valida antes em projeto separado:

- projeto próprio (`<app>-teste`), porta alta distinta, `traefik.enable=false`;
- volume populado a partir do **tar pré-migration**, nunca compartilhando o volume de produção;
- `restart: "no"`;
- **não** use `networks.default.internal: true` — isso impede publicar porta (`docker port` volta
  vazio) e derruba o DNS de saída do container. Bancada inalcançável não valida nada.

Só depois que a bancada reproduz o cenário e o estado confirma ativação é que a produção se move.

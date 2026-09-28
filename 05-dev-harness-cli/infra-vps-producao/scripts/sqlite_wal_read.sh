#!/usr/bin/env bash
# Leitura WAL-aware de um SQLite que vive num volume Docker.
#
# POR QUE EXISTE: ler com immutable=1, ou copiar apenas database.sqlite, IGNORA o
# arquivo -wal e devolve tabela vazia onde existem dados — invertendo o diagnóstico.
# Montar o volume :ro e abrir com WAL falha com "unable to open database file (14)",
# porque o SQLite precisa escrever para reproduzir o WAL. Por isso consultamos uma CÓPIA.
#
# USO:
#   sqlite_wal_read.sh <volume-docker> <arquivo.sql> [caminho-do-db-dentro-do-volume]
#
# EXEMPLO:
#   cd /docker/n8n-prod && docker compose stop     # WAL consistente
#   sqlite_wal_read.sh n8n-prod_n8n_data /root/q.sql
#
# O script NÃO para nem sobe container — faça isso você, conscientemente.
# Ele só lê. A cópia fica em /root/sqlite-wal-read/ para inspeção posterior.
set -euo pipefail

VOL="${1:?uso: $0 <volume-docker> <arquivo.sql> [db-path-no-volume]}"
SQL="${2:?uso: $0 <volume-docker> <arquivo.sql> [db-path-no-volume]}"
DB="${3:-database.sqlite}"
OUT=/root/sqlite-wal-read

[ -f "$SQL" ] || { echo "arquivo SQL nao encontrado: $SQL" >&2; exit 1; }

rm -rf "$OUT"; mkdir -p "$OUT"

# Copia db + wal + shm JUNTOS. Sem o -wal a leitura mente.
docker run --rm -v "$VOL":/src:ro -v "$OUT":/dst alpine:3.20 sh -c "
  cd /src
  for f in '$DB' '$DB-wal' '$DB-shm'; do
    [ -f \"\$f\" ] && cp \"\$f\" /dst/ || true
  done
"

echo "=== arquivos copiados ==="
ls -l "$OUT"
[ -f "$OUT/$DB-wal" ] || echo "AVISO: sem arquivo -wal (ok se o app nao usa WAL, suspeito se usa)"

echo
echo "=== resultado ==="
# Leitura normal (read-write na COPIA) para o SQLite reproduzir o WAL.
docker run --rm -v "$OUT":/d -v "$SQL":/q.sql:ro alpine:3.20 sh -c "
  apk add --no-cache sqlite >/dev/null 2>&1
  sqlite3 /d/'$DB' < /q.sql
"

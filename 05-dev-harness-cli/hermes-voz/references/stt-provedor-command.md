# STT por provedor `type: command` (nuvem sem suporte nativo)

Use para plugar qualquer API de transcrição (Deepgram, AssemblyAI...) sem tocar no código do Hermes.
O Hermes renderiza o comando com placeholders shell-quoted e lê o texto do arquivo de saída (ou do
stdout).

## Placeholders

`{input_path}` (áudio, geralmente `.webm` do desktop), `{output_path}` (arquivo de transcrição),
`{output_dir}`, `{format}` (txt/json/srt/vtt), `{language}` (vem de `stt.providers.<nome>.language`,
senão do STT global; padrão `en`).

## Registro

`hermes config set` rejeita `stt.providers.*` como chave desconhecida; use `--force`:

```bash
hermes config set --force stt.providers.deepgram.type command
hermes config set --force stt.providers.deepgram.command '~/.hermes/scripts/deepgram-stt.sh {input_path} {output_path} {language}'
hermes config set --force stt.providers.deepgram.language pt-BR
hermes config set --force stt.providers.deepgram.env_passthrough '["DEEPGRAM_API_KEY"]'
```

- O processo filho roda com ambiente **sem segredos**; a chave só chega ao script se estiver em
  `env_passthrough`. Sem isso o script vê a variável vazia mesmo com ela no `.env`.
- A chave vai em `~/.hermes/.env`, colada pelo usuário; nunca pelo chat.
- Nomes built-in (`local`, `openai`, `groq`...) sempre vencem; dê nome próprio ao provedor.

## Script (Deepgram, `~/.hermes/scripts/deepgram-stt.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail
in="$1"; out="$2"; lang="${3:-pt-BR}"; [ "$lang" = "pt" ] && lang="pt-BR"
: "${DEEPGRAM_API_KEY:?DEEPGRAM_API_KEY ausente no ~/.hermes/.env}"
mime="$(file -b --mime-type "$in")"
resp="$(curl -sS --fail-with-body --max-time 120 \
  -H "Authorization: Token ${DEEPGRAM_API_KEY}" -H "Content-Type: ${mime}" --data-binary @"$in" \
  "https://api.deepgram.com/v1/listen?model=nova-3&language=${lang}&smart_format=true&punctuate=true")"
python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["results"]["channels"][0]["alternatives"][0]["transcript"])' <<<"$resp" > "$out"
```

O STT global fala `pt`; o Deepgram quer `pt-BR` — por isso o mapeamento no script.

## Ativação (só depois de validar)

1. Com a chave no `.env`, rode o script num `.wav`/`.webm` real em PT-BR e leia o texto.
2. Só então `hermes config set stt.provider deepgram`.
3. Reverter: `hermes config set stt.provider local`.

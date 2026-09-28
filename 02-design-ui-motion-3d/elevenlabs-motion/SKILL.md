---
name: elevenlabs-motion
description: Gera locuções pela API da ElevenLabs e entrega áudio com timings para sincronizar Reels, Shorts e vídeos em motion. Use quando uma peça aprovada precisar de voz, escolha de voice_id, validação de cota ou alinhamento para beats e legendas.
---

# ElevenLabs Motion

Transforme a locução aprovada em um par reutilizável: áudio final e JSON de timings. Operações de consulta são gratuitas; `generate` consome créditos e só deve rodar quando o usuário ou o Board pedir explicitamente a geração.

## Fluxo

1. Identifique a locução exata aprovada e preserve todas as palavras. Direção de performance não é texto falado: no `eleven_v3`, traduza apenas o que for pertinente para audio tags e pontuação suportadas.
2. Resolva a voz. Use `ELEVENLABS_VOICE_ID` quando configurada; caso contrário, execute `voices`, apresente as candidatas e obtenha uma escolha explícita antes de gerar.
3. Escolha o modelo:
   - `eleven_v3`: padrão para motion, publicidade e entrega expressiva;
   - `eleven_multilingual_v2`: use para estabilidade em locuções longas ou quando a leitura de números for crítica;
   - `eleven_flash_v2_5`: use quando custo ou latência importar mais que expressividade.
4. Normalize por extenso números, datas, siglas e símbolos cuja pronúncia importe. Para `eleven_v3`, controle pausas com pontuação e audio tags; para os modelos v2/v2.5, `<break time="x.xs" />` aceita pausas de até 3 segundos.
5. Rode primeiro com `--dry-run`. Confira voz, modelo, formato, caracteres e destinos; só então execute sem esse sinalizador.
6. Inspecione o áudio gerado. O JSON fornece alinhamento bruto, palavras derivadas e duração; use esses tempos como base dos beats e legendas, ajustando visualmente quando a performance exigir.

## Helper

Use o script sem instalar SDK:

```powershell
python skills/elevenlabs-motion/scripts/elevenlabs_motion.py status
python skills/elevenlabs-motion/scripts/elevenlabs_motion.py models
python skills/elevenlabs-motion/scripts/elevenlabs_motion.py voices --language pt --search narracao
python skills/elevenlabs-motion/scripts/elevenlabs_motion.py generate --text-file roteiro.txt --voice-id VOICE_ID --output locucao.mp3 --dry-run
python skills/elevenlabs-motion/scripts/elevenlabs_motion.py generate --text-file roteiro.txt --voice-id VOICE_ID --output locucao.mp3
```

`generate` chama o endpoint com timestamps e cria, ao lado do áudio, `<nome>-timings.json`. Ele recusa sobrescrever arquivos sem `--force`. Prefira salvar ambos na pasta canônica da peça de motion, não em `scratch/`.

O script lê `ELEVENLABS_API_KEY` do ambiente ou do `.env` mais próximo. `ELEVENLABS_VOICE_ID` e `ELEVENLABS_MODEL_ID` são defaults opcionais. Nunca passe a chave na linha de comando, registre-a em artefatos ou mostre seu valor.

Chaves restritas precisam de `text_to_speech` para gerar, `models_read` para executar `models`, `voices_read` para executar `voices` e `user_read` para executar `status`. Se a chave tiver apenas geração, receba modelo e `voice_id` por configuração ou pelo usuário; a falha das consultas auxiliares não invalida a permissão de TTS.

Leia [references/api-elevenlabs.md](references/api-elevenlabs.md) ao alterar endpoints, modelos, formatos ou parametros da integracao.

## Critério de pronto

A geração termina com áudio audível, timings JSON válidos, voz/modelo registrados nos metadados e duração disponível para o pipeline de motion. Uma resposta da API sem inspeção do arquivo não encerra o trabalho.

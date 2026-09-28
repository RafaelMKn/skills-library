# API ElevenLabs para locução de motion

Consulta oficial realizada em 2 de setembro de 2026.

## Superfície usada

- Autenticação: header `xi-api-key`, carregado de `ELEVENLABS_API_KEY`.
- Modelos disponíveis: `GET /v1/models`.
- Cota e plano: `GET /v1/user/subscription`.
- Busca paginada de vozes: `GET /v2/voices`.
- Áudio com alinhamento: `POST /v1/text-to-speech/{voice_id}/with-timestamps`.
- Modelo padrão da API quando omitido: `eleven_multilingual_v2`; a skill envia o modelo explicitamente.
- Formato padrão: `mp3_44100_128`.

O endpoint com timestamps devolve `audio_base64`, `alignment` e `normalized_alignment`. Cada alinhamento contém caracteres e vetores de início/fim em segundos. O helper persiste o retorno relevante e deriva intervalos por palavra; não trate essa derivação como transcrição nova.

Em chaves com escopo mínimo, `models` requer `models_read`, `status` requer `user_read`, `voices` requer `voices_read` e `generate` requer `text_to_speech`. Mantenha apenas as permissões necessárias; quando os escopos de leitura não estiverem disponíveis, forneça modelo e `voice_id` conhecidos sem afrouxar a chave automaticamente.

## Modelos

| ID | Quando usar | Limite informado |
|---|---|---:|
| `eleven_v3` | conteúdo expressivo e narração profissional | 5.000 caracteres |
| `eleven_multilingual_v2` | PT-BR estável e locução longa | 10.000 caracteres |
| `eleven_flash_v2_5` | baixa latência e menor custo | 40.000 caracteres |

`eleven_v3` aceita audio tags e não aceita SSML `<break>`. A documentação recomenda prompts com mais de 250 caracteres para reduzir variação em v3. `eleven_multilingual_v2` e Flash aceitam `<break time="x.xs" />` com pausas de até 3 segundos. Flash pode pronunciar números de modo inesperado; escreva números, datas, símbolos e siglas por extenso quando a leitura exata importar.

## Voz e configuração

O sotaque vem principalmente da voz escolhida. Busque vozes por idioma, sotaque e caso de uso em `/v2/voices`; não infira `voice_id` pelo nome.

Nos modelos compatíveis, `stability` e `similarity_boost` ficam entre 0 e 1, `style` normalmente permanece em 0 e `speed` fica entre 0,7 e 1,2. `speed`, `similarity_boost` e `style` não estão disponíveis no Eleven v3; direcione v3 pelo texto, pontuação e audio tags.

## Referências oficiais

- [Autenticação](https://elevenlabs.io/docs/api-reference/authentication)
- [Criar fala com timestamps](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps)
- [Listar vozes](https://elevenlabs.io/docs/api-reference/voices/search)
- [Modelos](https://elevenlabs.io/docs/overview/models)
- [Escolha de modelo](https://elevenlabs.io/docs/eleven-api/choosing-the-right-model)
- [Text to Speech e configurações de voz](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech)
- [Prompting do Eleven v3](https://elevenlabs.io/docs/best-practices/prompting)
- [Boas práticas de TTS](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)

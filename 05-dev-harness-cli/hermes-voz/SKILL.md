---
name: hermes-voz
description: "Use when setting up or debugging Hermes voice and wake."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, voz, wake-word, stt, tts, desktop, pt-br]
    related_skills: [hermes-agent, hermes-context-tuning]
---

# Voz no Hermes (wake word, transcrição, fala)

O ciclo de voz do desktop tem quatro elos: **wake word → gravação → STT → agente → TTS**. Quando o
O usuário diz "não funciona" ou "ficou em silêncio", o defeito está em um elo só. Ache qual pelo log
antes de mexer em config. O usuário fala PT-BR e dita pedidos por voz, então o idioma pesa em todos
os elos.

## When to Use

- Trocar a palavra de ativação, ligar `/wake`, escolher voz ou modelo de transcrição.
- "Não acorda", "ficou em silêncio", "entendeu errado", "não falou a resposta".
- Pedido ditado chega com "week word"/"wake word" — é esta skill.

## Procedure

1. **Leia o estado atual.** `hermes config get wake_word`, `hermes config get voice`,
   `hermes config get tts`, `hermes config get stt`. Config só se altera com `hermes config set`
   (o arquivo é protegido contra escrita direta).
2. **Cheque o volume de entrada do microfone** antes de culpar motor ou modelo:
   `pactl get-source-volume @DEFAULT_SOURCE@`. Abaixo de ~30% derruba wake word, conversa e STT de
   uma vez (transcrição sem sentido + `VAD filter removed` grande). Ver linha do AGC na tabela.
3. **Localize o elo quebrado no log** — `grep -iE "wake|faster_whisper|transcri|tts" ~/.hermes/logs/agent.log`
   e `~/.hermes/logs/desktop.log`, olhando a janela de horário do teste:
   - `wake.start(gui): not available — <hint>` → o wake word se recusou a armar; o hint diz o elo.
   - `listening for '<frase>'` sem `phrase detected` → o detector não reconhece a pronúncia.
   - `phrase detected` → `Transcribed ...` → `tui prompt accepted` → o ciclo rodou. Leia a sessão
     criada (`session_search(session_id=...)`, o id aparece em `agent_session_id=`) para ver **o que
     foi transcrito e o que foi respondido** antes de chamar de silêncio.
4. **Corrija o elo** com a tabela abaixo. Para novo detector, passe primeiro no áudio real e nos negativos offline (`references/teste-offline-wake-word.md`); implemente por subagente e revise o engine efetivo e a integração. Separe aprovação offline de ativação. Quando houver restrição de não interromper serviços, solicite autorização específica para reabrir apenas o Desktop/backend e preserve gateway e pontes; não declare integração completa antes do teste real até TTS.
5. **Verifique antes de dizer que funciona.** Descubra o Python efetivo com
   `hermes --print-runtime-command --module tools.wake_word`; execute as sondagens no runtime
   retornado, sem presumir `venv/bin/python` nem usar `--run-module` nessa descoberta.
   Sondagem interna: importe `load_wake_word_config` e `check_wake_word_requirements` de
   `tools.wake_word`. Para Desktop com captura pelo cliente, teste uma cópia da configuração com
   `capture='client'`; não altere a configuração persistida só para fazer a sonda passar.
   Uma sonda em captura local pode falhar por ausência de entrada PortAudio enquanto o Desktop
   está apto a enviar áudio via `wake.feed`. Compare o resultado com `capture=client/local` no log
   de `wake.start(gui)` antes de diagnosticar falta de microfone.
   Síntese: importe `text_to_speech_tool` de `tools.tts_tool` e execute `text_to_speech_tool('teste')`.
   Isso prova prontidão e síntese, não reconhecimento da fala real nem reprodução audível.
6. **Separe ativação da conversa de abertura da janela.** Ao mapear uso por palavra de ativação,
   verifique separadamente: conversa dentro do app, restauração/foco da janela minimizada e app
   totalmente encerrado. Um evento `wake.detected` que inicia voz e cria uma sessão não prova que
   a janela será restaurada. Teste esse comportamento antes de propor alteração de código.
   Para acordar com o app encerrado, é necessário um listener independente; prefira primeiro o
   Desktop aberto/minimizado e confira a inicialização automática da sessão do usuário.
   Informe o que já existe, o que foi apenas sondado e o que depende do teste com a voz do usuário.
   Quando a pergunta for apenas qual opção é gratuita, responda primeiro com a combinação:
   Faster-Whisper local + Edge PT-BR; esclareça que Edge usa internet e que o custo do LLM é separado.
7. **Separe código, pacote e processo em execução ao entregar mudanças no Desktop.** Rode os
   testes específicos e verifique o pacote final; `npm run build` atualiza `dist`, não prova que
   `release/linux-unpacked` nem a janela aberta carregaram a mudança. Empacote em diretório
   separado para preservar o app em uso e peça autorização antes de fechar/reabrir a sessão.
   Receita de empacotamento e verificação: `references/desktop-voz-implantacao.md`.

## Elo × correção

| Sintoma | Causa | Correção |
|---|---|---|
| `/wake on` recusa com "needs text-to-speech" | provedor de TTS sem credencial (ex.: `nous` sem gateway gerenciado, `openai` sem chave) | `hermes config set tts.provider edge` + `tts.edge.voice pt-BR-AntonioNeural` (ou `pt-BR-FranciscaNeural`). Edge é grátis e sem chave. |
| Trocar a palavra de ativação | openWakeWord depende de modelos treinados; idioma e vocabulário do detector limitam a frase | Para inglês, avaliar sherpa com frase livre; para PT-BR, avaliar Vosk com modelo português e gramática restrita. Testar gravação real e negativos antes de ativar; ver `references/teste-offline-wake-word.md`. |
| Arma, escuta, mas nunca acorda com a frase falada em português | o modelo KWS do sherpa é só inglês; "Hermes" pronunciado "Érmes" não casa com os tokens BPE e nem grafia fonética nem limiar baixo resolvem | validar primeiro uma gravação real no detector; pronúncia inglesa é hipótese, não correção comprovada. Se falhar, avaliar motor/modelo compatível com a fala desejada, sem ativá-lo antes de passar no teste real. Alternativa com chave: Porcupine (`wake_word.provider porcupine`, `wake_word.porcupine.keyword <caminho .ppn>`, `PORCUPINE_ACCESS_KEY` no `.env` — o usuário cola a chave, nunca pelo chat). O engine do Hermes chama `pvporcupine.create` sem `model_path`, então só carrega `.ppn` criado com idioma **English**; para aproximar o sotaque, crie a palavra em inglês com grafia fonética ("Ermes"). `.ppn` em português exige patch no código (perdido a cada `hermes update`). |
| Acorda, mas a resposta não tem nada a ver | STT local transcreveu errado; o `base` erra muito em PT-BR e o VAD corta fala | `hermes config set stt.local.model small` (download único de centenas de MB; primeira resposta demora). |
| Gravação avulsa (clique no mic do composer) funciona, mas "Start voice conversation" não capta nada e o wake word para de acordar | o app (Chromium, `autoGainControl`) baixa o volume de entrada do sistema para ~10–20%; o loop de conversa só grava acima de nível 0.075 e o detector não ouve. A gravação avulsa não tem limiar, por isso engana | `pactl get-source-volume @DEFAULT_SOURCE@` (se volta a cair depois de subir, é o AGC). Criar `~/.config/pipewire/pipewire-pulse.conf.d/90-hermes-mic-agc.conf` com `pulse.rules = [ { matches = [ { application.process.binary = "Hermes" } ] actions = { quirks = [ block-source-volume ] } } ]`, `systemctl --user restart pipewire-pulse`, `pactl set-source-volume @DEFAULT_SOURCE@ 85%`, e o usuário reabre o app (o restart derruba o stream aberto). Confirmar o binário com `pactl list source-outputs \| grep process.binary`. |
| Quer STT de nuvem que o Hermes não tem nativo (ex.: Deepgram) | built-ins são só local/groq/openai/mistral/xai; o resto entra como provedor `type: command` | Receita em `references/stt-provedor-command.md`. Registre sem ativar; só troque `stt.provider` depois de transcrever um áudio real com a chave. |
| Resposta aparece escrita mas não é falada | confira `voice.auto_tts` ("Ler respostas em voz alta" no menu de voz do composer) | ligar pelo menu ou `hermes config set voice.auto_tts true`; pergunte ao usuário se viu o texto antes de concluir. |

## Pitfalls

- **Use áudio real antes de recomendar pronúncia ou declarar a ativação pronta.** Vozes Edge
  PT-BR/EN servem como triagem, não validam a voz do usuário. Se o ditado funciona mas a wake word
  falha, confirme entrada/captura e reproduza a gravação real no detector com o limiar atual;
  não insista em pronúncia inglesa porque uma voz sintética acionou. Antes de pedir reenvio,
  procure a mídia recente no cache e confirme seu conteúdo com STT local: texto transcrito no
  chat não significa que o áudio original esteja indisponível. Receita:
  `references/teste-offline-wake-word.md`.
- **Pergunte qual caminho de áudio falha antes de diagnosticar.** Gravação avulsa, conversa por voz
  e wake word usam limiares diferentes; "não funciona" de um não vale para os outros. Mensagem ditada
  chegando normal prova que o mic capta, não que o nível passa no limiar da conversa.
- **Volume que você subiu e voltou a cair é AGC, não a voz do usuário.** Releia o volume 1–2 min depois de
  ajustar; se caiu, bloqueie com a quirk do PipeWire em vez de só subir de novo.
- **"Ficou em silêncio" raramente é silêncio.** O log quase sempre mostra que o ciclo rodou com
  transcrição errada. Mostre ao usuário o texto transcrito e a resposta antes de mudar config.
- **Não anuncie "funcionou" porque a checagem interna passou.** Ela valida dependências e
  credenciais, não o áudio real. O usuário testa no microfone; o relato dele é a prova.
- **Palavra única dispara mais por engano que frase de duas palavras.** Avise ao trocar; o ajuste é
  `wake_word.sensitivity` (sherpa: limiar = 0.05 + 0.4 × sensitivity).
- **STT melhor não conserta wake word.** O detector da palavra de ativação roda local (sherpa,
  openWakeWord, Porcupine) e não aceita provedor de nuvem; trocar o STT só melhora o que é
  entendido depois de acordar. Diga isso quando o pedido for "põe o Deepgram pra reconhecer Hermes".
- **Não ative provedor que depende de chave ausente.** Trocar `stt.provider`/`tts.provider` antes
  da chave existir quebra o caminho que hoje funciona; registre, teste, só então ative.
- **Teste de detector fora do venv do Hermes:** o venv recusa instalação preguiçosa de fora do
  processo dele. Use um venv descartável em `$TMPDIR` (ver reference).

## Verification

- `check_wake_word_requirements()` retorna `available: True` com `hint` vazio.
- `text_to_speech_tool('teste')` retorna `success: true` com o provedor esperado.
- Depois do teste do usuário, o log mostra `phrase detected` e `Transcribed`, e a sessão criada tem a
  frase dele transcrita corretamente.

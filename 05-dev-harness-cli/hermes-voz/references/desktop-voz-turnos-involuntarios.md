# Desktop: comandos involuntários no loop de voz

- Distinga falso wake de falso turno: conte `phrase detected`/`wake.detected` e compare com `tui prompt accepted`. Turnos extras sem novo wake pertencem ao loop de conversa/STT/barge-in, não ao Vosk.
- Confira a preferência local `hermes.desktop.autoSpeakReplies` pelo controle "Read replies aloud". `voice.auto_tts` só migra uma vez; não sobrescreva uma escolha persistida para corrigir ausência de TTS.
- Não interprete duração de 12 s como fala reconhecida: o recorder possui idleSilenceMs de 12 s. Examine heardSpeech e o VAD antes de ajustar volume ou limiar.
- Exija fala sustentada para marcar heardSpeech e para reiniciar a espera por silêncio. Pico único não comprova fala; preserve testes de pico isolado, fala sustentada e ruído após fala. A confirmação de 300 ms não resolve automaticamente eco ou captura de barge-in.
- Não filtre transcrições curtas por blacklist nem por duração retida pelo VAD: isso elimina comandos legítimos. Investigue eco TTS separadamente, sem capturar áudio ambiente sem consentimento.
- Verifique o renderer empacotado com a API ASAR e compare bytes com dist; confirme a constante e seus usos no minificado, pois o bundler pode substituir `>=300` por `>=LX`.
- Ao empacotar árvore dirty, declare mudanças extras incluídas e rode seus testes. Preserve o pacote anterior em diretório de rollback, troque após o backend antigo sair e confirme BACKEND_READY, wake.start vosk e PIDs dos serviços preservados. Build aprovado não substitui teste de silêncio real pelo usuário.

# Teste offline de wake word (sem microfone)

Objetivo: saber se uma frase vai ser detectada **antes** de mandar o usuário testar. Gera a frase
com vozes sintéticas (PT-BR e EN) e roda os detectores sherpa e openWakeWord sobre os WAVs.

## 1. Ambiente descartável

O venv do Hermes recusa instalar extras quando chamado de fora do processo dele, então use um venv
próprio no scratch:

```bash
cd $TMPDIR && mkdir -p kws && cd kws
uv venv -q .v
uv pip install -q -p .v/bin/python sherpa-onnx numpy sentencepiece pypinyin pyopen-wakeword edge-tts
```

`text2token` do sherpa exige `sentencepiece` **e** `pypinyin`, mesmo para inglês.

## 2. Gerar os áudios (16 kHz mono)

```bash
FF=$(ls -d ~/.hermes/tools/ffmpeg-*/bin/ffmpeg | head -1)   # ou ffmpeg do sistema
for v in pt-BR-AntonioNeural pt-BR-FranciscaNeural en-US-GuyNeural; do
  for t in "Hermes" "Hey Hermes"; do n="${v}_${t// /_}"
    .v/bin/edge-tts -v $v -t "$t" --write-media $n.mp3
    $FF -loglevel error -y -i $n.mp3 -ar 16000 -ac 1 $n.wav
  done; done
```

## 3. sherpa (frase livre)

Modelo baixado pelo Hermes em `~/.hermes/cache/wakewords/sherpa-onnx-kws-zipformer-gigaspeech-*`.

```python
# t.py  uso: .v/bin/python t.py "frase1,frase2" 0.29 *.wav
import sys, os, glob, wave, tempfile, numpy as np, sherpa_onnx
from sherpa_onnx import text2token
d = glob.glob(os.path.expanduser("~/.hermes/cache/wakewords/sherpa-onnx-kws-*"))[0]
f = lambda p: sorted(x for x in glob.glob(f"{d}/{p}-*.onnx") if not x.endswith("8.onnx"))[0]
phrases, thr = sys.argv[1].split(","), float(sys.argv[2])
toks = text2token([p.upper() for p in phrases], tokens=f"{d}/tokens.txt", tokens_type="bpe", bpe_model=f"{d}/bpe.model")
kw = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
for p, t in zip(phrases, toks): kw.write(" ".join(t) + f" @{p.upper().replace(' ','_')}\n")
kw.close()
for wav in sys.argv[3:]:
    s = sherpa_onnx.KeywordSpotter(tokens=f"{d}/tokens.txt", encoder=f("encoder"), decoder=f("decoder"),
        joiner=f("joiner"), keywords_file=kw.name, keywords_threshold=thr, num_threads=1)
    st = s.create_stream(); w = wave.open(wav)
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    a = np.concatenate([np.zeros(8000, np.float32), a, np.zeros(16000, np.float32)])
    hits = []
    for i in range(0, len(a), 1280):
        st.accept_waveform(16000, a[i:i+1280])
        while s.is_ready(st):
            s.decode_stream(st); r = s.get_result(st)
            if r: hits.append(r); s.reset_stream(st)
    print(wav, hits)
```

Limiar real do Hermes: `0.05 + 0.4 × wake_word.sensitivity` (0.6 → 0.29).

## 4. openWakeWord (modelo "hey hermes" embarcado)

```python
# o.py  uso: .v/bin/python o.py *.wav — dispara com score >= sensitivity em N frames seguidos
import sys, os, wave, numpy as np
from pyopen_wakeword import OpenWakeWord, OpenWakeWordFeatures
M = os.path.expanduser("~/.hermes/hermes-agent/tools/wakewords/hey_hermes.tflite")
for wav in sys.argv[1:]:
    feats, m = OpenWakeWordFeatures.from_builtin(), OpenWakeWord.from_model(M)
    w = wave.open(wav); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    a = np.concatenate([np.zeros(16000, np.int16), a, np.zeros(24000, np.int16)])
    best = over = 0
    for i in range(0, len(a), 1280):
        for e in feats.process_streaming(a[i:i+1280].tobytes()):
            for sc in m.process_streaming(e): best = max(best, sc); over += sc >= 0.6
    print(f"{wav}: max={best:.3f} frames>=0.6: {over}")
```

## Testar gravação real recebida pelo chat

1. Procure a mídia recente em `$HERMES_HOME/cache/audio/` antes de pedir outro envio; um áudio
   pode aparecer na conversa apenas como transcrição, mas continuar disponível no cache.
2. Confirme a gravação pelo conteúdo, não só pela data. Transcreva localmente com o modelo
   Faster-Whisper já instalado, `language='pt'` e `local_files_only=True`; não envie áudio pessoal
   a um provedor externo para diagnosticar um detector local.
3. Converta o arquivo selecionado para WAV PCM mono de 16 kHz com
   `ffmpeg -loglevel error -y -i <entrada> -ar 16000 -ac 1 <scratch>/user-wake.wav`.
4. Passe esse WAV ao script `t.py` acima com a frase e o limiar efetivamente configurados.
   Use as dependências existentes no runtime descoberto por
   `hermes --print-runtime-command --module tools.wake_word`; crie o ambiente descartável apenas
   se precisar de outro detector. Não presuma que existe um venv fixo.
5. Compare os dois resultados: STT correto e `hits=[]` isolam a falha de reconhecimento do
   detector para aquela gravação; não provam defeito no Whisper nem que todas as pronúncias falham.
   Preserve esse áudio como fixture local para comparar candidatos antes de alterar a configuração.

## Vosk PT-BR: reconhecimento restrito e validação streaming

1. Teste em venv descartável com `vosk` e `numpy`, WAV mono PCM16/16 kHz e modelo PT compatível. Confira licença e checksum do modelo; não trate todos os modelos portugueses como equivalentes. Para `vosk-model-small-pt-0.3`, confirme a palavra com `model.vosk_model_find_word('hermes')` antes de usar gramática: palavras OOV não serão reconhecidas.
2. Compare `KaldiRecognizer(model, 16000)` com `KaldiRecognizer(model, 16000, json.dumps(['ei hermes', 'hermes', '[unk]']))`, usando `SetWords(True)`. Decodificação livre pode falhar enquanto a restrita reconhece; confiança alta na gramática restrita não prova acerto, pois o espaço de alternativas foi reduzido.
3. Confira os tokens realmente emitidos: o reconhecedor pode omitir a interjeição `ei`. Se o engine aceitar o nome sozinho, declare essa semântica mesmo quando a configuração exibir `ei hermes`; não prometa uma frase de duas palavras obrigatória.
4. Antes de integrar, teste negativos que competem foneticamente e frases com o nome no início, meio e fim, além de silêncio, ruído e fala contínua. Reserve um conjunto não usado no ajuste. Avalie o engine streaming efetivo, não apenas `FinalResult` de arquivos isolados; silêncio artificial e reset a cada arquivo escondem falhas em conversas longas.
5. Para detectar invocação isolada, valide segmento exato, confiança, pausa anterior e ausência de fala logo depois. Uma gramática restrita pode esconder fala posterior até emitir `[unk]`; a energia relativa à palavra ajuda a cancelar candidatos antes disso. No provider implementado, a confirmação usa ~0.6 s, confiança `0.5 + 0.4 × sensitivity` e cancelamento por energia após a palavra. Confira o código atual antes de reutilizar parâmetros e teste ganho/ruído: heurísticas não são garantias universais.
6. Exercite `start_listening(external_audio=True)` → `feed_audio` com o engine real, `HERMES_HOME` temporário e lock isolado, sem disputar o detector do Desktop. Envie em tempo real e use frames ou lotes múltiplos do `detector_frame_info()['frame_length']`: envio acelerado estoura a fila e chunks curtos são preenchidos com zeros, alterando o sinal. Separe disparos do engine dos callbacks do loop, que têm cooldown.
7. Integre o provider em resolução, probe de requisitos, extra/anchor PM, defaults e opções da UI. Não use a ordem automática de preferência como catálogo completo se o provider for explícito apenas. Teste schema e markers do extra junto com a construção real; depois siga `desktop-voz-implantacao.md` para ativação.

Relate contagens de positivos/negativos e sua origem; zero falsos positivos em TTS não estima a taxa em ambiente real. Não transforme gravação reproduzida offline em prova de microfone, restauração de janela ou TTS audível.

## Leitura do resultado

- Voz sintética é aproximação: detectar nela não garante a voz do usuário, mas **não detectar em
  nenhuma voz PT-BR** já basta para não prometer a frase.
- Resultado observado com o modelo KWS gigaspeech: "hermes" só casa com pronúncia inglesa; nenhuma
  voz PT-BR casa, nem com grafias fonéticas ("ermes", "air mess") nem limiar 0.08. O openWakeWord
  "hey hermes" casa forte em EN e só de forma instável em PT-BR.

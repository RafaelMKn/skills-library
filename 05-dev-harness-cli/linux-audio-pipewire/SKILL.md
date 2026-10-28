---
name: linux-audio-pipewire
description: "Corrige áudio no Linux — PipeWire, mic, Bluetooth, ganho."
---

# Áudio no Linux (PipeWire / WirePlumber / BlueZ)

Diagnóstico e correção de áudio em desktop Linux. Quase nunca é driver — é perfil,
roteamento ou ganho.

**Use quando:** microfone ruim ou chiando, som estourado, headset Bluetooth com qualidade
baixa quando o mic está em uso, fonte/saída padrão errada, app pegando o dispositivo errado,
ou pedido de "atualizar/baixar driver de áudio".

## Regra de entrada: recusar a premissa de "driver"

Pedido de "baixar/atualizar driver de áudio" no Linux é premissa errada em quase todos os
casos: HDA Intel/Realtek, AMD e BlueZ são drivers de kernel, já presentes e atualizados
com o kernel. Não existe pacote pra baixar do site do fabricante.

Diga isso na primeira resposta, com o motivo, **antes** de sair procurando qualquer coisa —
não execute um pedido que você sabe que não vai resolver. Usuário vindo do Windows enquadra
qualquer defeito de áudio como "driver" porque lá o painel Realtek de fato mudava o
comportamento; aqui o equivalente é configuração do PipeWire e ganho do ALSA.

Exceção real (raríssima): codec muito novo que precisa de firmware (`sof-firmware`,
`alsa-firmware`) ou de quirk `hda-model`. Só considere isso se o dispositivo **não aparece**
em `/proc/asound/cards` — não quando ele aparece e soa mal.

## Procedimento

### 1. Levantar o estado real (um lote só)

```bash
pactl info                      # servidor, sink/source padrão
pactl list short sinks
pactl list short sources
pactl list cards                # perfis disponíveis e Perfil ativo
cat /proc/asound/cards          # hardware visto pelo kernel
systemctl --user is-active pipewire pipewire-pulse wireplumber
```

O par que resolve a maioria dos casos: **qual é a fonte padrão** (`pactl get-default-source`)
e **qual é o perfil ativo** de cada card. Leia os dois antes de teorizar.

### 2. Ler o ganho do microfone no ALSA, não só no PulseAudio

`pactl` mostra o volume do software; o estrago costuma estar no ganho de hardware:

```bash
amixer -c <N> scontrols | grep -iE "mic|capture|boost"
amixer -c <N> sget 'Internal Mic Boost'
amixer -c <N> sget 'Capture'
```

O índice `<N>` vem de `/proc/asound/cards` — não assuma 0.

**Boost e Capture somam.** `Internal Mic Boost 3/3` (+30 dB) com `Capture 63/63` (+30 dB) são
60 dB empilhados num mic de notebook: isso não é volume, é clipping e chiado — a causa número
um de "o microfone ficou horrível depois que saí do Windows". O driver Realtek do Windows
limitava esse ganho por conta própria; no Linux ele fica cru no talo.

### 3. Medir antes e depois — nunca calibrar de ouvido no escuro

Grave e meça; não afirme que melhorou sem número:

```bash
timeout 6 parecord --device=<source> --file-format=wav /tmp/teste.wav
ffmpeg -hide_banner -ss 0.5 -i /tmp/teste.wav -af volumedetect -f null /dev/null 2>&1 \
  | grep -E "mean_volume|max_volume"
```

Interpretação:

| mean_volume | Leitura |
|---|---|
| acima de −10 dB com max em 0.0 dB | clipping contínuo — baixar ganho |
| −18 a −30 dB | faixa saudável de fala |
| abaixo de −50 dB | surdo demais — subir ganho |

Use `-ss 0.5` para descartar o pop de abertura do stream: os primeiros milissegundos do
`parecord` frequentemente contêm um transiente de nível máximo que envenena o `max_volume`
de uma gravação que na verdade está baixa.

Ajuste em passos e re-meça (`Capture` 63 → 45 → 28 → 24). Converge em duas ou três iterações.

### 4. Bluetooth: A2DP vs HFP é limite de protocolo, não defeito

Headset Bluetooth **não** transmite microfone e áudio hi-fi ao mesmo tempo. Ou:

- **A2DP** (`a2dp-sink`, AAC/SBC/SBC-XQ) — estéreo bom, **sem microfone**;
- **HSP/HFP** (`headset-head-unit`, mSBC/CVSD) — microfone funciona, som cai pra mono 16 kHz.

Se a fonte padrão é o mic do headset, todo app que abre o microfone faz o WirePlumber trocar
A2DP → HFP e a escuta vira lata. O sintoma "usando os dois juntos fica ruim" é sempre isso.

Correção padrão — mic separado (interno ou USB) e headset travado em A2DP:

```bash
pactl set-default-source alsa_input.<card>.analog-stereo
```

`~/.config/wireplumber/wireplumber.conf.d/51-bt-no-autoswitch.conf`:

```
wireplumber.settings = {
  bluetooth.autoswitch-to-headset-profile = false
}
```

```bash
systemctl --user restart wireplumber
wpctl settings bluetooth.autoswitch-to-headset-profile   # confirmar: Value: false
```

Detalhes de perfil, codec e recuperação em `references/bluetooth-perfis.md`.

### 5. Persistir e verificar

- Configuração do WirePlumber em `wireplumber.conf.d/` sobrevive a reboot e a update.
- Níveis do `amixer` **não** necessariamente: `alsactl store` precisa de root. Se não puder
  rodar, **diga que pode não sobreviver ao reboot** em vez de afirmar que ficou permanente.
- Feche relendo o estado (`get-default-sink`, `get-default-source`, `Perfil ativo`, codec) e
  reporte o que foi lido, não o que foi mandado.

## Armadilhas

- **`set-card-profile` falha com "Não existe tal entidade" quando o perfil sumiu da lista.**
  O BlueZ às vezes negocia só HFP na conexão e os perfis A2DP nem aparecem em `pactl list cards`.
  Não insista no comando: desconecte e reconecte o dispositivo
  (`bluetoothctl disconnect <MAC>` / `connect <MAC>`, ~4 s entre os dois) para forçar
  a renegociação — os perfis A2DP voltam.
- **`systemctl --user restart wireplumber` pode deixar o headset preso em HFP** mesmo com o
  autoswitch desligado, porque o perfil é restaurado do estado salvo. Confira o `Perfil ativo`
  depois de todo restart.
- **Salve os valores originais antes de mexer** (fonte/saída padrão + `amixer` de boost e
  capture) num arquivo, e informe o caminho ao usuário. Ganho de mic é fácil de piorar às cegas.
- **Sem `sox` no Fedora**, use `ffmpeg -af volumedetect` — está instalado por padrão em
  máquina que edita vídeo.
- **Não pare no ajuste de software quando o hardware é o teto.** Mic de notebook calibrado
  ainda é mic de notebook; se o uso é locução, diga que o caminho é mic USB. Mic de headset
  Bluetooth em HFP nunca vai servir pra gravação — é limite do protocolo, não de configuração.

## Atualização do sistema e reinicialização no Fedora

- Consulte `dnf --refresh check-upgrade kernel-core kernel-modules 'pipewire*' wireplumber 'alsa*' linux-firmware` antes de afirmar que está atualizado. Código 100 indica atualizações disponíveis, não falha.
- Só atualize e reinicie quando autorizado. No desktop, se `sudo -n true` exigir senha, use `pkexec /usr/bin/dnf upgrade --refresh -y`: a autorização ocorre na janela gráfica do Polkit, nunca recebendo ou digitando senha pelo chat.
- Para atualização completa autorizada, confira também `flatpak update --user --noninteractive -y` e `flatpak update --system --noninteractive -y`. Não confunda pacotes de firmware com atualização de BIOS/UEFI.
- Espere o DNF terminar, inclusive scriptlets de kernel e DKMS. Antes do reboot, confira versões com `rpm -q`, pendências com `dnf check-upgrade`, existência de vmlinuz/initramfs e kernel padrão com `pkexec /usr/bin/grubby --default-kernel`. `grubby` sem root pode imprimir `/boot` e sair com código 0 apesar de permissão negada; essa saída não valida o kernel padrão.
- Avise para salvar arquivos antes de reiniciar. Não afirme que o microfone melhorou só porque os pacotes foram atualizados: ainda exige teste de voz.

## Ferramentas complementares

- `easyeffects` — supressão de ruído (RNNoise), compressor, gate para o mic. Considere quando
  o nível já está calibrado e o problema restante é ruído de fundo, não ganho.
- `wpctl status` — visão em árvore de nós e dispositivos, mais legível que `pactl` para
  entender roteamento.

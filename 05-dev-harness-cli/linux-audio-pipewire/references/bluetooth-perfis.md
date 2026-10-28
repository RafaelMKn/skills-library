# Perfis Bluetooth de áudio (BlueZ + WirePlumber)

## Os perfis e o que cada um entrega

| Perfil (`pactl list cards`) | Codec | Saída | Microfone | Uso |
|---|---|---|---|---|
| `a2dp-sink` | AAC | estéreo 44.1/48 kHz | não | padrão para escutar |
| `a2dp-sink-sbc_xq` | SBC-XQ | estéreo, bitrate alto | não | alternativa quando AAC falha |
| `a2dp-sink-sbc` | SBC | estéreo, baseline | não | fallback universal |
| `headset-head-unit` | mSBC | mono 16 kHz | sim | chamada |
| `headset-head-unit-cvsd` | CVSD | mono 8 kHz | sim | pior caso |
| `off` | — | — | — | desligado |

Não existe perfil com áudio hi-fi **e** microfone. É limitação do transporte Bluetooth
clássico (A2DP e SCO/eSCO não coexistem), não do Linux nem do fabricante. LE Audio / LC3
resolve isso no papel, mas exige suporte no headset e no adaptador — verifique antes de
prometer.

## Comandos

```bash
# perfis disponíveis e ativo
pactl list cards | grep -A200 bluez_card | sed -n '/Perfis:/,/Perfil ativo/p'

# forçar A2DP
pactl set-card-profile bluez_card.<MAC_COM_UNDERSCORES> a2dp-sink

# codec realmente em uso
pactl list sinks | grep -E "api.bluez5.codec|api.bluez5.profile"

# renegociar a conexão (recupera perfis A2DP ausentes)
bluetoothctl disconnect <MAC>; sleep 4; bluetoothctl connect <MAC>
```

O nome do card usa MAC com underscore (`bluez_card.40_58_99_1C_52_28`); o source às vezes usa
MAC com dois-pontos (`bluez_input.40:58:99:1C:52:28`). Copie do `pactl list short`, não digite.

## Diagnóstico rápido por sintoma

- **Som ótimo até abrir o Meet/Discord, aí vira lata** → autoswitch para HFP. Desligue o
  autoswitch e use outro microfone.
- **Perfis A2DP não aparecem na lista** → a conexão foi negociada só como HFP. Reconecte.
- **Voltou a HFP depois do reboot ou do restart do wireplumber** → estado salvo do dispositivo.
  Confirme o `Perfil ativo` após cada restart; force `a2dp-sink` se necessário.
- **AAC indisponível / só SBC** → nem todo headset anuncia AAC; `a2dp-sink-sbc_xq` é o melhor
  substituto disponível.

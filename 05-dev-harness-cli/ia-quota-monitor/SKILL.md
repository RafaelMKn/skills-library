---
name: ia-quota-monitor
description: "Monitor, consultar e gerenciar cotas e limites de taxa de IA (Claude Code, OpenAI Codex e Google Antigravity/Gemini) no Linux e KDE Plasma."
version: 1.0.0
author: Antigravity + Hermes
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Quota-Monitor, Rate-Limits, Claude, Codex, Antigravity, Gemini, KDE, Plasmoid, Systemd, HUD]
    related_skills: [claude-code, codex, hermes-agent]
---

# IA Quota Monitor — Hermes Skill

Esta skill fornece instruções completas para consultar, diagnosticar e gerenciar o **IA Quota Monitor**, sistema que monitora em tempo real os limites de utilização e tempos de reset das três principais IAs de desenvolvimento do usuário:
- **Anthropic Claude (Claude Code)**
- **OpenAI Codex (Codex CLI)**
- **Google Antigravity (Gemini Cloud Code)**

O sistema opera através de um coletor em segundo plano (`ai-usage-monitor`), um serviço/timer `systemd --user`, um cache atômico (`~/.cache/ai-usage.json`) e um widget nativo para **KDE Plasma 6** na barra superior.

---

## 📍 Localização dos Componentes

| Componente | Caminho no Sistema |
| :--- | :--- |
| **Repositório do Projeto** | `~/Documentos/dev/IA Quota Monitor` |
| **Script CLI Executável** | `~/.local/bin/ai-usage-monitor` |
| **Cache JSON de Estado** | `~/.cache/ai-usage.json` |
| **Systemd Service** | `~/.config/systemd/user/ai-usage-monitor.service` |
| **Systemd Timer (3 min)** | `~/.config/systemd/user/ai-usage-monitor.timer` |
| **Plasmoid KDE Plasma 6** | `~/.local/share/plasma/plasmoids/org.kde.plasma.aiusage` |

---

## 💻 Como Consultar as Cotas no Terminal

O agente pode obter os dados de uso a qualquer momento através do CLI:

### 1. Resumo Visual (Tabela Colorida)
```bash
ai-usage-monitor
```

### 2. Leitura Rápida em JSON Puro
```bash
ai-usage-monitor --json
# Ou ler diretamente o cache pré-calculado:
cat ~/.cache/ai-usage.json
```

### Estrutura do JSON de Resposta:
```json
{
  "updated_at": 1790173000,
  "updated_at_str": "13:16:00",
  "claude": {
    "status": "ok",
    "five_hour_percent": 58.0,
    "five_hour_resets_in": "3h 14m",
    "seven_day_percent": 38.0,
    "seven_day_resets_in": "3d 8h"
  },
  "codex": {
    "status": "ok",
    "primary_percent": 100,
    "primary_resets_in": "2h 45m",
    "secondary_percent": 75,
    "reset_credits_available": 3,
    "limit_reached": true
  },
  "antigravity": {
    "status": "ok",
    "gemini_used_percent": 26.0,
    "gemini_remaining_percent": 74.0,
    "gemini_resets_in": "3h 05m"
  }
}
```

---

## ⚙️ Engenharia Reversa das APIs

### 1. Anthropic Claude (Claude Code)
- **Token:** `~/.claude/.credentials.json` -> `claudeAiOauth.accessToken`
- **Endpoint:** `GET https://api.anthropic.com/api/oauth/usage`
- **Headers:**
  - `Authorization: Bearer <accessToken>`
  - `anthropic-beta: oauth-2025-04-20`
  - `User-Agent: Claude-Code/0.2.29`

### 2. OpenAI Codex
- **Método:** Inicia o processo headless `codex app-server --stdio` e comunica via JSON-RPC.
- **Handshake:**
  1. `{"method": "initialize", "params": {"clientInfo": {"name": "ai-usage", "version": "1.0"}}}`
  2. `{"method": "initialized", "params": {}}`
  3. `{"method": "account/rateLimits/read", "params": {}}`
- **Retorno:** Janela primária (300 min), janela secundária (10080 min) e contagem de créditos de reset gratuito (`rateLimitResetCredits.availableCount`).

### 3. Google Antigravity
- **Token:** Busca no keyring nativo: `secret-tool search service gemini` (chave `token.access_token`).
- **Endpoint:** `POST https://daily-cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels`
- **Body:** `{}`
- **Retorno:** Dicionário de modelos com `quotaInfo.remainingFraction` e `quotaInfo.resetTime`.

---

## 🔧 Manutenção e Solução de Problemas

### Forçar Atualização Imediata
```bash
ai-usage-monitor -q
```

### Verificar o Temporizador Systemd
```bash
systemctl --user status ai-usage-monitor.timer
systemctl --user list-timers ai-usage-monitor.timer
```

### Reiniciar ou Recarregar o Plasmoid no KDE Plasma
Se fizer alterações no arquivo `main.qml` ou nos assets:
```bash
kbuildsycoca6 2>/dev/null
systemctl --user restart plasma-plasmashell.service
```

### Reinstalar do Código-Fonte
```bash
cd "$HOME/Documentos/dev/IA Quota Monitor"
./install.sh
```

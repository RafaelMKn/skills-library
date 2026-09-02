# openclaw-agent-creator

> Expert guide for designing and building OpenClaw agents. Use this skill when asked to create, configure, or optimize an OpenClaw agent, modify its SOUL/AGENTS/IDENTITY/TOOLS/MEMORY/BOOTSTRAP files, or adjust openclaw.json channel parameters.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **openclaw-agent-creator**.


## 📁 Estrutura de Arquivos

- [SKILL.md](SKILL.md)
- [references\openclaw_docs.md](references\openclaw_docs.md)

---

## 🛠️ Conteúdo da Skill

# OpenClaw Agent Creator Skill

This skill is the **deep developer guide** for creating, scaffolding, and configuring production-ready **OpenClaw** agents.

---

## 1. Overview of OpenClaw Agent Anatomy

An OpenClaw agent is defined by a directory containing six specialized Markdown files, which separate the model's instructions into manageable, contextual layers:

```text
agent_directory/
├── SOUL.md         # Identity, voice, core ethics, and conversational limits (The Persona)
├── IDENTITY.md     # TECHNICAL specifications: ID, hardware environment, active channels
├── AGENTS.md       # Standard Operating Procedure (SOP): exact steps to take on session startup
├── TOOLS.md        # Available tools/skills description and Quality Assurance checklist
├── MEMORY.md       # Few-shot examples (Golden Standards) and dynamic learning logs
└── BOOTSTRAP.md    # Commands executed on agent start (e.g. environment check)
```

And configured globally by:
*   [openclaw.json](../../templates/openclaw/openclaw.json): Defines active messaging channels, main model models, fallback paths, and custom skill folders.

---

## 2. Step-by-Step Scaffolding Guide

To create a new agent, you can use the built-in python script:
```bash
python tools/scaffold_agent.py
```
This utility copies files from the `templates/openclaw/agent_template/` folder and prompts you for details:
*   **Agent Name:** Placed in `SOUL.md` and `IDENTITY.md`.
*   **Main Role:** Placed in `SOUL.md`.
*   **Specialty:** Placed in `SOUL.md`.
*   **Output Path:** The target directory where files are written.

### Manual Customization

If writing files manually or modifying a scaffolded agent:

#### 2.1. SOUL.md Guidelines (Persona & Rules)
- **Zero-Guess Policy:** Emphasize that the agent must NEVER hallucinate or assume values (such as credentials or links). If data is missing, output `⚠️ Informações Faltantes`.
- **Tone & Style:** Keep answers direct, professional, and optimized for instant messaging (WhatsApp/Telegram).
- **No Filler:** Prohibit introductory sentences like "Entendido, irei analisar..." or "Com certeza!".

#### 2.2. IDENTITY.md Guidelines (Technical Specs)
- Define the system identifier: `openclaw-[agentname]-01`.
- Declare the execution environment: Windows PowerShell (default for the user).
- Define context parameters (e.g. max 8,000 tokens).

#### 2.3. AGENTS.md Guidelines (SOP)
- Instruct the agent to read `SOUL.md`, `TOOLS.md`, and `MEMORY.md` immediately at session start.
- Outline the pipeline: 1. Intake, 2. Gap Identification, 3. ReAct Planning, 4. Tool Execution, 5. Quality Review, 6. Direct Delivery.

#### 2.4. TOOLS.md Guidelines (Skills & QA)
- List current skills (e.g. `gemini`, `peekaboo`, `web-search`).
- Provide the QA Checklist:
  *   [ ] Is the language Brazilian Portuguese (PT-BR)?
  *   [ ] Is the code syntactically correct and free of placeholders?
  *   [ ] Are paragraphs separated by a blank line for easy reading on WhatsApp/Telegram?
  *   [ ] Have all assumptions been eliminated?

#### 2.5. MEMORY.md Guidelines (Few-Shot & Learnings)
- Maintain `Golden Standards` (highly rated prompts and their exact desired outputs).
- Instruct the agent to append dynamic learnings here if it encounters recurring patterns.

#### 2.6. BOOTSTRAP.md Guidelines (Startup script)
- Script to run at boot. Default commands:
  ```bash
  openclaw doctor
  openclaw gateway status
  ```

---

## 3. Configuring Communications (`openclaw.json`)

To enable channels for the new agent, adjust the `openclaw.json` config:
1.  **Telegram:** Set `enabled` to `true` and configure the bot token.
2.  **WhatsApp:** Set `enabled` to `true`, restrict incoming numbers via `allowFrom` if necessary, and enable `requireMention` in groups.
3.  **Model Configuration:** Define the primary execution model (default: `anthropic/claude-3-5-sonnet`) and fallback options.

---
*Parte da [Skills Library](../../README.md)*

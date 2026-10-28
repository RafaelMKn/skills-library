# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

HTML/CSS estático, sem build, publicável no GitHub Pages (resposta do Rafael, 28/10/2026). JavaScript só onde a peça exigir (ex.: herói ASCII com asciify-engine via CDN ESM).

## Users

Devs e operadores que usam harnesses de agentes de IA (Claude Code, Codex, Hermes, OpenClaw, Google Antigravity) e querem skills prontas para plugar. Chegam pelo GitHub ou por um link; o trabalho deles é achar uma skill que resolva uma tarefa e instalá-la no próprio harness em minutos.

## Product Purpose

Akmon é uma biblioteca curada de Agent Skills (pastas com SKILL.md e arquivos de apoio) organizada em categorias temáticas. Existe para que uma skill testada em produção na FluxMind possa ser reaproveitada em qualquer harness compatível. Sucesso: o visitante entende o que é, acha a categoria certa e copia o comando de instalação.

## Positioning

Skills extraídas de operação real (n8n em produção, agentes de clientes, motion, infra) e saneadas, não um catálogo agregado de terceiros. Uma pasta, vários harnesses.

## Operating Context

- Repositório: github.com/RafaelMKn/skills-library.
- Instalação documentada no README: symlink para `~/.claude/skills/` (Claude Code), `.agents/skills/` (Antigravity/Codex), `~/.hermes/skills/<categoria>/<skill>/` (Hermes/OpenClaw).
- Categorias: 01 Automação n8n/Make · 02 Design, UI, motion, 3D e vídeo · 03 Agentes e prompts · 04 Backend, APIs e banco · 05 Ferramental dev, CLI e harness · 06 Produtividade, pesquisa e docs.

## Capabilities and Constraints

- Contagem de skills em aberto: o README diz 136; em 28/10/2026 o disco tinha 174 arquivos SKILL.md (há pastas novas não commitadas). Não fixar número em material público até reconciliar.
- Conflito de nome Akmon (GitHub, npm, domínio) ainda não checado.
- Sem domínio definido.

## Brand Commitments

Fonte: docs/identidade-akmon.md (decisões de 28/10/2026, ainda não é guia final).

- Nome: Akmon (grego ákmōn, "bigorna"). Substitui "Master Skills Library".
- Herói: Hefesto martelando numa forja. Ilustração existente: `docs/Ferreiro Forjando uma Lâmina no Anvil.png` (silhueta preta sobre branco, bigorna, lâmina, faíscas). Formato final do herói em aberto (ASCII, vetor ou pintura).
- Tipografia: fonte quadrada e impactante para títulos e logotipo; família concreta e licença em aberto.
- Paleta: vermelho-laranja (metal em brasa) e preto; off-white opcional como respiro. Hex em aberto.

## Evidence on Hand

- Lista real de skills e categorias no README e nas pastas 01–06.
- Ilustração do ferreiro em docs/.
- Não existem: depoimentos, usuários citáveis, estrelas, métricas de uso, logos de clientes. Não inventar.

## Product Principles

1. Prova antes de promessa: mostrar skills reais e o comando de instalação, não adjetivos.
2. Agnóstico de harness: nenhuma ferramenta é tratada como a única.
3. Forjado em produção: a origem operacional é o diferencial, contada com fatos.
4. Instalar em minutos: o caminho da landing até o terminal é curto.

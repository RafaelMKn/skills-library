---
name: guia-contexto-projeto
description: "Use ao fazer guia de contexto, spec técnica ou tasks de v1."
version: 1.0.0
author: <autor>
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [planejamento, contexto, roadmap, docs]
    related_skills: [grill-with-docs, github, grounded-citations]
---

# Guia de contexto e plano de versão de um projeto

Pedido típico: "puxa os docs recentes do projeto X e faz um guia do contexto total + objetivo + tasks
para concluir a v1". O entregável é UM documento versionável no repo (`docs/guia-<versao>.md`), com
fonte para cada afirmação e decisões separadas de propostas.

## When to Use

- "Faz um guia do contexto do projeto X", "objetivo e tasks para fechar a v1", "onde paramos no X".
- "Finaliza a spec técnica" / "mapeia o projeto e o que falta decidir" a partir de uma proposta
  funcional já fechada → entregável `docs/spec-tecnica.md` no formato de
  `references/spec-tecnica.md` (mesmo procedimento abaixo, passo 6 troca de formato).
- Projeto com docs espalhados (repo, pastas locais, conversas) e ainda sem plano de execução.
- Não é para decidir escopo em aberto com o usuário (isso é `grilling`/`grill-with-docs`) nem para
  implementar as tasks (isso é a skill de implementação do seu ambiente).

## Procedure

1. **Localizar o projeto pelo nome e pelos apelidos.** Projeto do usuário costuma ter nome antigo no
   repo e nome novo no produto. Busque em todas as contas:
   `gh repo list --limit 200 --json nameWithOwner,description,updatedAt` + o mesmo para cada
   `gh org list`, filtrando pelos apelidos. Depois `ls <workspace> | grep -i <apelidos>`.
2. **Inventariar TODAS as fontes antes de ler a fundo**, porque a decisão mais nova raramente está
   no repo aberto:
   - clones paralelos e pastas sem git (comparar com `diff` e `ls --time-style` — o mais novo vence);
   - arquivos fora do commit (`git status --short`);
   - contexto externo que o README do repo cita (skills, pastas do agent-creator-hub);
   - **conversas anteriores do Hermes** (passo 3) — obrigatório, não opcional.
3. **Minerar decisões das sessões passadas.** `session_search(query="<nome>")` e com os apelidos;
   se a busca de sessões não estiver disponível, `scripts/buscar_sessoes.py <termo> [...]` (sqlite
   só leitura: casa por `sessions.cwd` e por conteúdo, lista id/data/título).
   Para entregar o histórico a subagentes, exporte a sessão de origem para um `.md` no scratch com
   `scripts/buscar_sessoes.py --dump <session_id> <saida.md>` — cada bloco sai rotulado com o papel
   (user / assistant / clarify), para o filho não confundir análise do agente com fala do cliente.
   As respostas do usuário ficam nos resultados de `clarify` (role `tool`), que a busca por padrão não
   mostra: extraia com `scripts/extrair_decisoes_sessao.py <session_id>` (lê `~/.hermes/state.db` só
   leitura e lista pergunta → resposta, sem duplicatas). Decisão que só existe em conversa entra no
   guia como tabela própria (C1, C2…) citando a sessão, e vira task "levar para o doc canônico".
4. **Fan-out read-only** (briefings e rotas de modelo conforme a skill de delegação do seu ambiente): um filho por
   área — (a) negócio + specs arquivadas: válido × superado × contradições; (b) design/mockups:
   telas, estados desenhados × faltando, tokens; (c) contexto externo reaproveitável e riscos.
   Exija `arquivo:linha` em toda afirmação e `output_schema` com listas.
5. **Conferir o filho por amostragem** antes de usar: `sed -n '<linha>p'` em ~10–15 citações. Linha
   errada se corrige no guia; afirmação sem fonte sai. Para filho de pesquisa web, reabra as URLs
   das afirmações que sustentam decisão: se `web_extract` truncar o trecho, baixe com
   `curl -sL -A "Mozilla/5.0" <url>`, tire as tags e `grep` o termo. URL 404 ou página que não diz o
   que o filho afirmou → a afirmação entra como `[não confirmado]` (vira caso de teste), nunca como fato.
6. **Escrever o guia** nesta ordem: o que é (glossário, stack, histórico em uma linha) → decisões
   vindas de conversa → o que segue valendo → contradições/riscos (com recomendação marcada como
   opinião) → contexto externo reaproveitável → objetivo da versão com critério de aceite
   verificável → decisões pendentes D# com opções e recomendação → tasks por marco (T#.#, cada uma
   com entregável e **Aceite:** verificável, dependências entre colchetes) → ordem/paralelismo.
7. **Não commitar sem pedido.** Entregue caminho, o que precisa de decisão humana e o próximo passo.

## Pitfalls

- **Pergunta sem resposta não é decisão.** Se uma sessão terminou esperando escolha (ex.: mocks
  gerados sem escolha registrada), registre como pendente; não promova a variação "mais provável".
- **Resposta que não responde à pergunta continua em aberto.** Confira se a resposta do `clarify`
  bate com o que foi perguntado ("como orquestrar?" respondido com o modelo de IA não decide a
  orquestração).
- **Cruze decisões entre si atrás de deadlock.** Duas regras confirmadas podem travar o fluxo juntas
  (ex.: "só promove com todos visíveis" + "sem regenerar" trava quando um item falha). Aponte como
  pergunta, não resolva calado.
- **Doc de design/spec antigo convive com o pivot.** Liste explicitamente o que no DESIGN/mockups
  ainda reflete a plataforma ou o nome anterior, para não virar task errada.
- **Fala do cliente só vale se estiver na transcrição/mensagem dele.** Subagente lendo um dump de
  sessão atribui ao cliente frases que eram análise do agente; confira cada "o cliente pediu X" na
  linha de origem e reescreva a divergência só com o que ele disse.
- **Proposta entregue ≠ proposta validada.** Antes de especificar em cima de uma proposta enviada ao
  cliente, procure registro do aceite dele; sem registro, isso vira D0 bloqueando tudo, no topo do doc.
- **Antes de concluir "não achei nada mais novo", rode o passo 3.** O usuário espera que decisões
  tomadas em chat sejam encontradas sem ele precisar apontar.

## Arquivos de apoio

- `references/spec-tecnica.md` — esqueleto e regras da spec técnica (pré-condições, legenda de fonte,
  D# com quem decide e o que bloqueia, agrupamento da entrega).
- `scripts/extrair_decisoes_sessao.py` — pergunta → resposta dos `clarify` de uma sessão.
- `scripts/buscar_sessoes.py` — achar sessões por termo/cwd e exportar uma sessão rotulada.

## Verification

- Toda afirmação sobre doc tem `arquivo:linha`; toda decisão de conversa cita a sessão.
- Cada task tem **Aceite:** verificável; cada D# tem opções e recomendação.
- `git status --short` mostra só o guia novo (nenhum doc alterado sem pedido).

---
name: doit
description: "Use when told /doit: implement approved doc via subagents."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagents, git, worktree, orchestration]
    related_skills: [esquadrao-agentes, requesting-code-review, systematic-debugging]
---

# /doit — Implementar Documento Aprovado com Multiagentes

Protocolo rigoroso de orquestração multiagente para implementar especificações técnicas, planos ou issues aprovadas. O agente principal atua estritamente como **orquestrador**: faz recon, decomposição em grafo de dependências (DAG), provisionamento de worktrees isolados, delegação, verificação ativa de evidências e integração. **Toda implementação de código é delegada** a subagentes via `delegate_task`.

A entrega final consiste exclusivamente em branch de integração local + commits atômicos + evidências verificáveis de teste e build. **Nunca fazer push, abrir PR, merge em branch principal ou deploy sem comando explícito do usuário.**

## When to Use

- O usuário executa `/doit` (com ou sem caminho) ou solicita a implementação de um documento, especificação técnica ou plano de arquitetura já aprovado.
- Implementação de um lote de issues de backlog/QA aprovadas com critérios de aceite claros.
- **NÃO usar** para especificações ainda em aberto ou rascunhos conceituais (refine o escopo antes com o usuário).
- **NÃO usar** para operações diretas em ambiente de produção ou deploy.

## Procedure

### 1. Ingestão de Escopo e Critérios de Aceite
1. **Documento-base:** Identificar o caminho do documento aprovado fornecido pelo usuário. Na ausência de caminho, confirmar formalmente se há um documento canônico na sessão.
2. **Fonte via Issues:** Se a fonte forem issues (ex.: GitHub Issues):
   - Listar e ler os títulos, corpos e comentários de todas as issues do lote.
   - Separar: (a) alterações de código, (b) decisões de produto/UX, e (c) verificações dependentes de ambiente externo.
   - Consolidar dúvidas e decisões de produto em uma única consulta ao usuário antes de começar.
   - Gerar um documento de escopo consolidado com decisões numeradas (D1, D2...), critérios de aceite e itens explicitamente fora de escopo.
3. **Critérios de aceite:** Extrair métricas objetivas e verificáveis (testes unitários/integração esperados, tipos criados, saídas de CLI). Decisões de produto pendentes bloqueiam a delegação — esclareça antes com o usuário.
4. **Verificação de conformidade:** Antes de briefar os implementadores, conferir se os símbolos, arquivos e tipos citados na especificação realmente existem na base de código (`git show <base>:<arquivo>`).

### 2. Resolução de Repositório e Base Git
1. Confirmar que o alvo é um repositório Git limpo (`git rev-parse --show-toplevel` e `git rev-parse HEAD`).
2. Resolver a branch-base correta pelas diretrizes do projeto (`main`, `master` ou branch de release informada).
3. **Preservar estado sujo:** Nunca executar `git stash`, `git reset --hard` ou `git clean` no checkout original do usuário. Alterações em andamento devem permanecer intocadas.

### 3. Isolamento em Git Worktrees
1. **Branch de integração:** Criar um worktree dedicado para a integração da entrega:
   `git worktree add -b doit/<slug> ~/.hermes/doit/worktrees/<repo>/<slug> <base-sha>`
   (Todas as tarefas serão integradas progressivamente nesta branch).
2. **Worktrees de tarefa:** Para cada tarefa do plano, criar uma branch e worktree próprios a partir do estado atual da integração:
   `git worktree add -b doit/<slug>-task-<id> ~/.hermes/doit/worktrees/<repo>/<slug>-task-<id> <integration-sha>`
3. **Regra de isolamento:** Cada subagente trabalha exclusivamente no diretório absoluto do seu respectivo worktree. Subagentes não compartilham diretórios concorrentemente.

### 4. Decomposição em Grafo de Tarefas (DAG)
1. Quebrar a especificação em tarefas atômicas e sequenciáveis (máximo 150-300 linhas de código alteradas por tarefa quando possível).
2. Identificar dependências estritas: tarefas com dependência só são despachadas após a integração e verificação de suas predecessoras.
3. Definir para cada tarefa:
   - Objetivo estrito.
   - Arquivos autorizados para escrita.
   - Critérios de verificação (testes que devem passar, comandos de lint/build).

### 5. Delegação Estruturada
1. Despachar subagentes utilizando o template de briefing padronizado (`templates/briefing.md`).
2. Passar no contexto:
   - Caminho absoluto do worktree isolado.
   - SHA da base fixa.
   - Instruções explícitas de não commitar arquivos fora do escopo.
   - Comandos exatos de verificação local.
3. Utilizar o modelo de raciocínio apropriado para cada complexidade de tarefa.

### 6. Verificação Ativa pelo Orquestrador
**Nunca confiar no relatório textual do subagente.** O agente principal deve verificar os fatos diretamente no disco do worktree da tarefa:
1. Inspecionar o diff real: `git -C <task-worktree> diff <integration-sha>..HEAD --stat` e `git diff`.
2. Conferir integridade: garantir que arquivos alheios ou arquivos binários/temporários não foram alterados.
3. Executar a suíte de testes e o build no diretório da tarefa.
4. Se a verificação falhar: relançar a tarefa ou rejeitar o commit antes de integrar.

### 7. Integração Progressiva e Revisão Independente
1. **Merge na integração:** Com a tarefa aprovada pelo orquestrador, fazer o cherry-pick ou merge fast-forward da branch da tarefa na branch `doit/<slug>`.
2. **Revisão cega (Peer Review):** Ao concluir o conjunto de tarefas ou lote:
   - Despachar um subagente revisor em contexto isolado com o template `templates/reviewer.md`.
   - O revisor avalia o diff completo da branch de integração contra a especificação original, apontando regressões, vulnerabilidades ou desvios de critério.
   - Corrigir apontamentos válidos antes de finalizar.

### 8. Finalização e Handoff
1. Executar a validação final completa na branch de integração consolidada (testes de ponta a ponta, lint e typecheck).
2. Limpeza segura de worktrees de tarefas finalizadas: `git worktree remove ~/.hermes/doit/worktrees/<repo>/<slug>-task-<id>`. Manter o worktree de integração.
3. Gerar relatório de entrega para o usuário contendo:
   - Branch de entrega local (`doit/<slug>`).
   - SHA final e lista de commits produzidos.
   - Tabela de critérios de aceite comprovados com comandos e saídas reais.
   - Arquivos alterados.

## Pitfalls

- **Trabalhar no repo principal:** Nunca execute alterações diretamente na cópia de trabalho do usuário. Sempre utilize worktrees fora da árvore de código principal.
- **Aceitar relatórios cegamente:** Subagentes frequentemente relatam "testes executados com sucesso" sem tê-los rodado de fato. O orquestrador tem obrigação de conferir o diff e rodar a validação.
- **Worktrees aninhados:** Nunca crie um worktree dentro do próprio repositório ou de outro worktree; mantenha em diretório centralizado (`~/.hermes/doit/worktrees/`).
- **Subida não autorizada:** Jamais realizar `git push` ou abrir Pull Requests por conta própria. A fase /doit conclui com entrega local verificada.

## Verification

- `git status` no repositório original do usuário permanece idêntico ao início da execução.
- Branch de integração `doit/<slug>` contém histórico limpo e commits semânticos rastreáveis.
- Testes e verificações declaradas foram executados e tiveram saída bem-sucedida confirmada pelo orquestrador.

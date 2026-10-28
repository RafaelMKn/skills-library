---
name: limpeza-workspace-dev
description: "Use ao limpar pasta dev: worktrees, backups, clones."
version: 0.1.0
author: "<autor>"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [git, worktree, limpeza, organizacao, backup]
    related_skills: [grill-with-docs, grilling, auditoria-trabalho-de-agente]
---

# Limpeza e organização de pasta de desenvolvimento local

Cobre pastas como `<workspace>` que acumulam worktrees, cópias de backup, pastas de QA e clones
parados. O risco não é a pasta extra. É apagar o único lugar onde um commit existe, ou mover uma
pasta que um serviço, cron ou skill usa pelo caminho absoluto.

## When to Use

- Organizar ou enxugar a pasta de projetos (worktrees, `*-backup`, `*-qa-*`, clones arquivados).
- Liberar espaço em disco ocupado por worktrees ou node_modules duplicados.
- Mudar a estrutura de pastas de projetos (agrupar por dono ou cliente).
- Não é para limpeza de worktrees de uma execução em andamento: isso fica com a skill de execução por fases do seu ambiente.

## Procedure

1. **Inventário real antes de qualquer pergunta.** Rode `scripts/inventario_git.sh <pasta>`, que é
   read-only. Ele mostra, por pasta: repo ou worktree (e de qual repo), branch, quantos arquivos
   sujos, commits à frente do upstream, data do último commit e remoto. Depois rode `du -sh` por
   pasta, que é onde aparece o peso real (normalmente node_modules em N worktrees).
2. **Classificar cada pasta pelo destino possível**, com prova:
   - Já integrado: `git merge-base --is-ancestor <sha> origin/main`. Para squash ou cherry-pick,
     `git cherry origin/main <sha> | grep -c '^+'` (0 = patches já estão no main). Em linhas de
     trabalho encadeadas, compare também contra a branch remota mais recente da linha, não só
     contra o main.
   - Está no remoto: `git branch -r --contains <sha>`.
   - Só local: nenhum dos dois. Precisa de push ou bundle antes de sair.
   - Pasta sem git: olhar o conteúdo. Backup de workflow de produção (ANTES/DEPOIS/ROLLBACK) não é
     lixo; vai para dentro do projeto, não para a quarentena.
   - PR merged é prova para worktree de QA: `gh pr list --state all --json number,state,headRefName`.
3. **Varrer segredos soltos**: `find <pastas-qa-backup> -maxdepth 4 -name '.env*' -o -name '*-.env*'`
   fora de node_modules. Cópia de .env em pasta de QA é apagada antes de qualquer quarentena,
   depois de conferir que o .env original existe no clone.
4. **Mapear referências externas aos caminhos** antes de propor mover:
   `grep -rlI "<workspace>/" ~/.config/systemd/user ~/.hermes/config.yaml ~/.hermes/memories
   ~/.hermes/skills ~/.hermes/cron ~/.local/bin ~/.bashrc ~/.config/autostart`, mais `crontab -l`
   e os jobs em `~/.hermes/cron/jobs.json`. Anote os horários dos timers e crons: a mudança tem
   de terminar e ser testada antes da próxima execução.
5. **Grill das decisões** (`grill-with-docs`, rodadas via `clarify`), na ordem: destino do que sai
   → linhas só locais → repos parados → estrutura-alvo → convenção futura de worktree → segredos →
   alterações não commitadas por repo → referências → executor e portão entre fases. Registre as
   decisões em `<pasta>/_organizacao/decisoes.md` no formato ADR (contexto com os fatos medidos,
   tabela Q → decisão, consequências).
6. **Executar em fases com portão.** Um subagente por fase. O principal confere o resultado real
   antes de liberar a seguinte:
   1. Commits em branch `wip/organizacao-<data>`, pushes e bundles. Nada é apagado.
      Prova: `git ls-remote origin refs/heads/<b>` igual ao SHA local; `git bundle verify`.
   2. Apagar cópias de .env; `git worktree remove` (sem `--force`) dos integrados ou com bundle.
   3. Quarentena das pastas sem git; apagar clones limpos que estão no remoto.
   4. Mover para a estrutura-alvo e corrigir as referências do passo 4 no mesmo lote.
   5. `systemctl --user daemon-reload`, testar cada serviço, MCP e cron afetado, escrever o
      README índice e atualizar as skills que citam os caminhos.

## Regras padrão (decididas pelo operador; confirme só o que mudar)

- Worktree sai com `git worktree remove`, mantendo a branch. Ref só local ou HEAD destacado ganha
  bundle antes (criar `refs/salvos/<worktree>` para incluir HEAD destacado no bundle).
- Pasta sem git vai para `<quarentena>/<data>` por 30 dias; não apagar direto.
- Clone parado, limpo e no remoto pode ser apagado: dá para clonar de novo.
- Clone arquivado com alterações soltas: patch (`git diff HEAD`) + tar dos untracked, sem .env, e
  depois quarentena.
- Alterações não commitadas em repo ativo: commit numa branch wip + push, caso a caso. Nunca no
  main, exceto push fast-forward de commits que já estão no main local.
- Worktrees novos ficam só em `~/.hermes/<fluxo>/worktrees/<repo>/<tarefa>`, fora da pasta de projetos.
- Execução por subagente, uma fase por vez, com revisão do principal entre as fases.

## Pitfalls

- **Bundles fora da árvore que vai ser movida** (ex.: `<bundles>/<data>/`). Bundle
  dentro do repo ou da pasta de projetos muda de lugar ou é apagado junto com ela.
- **`git cherry` antes de concluir "não mergeado"**: `merge-base --is-ancestor` dá falso negativo
  quando a linha foi integrada por squash ou cherry-pick, e você apagaria algo que já está salvo ou
  manteria lixo achando que é trabalho.
- **Voltar o checkout para main tira do disco os arquivos que só existem na branch wip.** Confirme o
  push com `ls-remote` antes de voltar, ou mantenha o checkout na wip.
- **Não proponha mover pasta sem o mapa de referências**: unit systemd, `config.yaml` (caminho do
  MCP), cron do Hermes, memória e skills quebram em silêncio. `config.yaml` só muda via
  `hermes config set`.
- **Symlinks também são referência**: `find ~ -maxdepth 4 -type l -lname '*<workspace>*'`.
  ~/.claude/skills pode ter dezenas de links para a biblioteca de skills, e ~/.local/bin pode ter o
  executável de um timer. O grep de texto não encontra symlinks.
- **`git worktree repair` sem argumentos não acha worktrees externos** depois de mover o repo.
  Passe os caminhos: `git -C <repo-novo> worktree repair <wt1> <wt2>...`.
- **Lista no config.yaml**: `hermes config set mcp_servers.<x>.args '["<caminho>", "<PREFIXO>"]'`
  (JSON). Faça backup antes e confira com diff que só mudaram os caminhos.
- **Cron**: `hermes cron edit <id> --prompt "$(cat arquivo)" --workdir <novo>`. Gere o prompt novo
  por substituição em script, porque ele é longo demais para redigitar sem erro, e compare depois
  com o antigo.
- **Smoke do MCP n8n**: o primeiro `npx` baixa o pacote e passa de 40s. Use timeout de 240s e
  mantenha o stdin aberto (`(printf '<initialize>'; sleep 200) | timeout 240 ...`), senão o
  timeout parece falha do caminho novo.
- **Commit de pasta de cliente: ler o conteúdo antes**. Um JSON de dados pode ter dado pessoal; o
  briefing manda checar e não commitar se tiver.
- **Resumo de subagente não libera fase irreversível.** O push "feito" que não chegou ao remoto vira
  perda de código na fase de remoção; confira cada SHA você mesmo.
- **Pasta de QA leva os .env junto**: copiar um repo para teste copia os segredos. Varra todas as
  pastas de QA, não só a que você notou.
- **Não presuma que o .env da pasta que sai é cópia.** Compare com `cmp` contra o clone principal,
  sem abrir o conteúdo. Worktree pode ter o único .env.local do projeto (o clone principal nunca
  recebeu um), e o clone parado que vai ser apagado leva junto os únicos .env dele. Os únicos vão
  para `~/.config/segredos-dev/<projeto>/` (700/600) antes da remoção.
- **Bundle não salva arquivo sujo.** Antes de remover worktrees, rode `git status --porcelain` em
  cada um (`git worktree list --porcelain`): modificado vira `git diff HEAD --binary` e untracked
  vira tar no diretório de bundles. Só então `--force` nesses, e só neles.

## Verification

- `decisoes.md` existe com os fatos medidos e a confirmação do operador antes da primeira mutação.
- Cada push com `ls-remote` = SHA local; cada bundle com `git bundle verify` OK.
- `git worktree list` dos repos sem entradas `prunable` para caminhos removidos.
- Depois de mover: os serviços do mapa de referências sobem, o MCP responde e o grep do passo 4 não
  devolve caminho antigo.

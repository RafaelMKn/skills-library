# Reparar e encerrar worktrees integrados

Use quando a auditoria encontra um worktree antigo, especialmente após mover ou renomear o repositório principal.

## Descoberta e prova

1. Leia `<worktree>/.git` e verifique se o `gitdir` existe. Se não existir, procure o repositório principal entre os projetos locais, excluindo dependências e diretórios de build da busca; não trate um ponteiro antigo como perda de commits.
2. Confirme o candidato com `git -C <repo> worktree list --porcelain` e histórico. O registro deve identificar o caminho do worktree e sua branch.
3. Execute `git -C <repo> merge-base --is-ancestor <branch> main`. Só exit 0 prova incorporação por ancestralidade; outro resultado exige investigação, não exclusão forçada.
4. Compare `<branch>..main` para saber se a main evoluiu. Relate qual versão foi testada e não atribua evidências antigas à ponta atual.

## Limpeza autorizada

1. Confirme o escopo da autorização: remover worktree e branch local integrada, preservando repositório principal e evidências externas. Não inclua branches remotas, arquivos de outros trabalhos ou evidências na limpeza implícita.
2. Mude o diretório corrente para o repositório principal **antes** de remover o worktree; caso contrário, a sessão fica num diretório apagado.
3. Se o apontamento estiver obsoleto, execute `git -C <repo> worktree repair <worktree>`. Use o reparo nativo, não reescreva metadados Git manualmente.
4. Execute `git -C <worktree> status --short --untracked-files=all`. Se houver alterações ou arquivos não rastreados, pare a exclusão e examine-os; incorporação da branch não preserva trabalho sem commit.
5. Com o worktree limpo e a ancestralidade confirmada, execute `git -C <repo> worktree remove <worktree>` e `git -C <repo> branch -d <branch>`. Não use `--force` ou `-D` para contornar recusa: investigue o motivo.
6. Verifique com `git -C <repo> worktree list`, `git -C <repo> branch --list <branch>` e `git -C <repo> status --short`. Informe sucintamente o que foi removido, o que foi preservado e o diretório/branch ativos.

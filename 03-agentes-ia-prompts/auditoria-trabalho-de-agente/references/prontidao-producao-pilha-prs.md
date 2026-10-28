# Prontidão para produção de uma pilha de PRs

Use quando a pergunta for "o que falta para subir para produção" e o trabalho estiver em PRs empilhadas
(cada uma com base na anterior), ainda não mergeadas.

## Procedimento

1. **Mapear a pilha.**
   `gh pr list --state all --json number,headRefName,baseRefName,headRefOid,mergeStateStatus` e, por branch,
   `git rev-list --count origin/main..origin/<b>` e `git merge-base --is-ancestor <b-anterior> <b-topo>`.
   Audite o **topo** (contém as anteriores) e declare a ordem de merge. Branch de handoff/estado marcada
   "não mergear" é evidência, não entrega.
2. **Gates uma vez, auditores em paralelo.** Worktree destacado no SHA do topo, em scratch:
   `git worktree add --detach <scratch>/wt origin/<topo>`. Gates em background, gravando exit por gate
   (`... ; echo "<gate> exit $?" >> exits`). Auditores somente leitura no mesmo worktree, um grupo de issues
   cada, proibidos de instalar/buildar/subir servidor (RAM e corrida de node_modules). No fim:
   `git worktree remove --force <scratch>/wt`.
3. **Provar o que a produção serve hoje, sem custo.** `curl -s -o /dev/null -w '%{http_code}'` na raiz e nas
   rotas que a pilha cria. 404 nas rotas novas = produção ainda é a main antiga. 302 para SSO no preview =
   convidado externo não entra. Nunca POST que acione IA, e-mail ou crédito.
4. **Variáveis exigidas × documentadas.** `git grep -n 'process.env\.'` contra `.env.example` e docs.
   Variável lida no código e ausente da documentação é pendência de deploy silenciosa: a feature degrada
   sem erro (ex.: link de retorno some do e-mail).
5. **Handoff contra o repositório.**
   - Caminho de evidência citado precisa existir: `git ls-tree -r --name-only <branch> | grep <dir>`.
   - Contagem de testes diferente da sua (ex.: skipped) indica teste dependente de ambiente: uma linha.
   - Ressalva "aceita" pelo orquestrador ou outro agente não é decisão do usuário: vira decisão pendente,
     principalmente quando coincide com o critério da issue.
   - Docs internos que ainda dizem "não corrigido" ou "não implementado" contradizem a PR: cite arquivo:linha.
6. **Entrega**, nesta ordem:
   - estado: main × pilha × produção;
   - o que foi entregue de fato;
   - divergências relato × código, numeradas;
   - uma linha por issue: pode fechar? + lacuna decisiva;
   - checklist de produção em ordem de dependência, cada item marcado como decisão do usuário,
     escrita que exige autorização, ou verificável por agente.
   Nenhuma escrita em hospedagem, banco ou GitHub sem autorização.

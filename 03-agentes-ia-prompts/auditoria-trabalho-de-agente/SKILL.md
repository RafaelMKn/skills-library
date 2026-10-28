---
name: auditoria-trabalho-de-agente
description: Use ao conferir o que outro agente de IA fez.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [auditoria, agentes, git, delegacao, verificacao, PT-BR]
    category: <categoria>
    related_skills: [requesting-code-review]
---

# Auditar trabalho feito por outro agente

"Rodei o Antigravity/Codex/Claude Code pra fazer parte disso, pode conferir" — ou um subagente meu
morreu no meio e deixou coisa no disco. Nos dois casos o trabalho está pronto ou semipronto, foi feito
**fora da minha vista**, e o relatório dele (quando existe) é auto-relato, não fato.

Isso não é code review. É reconstrução: eu não sei **onde** ele mexeu, **de que base** ele partiu, nem
se ele já empurrou para algum lugar compartilhado. Responda em **PT-BR**.

## When to Use

- Usuário pede para conferir o que um agente externo produziu.
- Usuário pergunta se um PR atende todas as issues ou critérios de aceite listados.
- Subagente terminou com `status=failed`, `interrupted`, ou cota estourada.
- Suspeita de que duas linhas de trabalho paralelas colidiram no mesmo repositório.

Quando o alvo é fluxo n8n, as regras de conteúdo ficam na skill de correção de produção do seu ambiente. Esta skill cobre a
camada de cima: achar o trabalho, medir a colisão e julgar as afirmações.

## Procedure

### 1. Ache o território — nunca suponha o caminho

Agente externo cria clone próprio, com nome próprio, que eu não conheço. Varra por **tempo**, não por
caminho:

```bash
ls -lat <workspace> | head -20           # diretório novo/tocado aparece no topo
find <workspace> -maxdepth 4 -type f -newermt '<AAAA-MM-DD>' \
  -not -path '*/.git/*' -not -path '*/node_modules/*' \
  -printf '%TY-%Tm-%Td %TH:%TM  %p\n' | sort -r | head -30
```

Um segundo clone do mesmo repositório com sufixo diferente é o sinal mais forte: trabalho paralelo
que não passou pela minha branch.

### 2. Pergunte, nesta ordem, até onde o trabalho chegou

1. **Mergeou em branch compartilhada?** `git log --oneline -6` · `gh pr list --state merged --limit 5`
2. **Escreveu em sistema de produção?** (instância, banco, API de cliente) — checar antes de qualquer
   julgamento de conteúdo, porque muda a urgência de tudo.
3. **Editou arquivo fora do repositório dele?** Compare mtime dos arquivos do workspace principal
   com a janela em que ele rodou.

Só depois disso leia o conteúdo. Auditar o mérito de um prompt enquanto produção está alterada é a
ordem errada.

**Ao responder “o que falta para fechar a integração”, confira a branch de destino antes de rodar gates no worktree.** Use `git -C <repo> worktree list --porcelain`, `git -C <repo> log -6 --oneline main` e `git -C <repo> merge-base --is-ancestor <branch-integracao> main` (exit 0 = já incorporada). Compare `git -C <repo> diff --stat <branch-integracao>..main` para localizar evolução posterior. Separe integração pendente, deploy/homologação real e funcionalidades novas: documentos antigos e state.json são pistas, não substituem o histórico atual. Vincule cada resultado de teste à branch/SHA realmente exercitada; teste verde no worktree antigo não valida a main mais recente.

Se o Git falhar num worktree, leia o arquivo `.git` e confira o destino antes de declarar o repositório perdido. Localize candidatos no diretório de projetos e confirme a identidade por histórico e `worktree list`; não suponha que o nome da pasta permaneceu igual. Para reparar e limpar um worktree já incorporado, siga `references/worktree-lifecycle.md`.

### 3. Merge de base velha reverte trabalho concorrente em silêncio

O achado mais caro desta skill. Agente que clonou **antes** do meu trabalho e mergeou **depois**
apaga o que entrou no meio. Para o git o merge é legítimo; a estatística do diff é a única denunciante:

```bash
git fetch origin
git diff --stat <meu-ultimo-commit> origin/main
```

Centenas de deleções em arquivos que o trabalho dele nem menciona = **reversão, não contribuição**.
Antes de chamar de perda, confirme que a branch original sobreviveu no remoto:

```bash
git ls-remote --heads origin <minha-branch>
```

Normalmente nada morreu de fato — a branch está lá e o estrago é que a `main` virou retrocesso, o que
se conserta com PR de restauração. Verifique especificamente se o **`.gitignore` foi levado junto**:
sem ele, fixture com segredo ou mapa de credencial passa a entrar no próximo commit.

### 4. Confira as afirmações uma por uma

Relatório de agente tem três mentiras recorrentes. Teste cada uma com comando próprio:

- **"zero ocorrências de X"** — rode a busca você mesmo com `search_files`, no repositório dele, no
  conteúdo bruto. String em sticky note, descrição de nó, comentário ou texto de canvas sobrevive à
  busca estreita que ele fez em campos de parâmetro. Sobrevivente não quebra execução, mas contradiz o
  relatório e engana quem ler depois.
- **"validado" / "comportamento certificado"** sem uma única execução — matriz de cenários derivada de
  leitura de prompt é **análise estática**. Se o critério de aceite pede evidência de resposta e existe
  bancada de teste que ele não usou, o critério **não** fechou.
- **"resolve a issue N"** — confira a dependência externa. Mudar configuração num arquivo não fecha
  item que exige confirmar ID, fuso ou permissão em serviço de terceiro que ninguém liberou.

Leia o conteúdo **no ponto que importa** (o nó citado, o campo citado, a função citada) em vez de
confiar na mensagem de commit: a mensagem descreve a intenção, não o resultado.

### 4.1. Compare PR e issues por critério, não por título

1. Leia os corpos integrais das issues, a descrição do PR e as decisões aprovadas; salve o inventário e confira paginação, removendo PRs que a API de issues devolve junto. Separe requisito aprovado, hipótese comercial e dependência externa antes de cobrar implementação.
2. Fixe base/head e compare código final **e diff**. Marque cada capacidade como nova no PR ou herdada da base; funcionalidade preexistente não é entrega desse PR. Reexecute os contraexemplos de laudos anteriores no head atual antes de repetir um achado: correções recentes podem invalidar o diagnóstico antigo. Escopo explicitamente excluído continua pendente, mas não vira defeito do trabalho auditado. Quando uma decisão posterior divergir do texto da issue, exponha a divergência e peça reconciliação do aceite; não transforme a decisão silenciosamente em requisito atendido.
3. Monte uma matriz com uma linha por critério: status (coberto/parcial/não coberto/fora do escopo), evidência `arquivo:linha`, origem (base/PR) e prova faltante. Separe implementação rastreável de aceite em ambiente real; ausência de homologação não equivale a ausência de código.
4. Se houver subagentes, distribua grupos de critérios por área no mesmo SHA e exija leitura somente, matriz e probes reproduzíveis. O principal executa os gates comuns uma vez e reproduz os achados que sustentam o veredito; isso evita três instalações/builds concorrentes e conclusões baseadas só no relato dos filhos.
5. Confira checks **e commit statuses** do head exato no provedor. Um check de comentário de preview verde não prova deploy: consulte também `GET /repos/{owner}/{repo}/commits/{sha}/status`, além de `/check-runs`. Relate bloqueio observado sem inventar a causa.
6. Responda primeiro se o conjunto está coberto, depois apresente uma linha por issue com a lacuna decisiva, problemas prioritários e verificações executadas/puladas. Não recomende fechamento em bloco quando restarem critérios obrigatórios, nem amplie o escopo do PR para hipóteses futuras.

### 4.2. Confronte relatórios de QA com o contrato e a versão exercitada

1. Atualize as refs com `git fetch origin`, registre o SHA do relatório e o head remoto solicitado e compare `git diff --stat <sha-qa>..<head-remoto>`. Audite a versão atual em worktree isolado quando houver servidor dev ou edição concorrente; HMR durante o teste impede atribuir toda a sessão ao SHA anunciado.
2. Classifique cada apontamento como defeito reproduzido, hipótese, comportamento previsto pelo contrato, melhoria de produto ou cenário não testado. Confronte roteiro, schema e decisões: ausência de importação numa jornada de criação do zero e nome fixo de exportação podem ser decisões explícitas, não regressões.
3. Reproduza pelo caminho real com entrada válida. Se faltar o payload original, use fixture sintética e declare que ela prova o mecanismo, não a causa daquela ocorrência. Ao testar um parser, varie apenas a apresentação do mesmo conteúdo factual: títulos Markdown, linhas vazias, campos quebrados e múltiplos registros. Teste também a saída efetiva do extrator de arquivo; texto digitado não representa necessariamente os parágrafos de DOCX ou a ordem de leitura de PDF.
4. Compare as validações de importação, formulário e API. Regex conservadora de extração e schema de texto livre podem aceitar conjuntos diferentes; proponha uma política compartilhada sem copiar cegamente a regex restritiva para todas as entradas. Ao tolerar whitespace, preserve fronteiras de registros: remover todas as linhas vazias pode misturar campos de experiências distintas.
5. Para falha intermitente sem corpo de erro ou logs correlacionáveis, enumere os caminhos possíveis sem escolher uma causa. Proponha primeiro observabilidade com identificador de requisição, código, fase e duração, sem conteúdo pessoal; retentativa bem-sucedida com o mesmo payload não prova qual dependência falhou. Só recomende retry automático com limite e orçamento de custo/tempo explícitos.
6. Entregue ajustes priorizados com arquivos, mudança pretendida e regressões exigidas. Separe resultados dos gates de lacunas de ambiente real (banco, e-mail, impressão, viewport). Pedido de conferir e propor não autoriza implementar mudanças no produto.

Para homologação paga com IA, convite e ledger, siga `references/qa-ia-ledger.md`: baseline, jornada pela superfície solicitada, reconciliação por operação e distinção entre gasto registrado e cobrança real.

### 4.3. Transforme o parecer em execução sem reabrir decisões resolvidas

Quando o usuário autorizar continuar as issues parciais:

1. Separe correções do escopo vigente de funcionalidades futuras explicitamente excluídas. Pergunte somente pelas escolhas que mudam arquitetura ou comportamento; reúna escolhas independentes na mesma chamada de `clarify`.
2. Registre as respostas num briefing comum antes de delegar. Diferencie requisito alterado por decisão do usuário de defeito corrigido: aceitar paginação variável ou retenção temporária em tela não constitui implementação nova. Inclua a reconciliação dos critérios/documentação no trabalho, sem fechar issue antes das provas restantes.
3. Prepare worktrees isolados a partir do head auditado, atribua propriedade de arquivos e reserve uma branch de integração. Delegue correções reproduzidas com testes de regressão; mantenha homologação independente das alterações para evitar que um worker certifique o próprio resultado apenas por inspeção.
4. Se o usuário corrigir o modelo dos subagentes no meio da execução, aplique a escolha aos próximos despachos e continue o lote já autorizado; a troca de modelo não é a entrega nem exige novo pedido de continuação. Não atribua a troca retroativamente a filhos já iniciados.
5. Reúna commits, revise diffs e execute os gates na combinação final. Separe no fechamento implementação local, publicação e homologação externa; nenhum deles substitui os demais.
6. Quando o usuário pedir publicar também o trabalho local e os docs, inventarie relatórios relevantes fora do repositório e incorpore versões sanitizadas à documentação versionada. Preserve evidências, decisões e critérios pendentes; exclua envs, credenciais, tokens de convite, caches e conteúdo pessoal cuja retenção seja proibida. Publique apenas na branch autorizada e confira o SHA remoto; autorização para enviar docs não autoriza merge nem deploy em Production.

### 4.4. "O que falta para subir para produção" numa pilha de PRs

Siga `references/prontidao-producao-pilha-prs.md`: auditar o topo da pilha, gates uma vez em worktree destacado com auditores somente leitura, GET sem custo para provar o que a produção serve, variáveis do código × documentadas, handoff × repositório e checklist ordenado por dependência. Ressalva "aceita" por orquestrador ou outro agente não é decisão do usuário: liste-a como decisão pendente.

### 5. Colha subagente que morreu antes de re-despachar

Interrupção (cota, crash, `/stop`) atinge quase sempre a **cauda** da tarefa — a verificação — não o
começo. Artefatos, commits e até o push costumam ter sobrevivido:

```bash
git log --oneline origin/main..HEAD      # o que ele commitou
git status --short                        # o que ficou por commitar
git ls-remote --heads origin <branch>     # o push aconteceu?
```

Re-despachar às cegas reescreve trabalho bom e gasta cota de novo. Colha, identifique **qual passo
faltou**, e termine só esse passo — verificação que é só rodar script eu faço aqui mesmo, sem filho
nenhum.

**Alteração não commitada é sinal, não sujeira.** Arquivo modificado e sem commit no fim de uma
execução interrompida costuma ser exatamente a correção que ele estava aplicando quando parou. Leia o
diff antes de descartar ou de commitar por cima.

### 6. Rode a verificação que ele deveria ter rodado

A cauda cortada normalmente é a prova. Execute os gates de verdade e guarde a saída real — ida e volta
de transformações inversas, contagem batendo com gabarito, detector encontrando o caso conhecido.
Detector que não acha o problema conhecido está errado, não aprovado. Quando um gate falhar, preserve o log e diagnostique antes de aprovar; não altere asserções para fabricar verde. Se houver timeouts em massa ou falhas de inicialização de workers, confira carga, RAM/swap e concorrência antes de atribuir regressão. Sob contenção, reexecute primeiro o mesmo conjunto em série (`pnpm exec vitest run --no-file-parallelism`, quando for Vitest), mantendo implementação, asserções e timeouts; serializar reduz a disputa de recursos sem enfraquecer o teste. Compare também a base quando precisar distinguir falha preexistente da mudança. Só considere orçamento de timeout maior se a investigação justificar. Relate cada execução separadamente: sucesso serial ou com timeout ampliado não torna verde o comando padrão que falhou. Separe testes aprovados, falhos e ignorados; um teste ignorado não fornece evidência.

Para comandos, skills e coletores, confira também o caminho de uso e a entrega:

- **Separe instalação, descoberta, roteamento e execução.** Carregue a skill instalada, invoque o normalizador/dispatcher real com o texto previsto e confira se ele alcança o handler; só depois teste a superfície ao vivo. Descoberta no catálogo não prova que o adaptador entregue o comando ao agente.
- **Leia o resumo e o arquivo final após executar o pipeline.** Compare ambos com o contrato: um inventário completo não compensa um resumo ordenado apenas por prazo quando o usuário pediu urgência e impacto.
- **Recalcule contagens e cobertura nos artefatos brutos.** Distinga falhas de alvos, cortes temporais e limites de conteúdo; um total de falhas de API não representa todas as lacunas de cobertura.
- **Inspecione os pré-requisitos de uma segunda execução.** Procure manifestos, IDs e schemas necessários fora da instalação durável; dependência de scratch sujeito a poda pode funcionar na primeira rodada e desaparecer antes da próxima.
- **Teste alteração de conteúdo mantendo os mesmos IDs ao auditar síntese ou cache.** Correspondência de identificadores prova identidade dos registros, não que o julgamento ainda corresponda ao status e à evidência atuais.

Registre critérios atendidos e bloqueados separadamente; testes unitários verdes não encerram um critério de roteamento ou de entrega que permaneceu sem prova. Quando validar build com configuração pública local, use a receita existente do CI e identifique o destino no relato: compilação aprovada não comprova conexão ao backend nem pacote apto à produção.

Para provar sensibilidade após integrar correções, aguarde os gates terminarem, registre o diff inicial e introduza uma mutação mínima no contrato protegido (por exemplo, remover filtro de identidade ou inverter gate de habilitação). Execute somente as regressões pertinentes e confirme falhas de asserção esperadas, não erro de importação ou coleta. Restaure exatamente o trecho original, reexecute o mesmo comando e compare o diff com o inicial; isso demonstra RED/GREEN no conjunto integrado sem deixar sabotagem no artefato. Não execute build ou outros gates concorrentes sobre a árvore mutada.

- **Confronte as asserções dos testes com o aceite antes de usar verde como aprovação.** Um teste pode exigir conclusão e consumo de crédito mesmo sem uma seção obrigatória; nesse caso, ele consolida a divergência, não comprova conformidade. Separe também testes que documentam uma limitação dos que comprovam entrega: esperar campos vazios e obter PASS não comprova pré-preenchimento. Não some essas categorias como cobertura funcional concluída.
- **Exercite estados de falha na fronteira entre reducer e tela consumidora.** Injete limite, validação e falha genérica no reducer real e confira quais fases têm mensagem e ação de recuperação na UI; estado correto isoladamente pode deixar a jornada sem saída.
- **Teste proveniência factual com uma base sintética mínima e uma alegação nova sem números nem nomes próprios.** Troque um verbo de responsabilidade mantendo os substantivos e teste competências que só diferem por símbolos, como C e C++; sobreposição lexical pode aceitar promoção de responsabilidade e normalização pode apagar distinções técnicas. Confira também predicados `every` sobre tokens vazios, que aprovam sem evidência. Exercite separadamente resumo, conquistas e competências: proteção em um campo não garante os demais. Reproduza no handler real com LLM simulado e payload válido, registrando status e conteúdo aceito; erro de schema no próprio probe não comprova nem refuta a brecha. Um contraexemplo prova a falha de proteção, não a frequência de alucinação do provedor.
- **Valide separadamente mecanismos de exportação e retenção.** Rastreie a função chamada pelo botão de download e pelo anexo antes de atribuir renderizadores: ambos podem compartilhar a mesma biblioteca, enquanto Chromium atende somente CSS print. PDF por biblioteca não comprova CSS de impressão; limpar sessionStorage não prova descarte do React state nem impede persistência posterior. Siga o mecanismo e o ciclo de vida prometidos no critério, sem atribuir retenção no servidor a um estado apenas local.
- **Audite extração conservadora com positivos usuais e falsos positivos plausíveis.** Antes de integrar, teste títulos profissionais, cidades e empresas no lugar do nome, seções de recomendações no lugar de experiência, placeholders, linhas quebradas e datas locais como mês abreviado/barra/ano. Remover formatos ambíguos reduz invenção, mas também cobertura: declare os formatos aceitos e não anuncie extração geral. Preserve o texto literal e deixe ausências para confirmação do usuário, em vez de completar fatos por heurística.

### 7. Audite lotes de PRs no estado final, não só cada branch isolada

1. Registre base e SHA remoto final de cada PR; confirme o push com `git ls-remote --heads origin <branch>`. Leia o diff da correção e, em commits de merge, use `git show --remerge-diff <sha>` para separar a resolução de conflito do código herdado.
2. Confira dependências entre branches antes de recomendar a ordem de merge. Se uma PR incorporou outra, explicite a ordem e revise a interação dos comportamentos; merge sem conflito não prova integração correta.
3. Para whitespace introduzido pela PR, execute `git diff --check origin/main...HEAD`. A comparação de pontas `origin/main HEAD` inclui diferenças da main ausentes numa branch antiga e pode atribuir à PR um aviso alheio. Preserve essa comparação de pontas quando o objetivo for investigar regressão da main, não validar o patch da PR.
4. Examine os códigos de saída de cada gate e seus logs, não apenas o exit do script agregador: um wrapper pode terminar com sucesso depois de um comando interno falhar. Cabeçalho de execução ou log vazio de diagnósticos não comprova exit0; se o worker foi interrompido, reporte somente o resultado explícito disponível e deixe os demais gates não confirmados. Faça o executor registrar comando, SHA, exit e caminho do log por gate, inclusive quando TypeScript/ESLint terminam silenciosamente. Trate SIGTERM como execução incompleta; se houve cancelamento intencional, registre o motivo, preserve o log parcial e vincule a reexecução completa.
5. Leia a composição dos scripts antes de interpretar uma falha: num encadeamento com `&&`, os gates posteriores não executaram. Rode os restantes separadamente, registrando comando, SHA, exit e log; não deduza cobertura pela intenção do script. Identifique o runner efetivo: testes de Edge Functions executados em Vitest não comprovam execução no runtime Deno.
6. Descubra os caminhos reais dos specs antes de invocar o runner e confira quais testes foram coletados. Um seletor inexistente pode ser ignorado quando outro seletor encontra testes, produzindo sucesso com cobertura menor que a solicitada.
7. Monte a integração temporária com os SHAs finais e inclua os testes de regressão adicionados durante a revisão. Se o último ajuste não entrou na combinação testada, reexecute a verificação pertinente ou declare precisamente a lacuna; resolução manual equivalente não é prova do conjunto final.
8. Entregue uma linha por PR com correção publicada, evidência, dependência e pendência. Separe aprovação de código, prontidão para merge e aceite em ambiente real; não rotule como liberado um critério obrigatório ainda pendente de QA. Testes preventivos, mocks de Auth e asserções sobre texto-fonte não comprovam resolução da ocorrência original nem comportamento em serviço real.

## Veredito: separe conteúdo de método

O padrão real é **conteúdo bom e método ruim**. Aproveite o artefato, recuse o caminho — e não misture
os dois num elogio geral nem numa reprovação geral. O relato sai em quatro blocos:

1. **O que fica** — o artefato que presta, com o que eu conferi nó por nó (não "parece bom").
2. **O que precisa ser desfeito** — `git revert`, PR de restauração, reversão de snapshot, com o
   comando.
3. **O que não pode ser fechado** — item cujo critério de aceite exige prova que ninguém produziu.
4. **O que apareceu no caminho e não é culpa dele** — ver pitfall abaixo.

Ordene a proposta de ação por risco, não por assunto: produção fora do ar vem antes de restaurar CI,
que vem antes de discutir mérito de prompt.

## Pitfalls

- **Achado de infra descoberto durante a auditoria não é culpa do agente auditado — diga isso.**
  Investigar o que ele fez costuma esbarrar em serviço caído ou credencial expirada que já estava assim.
  Estabeleça a janela (a chamada que funcionou antes, a que falhou depois) e declare explicitamente que
  não foi ele. Acusar o culpado errado manda o usuário procurar no lugar errado.
- **Merge direto em branch compartilhada sem PR revisado é o problema, mesmo quando o código está bom.**
  Nomeie o método como defeito separado do conteúdo, senão ele se repete na próxima rodada.
- **Não feche issue por ter recebido resposta parcial.** Nome de responsável entregue sem definir
  como ele recebe o trabalho e onde registra ainda deixa buraco operacional: atualize o corpo da issue
  com o que foi decidido, marque o critério atendido e **mantenha aberta** o que sobrou.
- **Relatório de filho que afirma efeito externo exige handle verificável por mim.** URL, ID ou
  caminho absoluto — e eu confiro antes de repassar ao usuário como sucesso.
- **Ao auditar demora, confronte o pedido inicial, as mudanças de escopo aprovadas e o caminho mínimo de entrega.** Separe dependências do comportamento solicitado das introduzidas pela arquitetura escolhida; testes extensos de um subsistema adicional não provam entrega no ambiente real. Classifique cada pendência como leitura verificável pelo agente, autorização de escrita ou decisão de negócio, para não repassar ao usuário verificações que o agente pode executar.
- **Corpo de PR que diz "corrige #A–#B" é alegação em bloco.** Classifique cada issue do intervalo: observabilidade adicionada não corrige falha intermitente sem causa; timeout ampliado não reduz custo; docs internos que ainda dizem "não corrigido" contradizem a PR e devem ser citados.
- **Dois agentes no mesmo repositório pedem branch por agente.** Se eu vou delegar enquanto outro
  agente pode estar rodando, a spec precisa dizer de qual commit partir e proibir merge — o conflito
  é meu para resolver depois, não dele.

## Verification

- Sei **de que base** ele partiu e se a `main` regrediu (`git diff --stat` citado).
- Toda afirmação do relatório dele que eu repassei foi testada por comando meu.
- Branch original confirmada viva no remoto antes de eu falar de perda.
- Trabalho de subagente morto foi colhido antes de qualquer re-despacho.
- Achado de infra separado explicitamente do que o agente causou.

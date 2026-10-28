---
name: relatorio-resultados-cliente
description: "Use when building a client results/metrics report."
version: 1.0.0
author: <autor>
license: MIT
metadata:
  hermes:
    tags: [relatorio, metricas, cliente, supabase, erp, PT-BR]
    related_skills: [grill-with-docs, grilling, domain-modeling, agent-creator-hub]
---

# Relatório de resultados para cliente <empresa>

Relatório de "ganhos, pessoas atendidas, coisas marcadas" para um cliente que tem um agente da
<empresa> (ex.: <agente>) rodando sobre um ERP/CRM. O usuário quer estruturar a ideia em modo grill
antes de construir. Levante os dados reais antes de fechar as definições de métrica.

## When to Use

Pedido de relatório de ganhos, atendimentos, agendamentos ou ROI do agente para um cliente em
`clientes/`, seja pontual (apresentação em call) ou recorrente.

## Procedimento

1. **Recon do cliente** em `<workspace>/clientes/<slug>/`: `README.md`,
   README do projeto do agente, atas em `docs/`, doc da API do ERP. Procure incidentes que
   criem buracos no histórico (ex.: nó com `onError: continueRegularOutput` que engolia insert —
   nada gravado antes da correção).
2. **Separe as duas fontes** e diga isso na 1ª rodada:
   - ERP (ex.: Clinicorp) = visão da empresa inteira (agenda, faltas, orçamentos, pagamentos).
   - Banco do agente (Supabase) = o que o agente fez.
   O valor que só a <empresa> entrega é o **cruzamento** (conversa → consulta → dinheiro);
   repetir o painel nativo do ERP é trabalho sem diferencial.
3. **Grill (skill `grill-with-docs`)** — 1ª rodada: objetivo (agente × gestão × ambos),
   público/formato, recorrência, projeto novo ou extensão. Registre cada decisão numa tabela no
   `README.md` do projeto `clientes/<slug>/projetos/relatorio-resultados/` assim que fechar.
4. **Antes da 2ª rodada, meça os dados reais** (não pergunte ao usuário): contagem por mês no
   banco do agente, flags de conversão (`agendou`), linhas na tabela de agendamentos, execuções
   da tool de agendamento no n8n (`skills/n8n-manager/scripts/n8n_api.py --instance <X>
   list-executions --workflow-id <ID> --limit 250`), existência de coluna de origem do lead.
   O número real reformula as perguntas.
5. **2ª rodada** — período (com corte nas datas em que regras mudaram), definição de cada
   métrica, narrativa se o número do agente for baixo, acesso à API do ERP.
6. **Colete ERP + banco** (recipe em `references/coleta-dados.md`). Dado bruto do ERP traz CPF,
   endereço e telefone: salve em `clientes/<slug>/projetos/<p>/dados-brutos-<data>/` e prove com
   `git check-ignore -v` que está ignorado **antes** de qualquer outro passo.
7. Calcule em Python sobre os arquivos salvos. Quando a coleta contradisser número já dito na
   conversa, abra a resposta com a correção ("marcou 6, não 1") — não enterre no meio.
8. Termos resolvidos → `clientes/<slug>/CONTEXT.md` (glossário do cliente, só vocabulário);
   decisões numeradas → README do projeto.
9. Pedido que o usuário adiar ("ainda não, deixa salvo") vira item em `## Pendências` do README
   do projeto, com causa, escopo e plano — não some da conversa nem vira ação agora. Dado que
   só o sócio sabe (causa de queda de tráfego, verba de anúncio, data da call) também vira
   pendência; se o usuário pedir, redija a mensagem de WhatsApp para o sócio: contexto em 1 linha,
   perguntas numeradas com o número observado, e um pedido opcional de dado que ajude a explicar.
10. Só construa (HTML, se for apresentado em call) depois de o usuário confirmar entendimento
   compartilhado. HTML só com agregados — nunca nome de paciente — e limitações no rodapé.
   **Gráficos com Spell UI** (preferência do usuário) — limites e build em
   `references/html-graficos.md`; confira os limites antes de prometer um gráfico.

## Definições que sempre precisam ser desambiguadas

- **Ganhos:** recebido (caixa) × vendido (orçamento aprovado, com parcelas futuras). Recomende
  os dois com recebido em destaque — vendido sozinho infla a percepção de caixa.
- **Pessoas atendidas:** na seção da empresa = pacientes únicos com atendimento não cancelado,
  faltas em linha separada; na seção do agente = contatos únicos que conversaram. Nomes
  diferentes para não somar coisas diferentes.
- **Marcado pelo agente:** registro direto (conservador) × cruzamento por telefone com o ERP
  ("contatos que passaram pelo agente e viraram consulta"). O cruzamento é **influência, não
  autoria** — o relatório tem que dizer isso. Conte o registro direto **no ERP pela origem**
  (`CreatedBy = API`), não na tabela do fluxo: nó de gravação que engolia erro deixa a tabela
  com uma fração do real.
- **Cruzamento por telefone:** normalize para DDD + últimos 8 dígitos (absorve `55` e 9º dígito);
  só conte quem não tinha agendamento antes do contato, e puxe histórico do ERP de antes do
  período — senão paciente antigo aparece como novo. Rótulo do R$: "recebido de pacientes que
  passaram pelo WhatsApp", nunca "receita gerada pela IA".
- **Ganhos da empresa:** `payment/list` (pagamentos de paciente, pela data de recebimento) e
  `financial/list_cash_flow` (entradas do caixa, mês cheio) dão totais diferentes. Na seção da
  empresa use meses cheios pelo fluxo de caixa — bate com o painel que o dono já vê; o recorte
  por data exata fica só na seção do agente, com a diferença explicada no rodapé.
- **Agendamentos de teste:** criações pela API antes do 1º contato real, sem categoria/status,
  são suspeitas de teste — pergunte ao usuário e tire da conta se forem.
- **Contatos ≠ atendidos pelo agente:** percorra o fluxo a partir do webhook (BFS em
  `connections`) e veja se o nó que cria o contato vem antes do gate de horário/roteamento. Se
  vier, a tabela inclui conversas da equipe humana; aproxime por horário da 1ª mensagem e declare
  a limitação.

## Pitfalls

- **Não esconda número ruim do agente.** Recomende mostrar o dado com diagnóstico e plano
  (follow-up inativo, falta de origem do lead, falhas de execução); o cliente vê a agenda de
  qualquer jeito. A decisão de narrativa é do usuário/sócio — pergunte, não decida.
- **Antes de explicar uma queda do agente por mudança de regra, compare com a série total**
  (todos os contatos por semana, não só os atribuídos ao agente). Se o total também caiu, a
  regra não explica a queda sozinha — a causa provável é tráfego (anúncio/verba), que só o
  sócio sabe; corrija a recomendação já dada e pergunte, em vez de afirmar "queda esperada".
- **Taxa de conversão do agente não se compara crua com benchmark de mercado.** Os estudos
  (quase todos blogs de fornecedor, medindo ligação telefônica nos EUA: ~25–60% lead→agendamento)
  usam denominador de lead qualificado de paciente novo. Antes de comparar: tire do denominador
  quem já era paciente (cruze os contatos com o cadastro do ERP por telefone) e amplie a janela
  de consultas do ERP **além do fim do período** (`to` meses à frente) — com `to` = data da coleta,
  quem conversou no fim do período e marcou para depois fica fora e a conversão sai subestimada.
  Declare a fraqueza das fontes; não há benchmark confiável de WhatsApp no Brasil.
  Recontagem honesta: agenda **inteira** do ERP (`appointment/list` por semestre desde a abertura,
  num único fluxo temporário) e perfil de cada contato (`ja_ativo` < 6 meses fora do denominador,
  `inativo_6m`, `sem_historico`). Relate antes → agora numa tabela e diga se a taxa continua
  baixa depois da correção — medição corrigida não é desculpa para número ruim.
- **Conversão baixa confirmada → leia as conversas antes de propor solução.** Receita (memória do
  agente no Redis, cruzamento com o ERP, fan-out de leitura) em
  `references/diagnostico-conversas.md`.
- **Número para o site/case é outro filtro, mais duro que o do relatório.** O card vende
  **impacto no negócio do cliente** (dinheiro recebido, pacientes que marcaram/compareceram,
  atendimento fora do horário). Taxa de erro/acerto do agente — mesmo invertida em "% de
  atendimento correto" — é qualidade interna e o usuário rejeita como resultado. Dado financeiro
  do cliente só entra por decisão explícita do usuário, com o rótulo do glossário ("recebidos de
  pacientes que conversaram com o agente antes de marcar"), nunca "faturado" nem "gerado pela
  IA", e com lembrete de pedir o OK do cliente. Avise quando dois números juntos deixam o leitor
  calcular uma taxa ruim sem o contexto. Nome do cliente e qualquer número exigem autorização dele.
  **Pedido de "x% de aumento na conversão depois do agente"**: confira se existe baseline anterior
  ao agente e se a taxa subiu de fato antes de escrever; sem isso, diga que os dados não sustentam
  e ofereça (a) uma tabela de frases reais (frase · número exato + campo de `recontagem.json` ·
  ressalva) com recomendação e (b) a medição que criaria o baseline (ex.: primeiras consultas/mês
  na agenda completa antes × depois, checando mudança de anúncio no mesmo período).
  Quando o usuário trouxer frases prontas para o site, **audite cada uma contra `recontagem.json`/
  `diagnostico-conversas.md` antes de aplicar** e devolva a versão corrigida:
  - **Unidade certa:** contato ≠ conversa (nem todo contato tem conversa na memória); "N semanas"
    confere com as datas do período.
  - **Fração com o numerador certo:** subconjunto (ex.: só leads de anúncio) não vale pelo todo.
  - **Queda de contagem absoluta com volume caindo junto → publique a taxa** ("de 1 em 3 para 1
    em 6"), nunca "de 18 para 3"; quem confere acha inflado, e numa peça que vende "medimos"
    isso destrói a tese. Diga o denominador no texto (ex.: "conversas que não viraram consulta").
  - **Achado que expõe falha do agente só vai ao site com a correção já rodando** (idealmente com
    o número de depois); correção só proposta faz o leitor perguntar "e o que vocês fizeram?".
  - Classificação feita por modelo com revisão amostral pequena: dizer ao usuário antes de publicar.
- **Procure também o que melhorou no ERP** (ex.: conversão de orçamentos por mês): entra como
  destaque da seção da empresa, sem atribuir ao agente.
- **Olhe a taxa de erro das execuções do agente no período** (`list-executions` agrupado por
  dia/status + `get-execution <ID> --include-data` no primeiro erro). Falha de infraestrutura
  (ex.: DNS do Redis no nó de dedup) = leads sem resposta, o que distorce o funil. Reporte como
  achado separado e urgente, fora do escopo do relatório. `--limit 250` traz só as mais recentes:
  a janela real do incidente vem dos logs do container, e a contagem de leads afetados exige
  paginar (`--cursor`) até cobrir o período inteiro. Diagnóstico da causa na VPS:
  `infra-vps-producao` → `references/triagem-servico-fora-do-ar.md` §5. Se o usuário adiar a
  correção e depois pedir só "consulta o que deu", faça o diagnóstico read-only e pare antes de
  alterar compose/rede.
- **Credencial do ERP costuma existir só no n8n.** Ofereça: chaves no `.env` do cliente +
  script, ou fluxo temporário read-only na instância, apagado depois (receita validada em
  `references/coleta-dados.md`). A escolha é do usuário. Nunca traga valor do `.env` para a conversa (`sed 's/=.*/=<redacted>/'`).
- **Supabase via Composio:** cada conexão é de uma org; a errada devolve `403 Forbidden` no
  `SUPABASE_BETA_RUN_SQL_QUERY`. Rode uma query barata (`information_schema.columns`) em todas
  as contas para achar a certa; `word_id` que dá `ConnectedAccountResolutionError` é conexão
  morta. `<cliente>` (`<project-id>`) → `<conta>`. SQL via arquivo
  (`-d @p.json`).

## Referências

- `references/coleta-dados.md` — fluxo temporário de leitura no n8n (credencial presa lá) e
  campos/IDs do Clinicorp (exemplo).
- `references/html-graficos.md` — Spell UI chart: o que faz, o que não faz, como virar HTML único.
- `references/diagnostico-conversas.md` — exportar a memória do agente (Redis) e classificar por
  que o lead não marcou.

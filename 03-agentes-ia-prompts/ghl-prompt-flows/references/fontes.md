# Fontes oficiais e limites

Pesquisa realizada nesta sessão em 15/10/2026 (data fornecida pelo contexto da sessão). Fontes lidas integralmente abaixo, exceto S5, que é apenas complementar. As normas de produção, severidade, privacidade e matriz de testes são síntese local de engenharia, não especificações oficiais do GHL.

## S1 — AI Prompting 101 in HighLevel
https://help.gohighlevel.com/support/solutions/articles/155000002254

Base: Role, Task, Guidelines; exemplos; delimitadores; contexto; tom e iteração no Bot Trial. Sugere repetição de regras importantes e contexto estático conciso (100–200 palavras). Não estabelece um limite universal de prompt. Exemplos que orientam persona humana não foram adotados como norma de identidade.

## S2 — Customize Conversation AI Agent Responses
https://help.gohighlevel.com/support/solutions/articles/155000002255-conversation-ai-bot-settings

Base: Personality, Goal, Additional Information; Add Custom Value; conflitos; teste após salvar. Separa comportamento de Bot Training, Bot Goals e Response Style. Agendamento deve ser configurado em Bot Goals. Não copiar a lista de modelos para a skill: é volátil e deve ser verificada no seletor da conta.

## S3 — Workflow AI Builder: Generate and Edit Workflows with AI
https://help.gohighlevel.com/support/solutions/articles/155000006100-workflow-ai-builder

Base: criação por linguagem natural, edição com escopo, Point and Edit, Chat Mode sem construir, configurações de workflow, To-Do List e autosave. A seção Beta Limitations explicita que a IA não pode testar workflows e requer testes manuais. Undo/redo documentados são de sessão: não substituem plano de restauração.

## S4 — Conversation AI Flow Builder
https://help.gohighlevel.com/support/solutions/articles/155000006515-conversation-ai-flow-builder

Guia com indicação de atualização em 01/06/2026. A extração inicial retornou texto truncado; o artigo completo foi lido pelo navegador.

Base: prompt global por ação; Capture/Qualify; Book Appointment; AI Splitter; AI Message; Custom Message; End Conversation; Transfer Bot; Continue Conversation; Chat Initiated e Custom Triggers.

**Contradição interna relevante:** a seção AI Triggers afirma que Custom Triggers disparam após `[END]`, e que interrupção no meio do fluxo/sensibilidade seriam futuras. A seção seguinte já descreve Low/Medium/High para interrupção. Não escolher uma dessas versões por conveniência: verificar UI, documentação mais recente e teste controlado. O artigo também contém “Auto Followup — Coming soon”; isso não prova ausência atual do recurso.

**Diferença crítica:** `[END]` é fim dos objetivos; End Conversation é término explícito. AI Splitter não coleta. Capture e Book Appointment podem iterar; mensagens são de execução única.

## S5 — Visão geral complementar
https://help.gohighlevel.com/support/solutions/articles/155000001335

Artigo recuperado: Conversation AI Bot – How to Automate Customer Chats. Modos Off, Suggestive e Auto-Pilot e referência a Bot Trial. A lista de canais extraída diverge do guia S4; por isso nenhum catálogo fixo de canais é usado como requisito.

## Política de atualização

Reconsultar o artigo específico quando a tarefa depender de capacidade, limite ou campo da plataforma. Registrar URL e comportamento observado. Se documentação e conta divergirem, informar a divergência e não publicar até validar o caminho afetado.

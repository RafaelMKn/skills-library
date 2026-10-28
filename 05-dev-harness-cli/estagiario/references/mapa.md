# Mapa de skills — o que cada uma faz

Levantado a partir da biblioteca publicada; `scripts/checar_mapa.py <pasta-de-skills>` confere o mapa contra ela. Formato: `| \`nome\` | faz | chame quando |`.
O script `scripts/checar_mapa.py` lê as linhas que começam com `` | `nome` | `` — mantenha o formato.

## n8n — fluxos

| Skill | Faz | Chame quando |
|---|---|---|
| `using-n8n-mcp-skills` | Porta de entrada n8n-mcp; encaminha para a especialista | Qualquer tarefa n8n via MCP antes de escolher a especialista |
| `n8n-flow-builder` | Protocolo de construção do zero ao ativo, com gates | Fluxo novo ou mudança estrutural |
| `n8n-flow-debugger` | Diagnóstico a partir da execução real, correção mínima | Execução com erro, webhook mudo, "funcionava ontem" |
| `n8n-flow-reviewer` | Revisão read-only com severidade | Parecer antes de ativar/entregar/herdar fluxo |
| `n8n-correcao-producao` | Corrigir/alterar/auditar fluxo em produção com backup e prova | Fluxo de cliente real quebrou ou vai ser alterado |
| `radar-n8n` | Varre instâncias, agrupa erros por causa raiz, painel HTML | "Como estão os fluxos?", cron Radar n8n |
| `incident-forensics` | Reconstrói início, extensão e causa de incidente (read-only) | "Desde quando?", card automático de bug crítico |
| `n8n-manager` | CRUD de fluxos e execuções pela API com credenciais do .env | n8n sem MCP disponível |
| `n8n-mcp-tools-expert` | Uso correto das ferramentas n8n-mcp | Antes de chamar qualquer tool n8n-mcp |
| `n8n-multi-instance` | Escolher/verificar a instância alvo do MCP | Várias instâncias, NOT_FOUND estranho, INSTANCE_AMBIGUOUS |
| `n8n-workflow-patterns` | Padrões de arquitetura (webhook, API, DB, IA, batch, agendado) | Desenhar estrutura ou otimizar fluxo lento |
| `n8n-node-configuration` | Campos obrigatórios por operação, displayOptions | Configurar parâmetros de nó |
| `n8n-expression-syntax` | Sintaxe `{{ }}`, $json/$node, mapeamento | Escrever/consertar expressão |
| `n8n-validation-expert` | Interpreta erros/avisos de validação, falsos positivos | validate_* devolveu erro |
| `n8n-code-javascript` | JS no Code node | Code node em JS |
| `n8n-code-python` | Python no Code node | Code node em Python (pedido explícito) |
| `n8n-code-tool` | Custom Code Tool chamado por AI Agent | Tool de código plugada em agente |
| `n8n-agents` | Desenho de nós de IA: Agent, chain, classifier, memória, RAG | Construir/editar agente de IA no n8n |
| `n8n-binary-and-data` | Arquivos/binário, base64, anexos, visão | PDF, imagem, upload/download no fluxo |
| `n8n-error-handling` | Saídas de erro, retry, idempotência, DLQ, Error Trigger | Fluxo que falha em silêncio ou webhook duplicado |
| `n8n-subworkflows` | Sub-workflows reutilizáveis, inputs tipados | Lógica compartilhada, fluxo com +10 nós |

## n8n — servidor e infraestrutura

| Skill | Faz | Chame quando |
|---|---|---|
| `n8n-servidor-vps` | Upgrade, rollback e recuperação do container n8n no VPS | Versão/imagem/volume/proxy do n8n existente |
| `n8n-self-hosting` | Instalação nova de n8n (Docker + Caddy + TLS) em VM | Servidor novo do zero |
| `infra-vps-producao` | Operação de VPS de produção: Docker, Traefik, DNS | Qualquer mudança no VPS que não seja só o n8n |
| `auditoria-infra-hospedagem` | Auditoria de conta de hospedagem: custo, desperdício, DNS | "Quanto gasto?", limpeza de recursos |

## Outras automações e APIs

| Skill | Faz | Chame quando |
|---|---|---|
| `make-manager` | Cenários Make pela API v2 (CRUD, logs, blueprint) | Make/Integromat |
| `clickup-api` | API REST do ClickUp fora do n8n | Tarefa/lista/webhook ClickUp direto |
| `airtable` | Airtable REST via curl | Registros Airtable |
| `composio-apps` | Acesso a contas reais de apps pela CLI Composio | Gmail, Calendar, YouTube, GitHub, Slack, Notion, Outlook... |
| `composio` | Setup, SDK, MCP, migração e diagnóstico do próprio Composio | Conexão Composio quebrada ou integrar Composio em código |
| `google-workspace` | Gmail/Calendar/Drive/Docs/Sheets via `gws` CLI | Quando o `gws` for pedido ou Composio não servir |
| `box` | Arquivos, compartilhamento e metadados no Box | Box |
| `xurl` | X/Twitter: busca, post, DM, mídia | X/Twitter |
| `whatsapp-baileys-local` | Envio de WhatsApp pela bancada Baileys local | Mandar mensagem WhatsApp pela bancada local |

## Agentes de IA

| Skill | Faz | Chame quando |
|---|---|---|
| `prompt-engineering-agentes` | System prompt em XML, persona, anti-alucinação | Escrever/revisar prompt de agente |
| `ghl-prompt-flows` | Prompts GHL, Workflow AI Builder, Conversation AI, auditoria de fluxos, acesso a subconta e custo de ação premium | Qualquer trabalho em GoHighLevel: prompt, workflow, "tenho acesso à subconta X?", GHL→planilha/n8n |
| `openclaw-agent-creator` | Criar/configurar agente OpenClaw (SOUL, AGENTS, openclaw.json) | OpenClaw |
| `eval-set-agentes` | Eval set versionado e comparação entre rodadas | "Melhorou ou piorou?" |
| `auditoria-trabalho-de-agente` | Conferência do que outro agente fez | Resultado de subagente/agente externo |
| `claude-code` | Delegar código ao Claude Code CLI | Pedido explícito de usar Claude Code |
| `codex` | Delegar código ao Codex CLI | Pedido explícito de usar Codex |
| `opencode` | Delegar código/review ao OpenCode CLI | Pedido explícito de usar OpenCode |
| `delegated-cli-runtime` | Integrar CLI de agente como runtime (NDJSON/RPC) | Plugar CLI externo num host/app |
| `external-agent-runtime-integration` | Mesma integração, foco em testes de contrato | Apoio da anterior |
| `computer-use` | Controlar o desktop (mouse, teclado, tela) | Tarefa que exige GUI fora do navegador |
| `ia-quota-monitor` | Cotas e rate limits de Claude Code, Codex, Gemini | "Quanto de cota tenho?", 429 |
| `create-subagent` | Cria subagentes especializados com prompt de sistema próprio | Definir subagente reutilizável |

## Hermes

| Skill | Faz | Chame quando |
|---|---|---|
| `hermes-agent` | Configurar, usar, estender e orquestrar o Hermes | Qualquer dúvida/config do Hermes |
| `hermes-context-tuning` | Medir e reduzir contexto/custo por turno | Hermes lento, caro, contexto grande |
| `hermes-roteamento-modelos` | Trocar modelo, reasoning effort e fallback (principal e delegação) | "Muda o modelo", 429 de cota, ajustar subagentes |
| `hermes-agent-skill-authoring` | Padrões de SKILL.md no repo do Hermes | Criar skill para o repo hermes-agent |
| `inspecting-hermes-desktop-dom` | Ler DOM/CSS do app desktop via CDP | Bug visual do Hermes desktop |
| `skill-finder` | Buscar/instalar skills; decidir se precisa de skill | "Existe skill para X?" |

## Desenvolvimento de software

| Skill | Faz | Chame quando |
|---|---|---|
| `github` | PRs, issues, reviews, repos via `gh` | GitHub pela CLI |
| `systematic-debugging` | Debug em 4 fases, causa raiz antes do conserto | Bug de código |
| `test-driven-development` | Ciclo RED-GREEN-REFACTOR | Implementar com testes primeiro |
| `requesting-code-review` | Review pré-commit: segurança e gates | Antes de commitar |
| `simplify-code` | Limpeza paralela de mudanças recentes | "Simplifica esse código" |
| `spike` | Experimento descartável para validar ideia | Testar viabilidade antes de construir |
| `dogfood` | QA exploratório de web app com evidências | Testar app como usuário |
| `codebase-inspection` | Contagem de LOC/linguagens com pygount | "Tamanho do repo" |
| `node-inspect-debugger` | Debug Node via --inspect/CDP | Precisa de breakpoint em Node |
| `python-debugpy` | Debug Python com pdb/debugpy | Precisa de breakpoint em Python |
| `maintaining-custom-forks` | Manter fork de produção com código próprio | Rebase/merge de upstream em fork |
| `fastify-best-practices` | Servidores Fastify/REST em Node | Backend Fastify |
| `oauth` | Fluxos OAuth 2.0/2.1 em Fastify | Login/token/PKCE |
| `prisma-cli` | Comandos da CLI Prisma (migrate, generate...) | Migration/schema Prisma |
| `prisma-client-api` | Queries do Prisma Client | Escrever query Prisma |
| `domain-modeling` | Modelo de domínio, CONTEXT.md, ADR | Terminologia do projeto, registrar decisão |
| `postgres-least-privilege-api-tests` | Testes de privilégio mínimo e de bloqueio (locks) em Postgres | Testar permissões e locks de API com Postgres |
| `sdlc-review` | Revisa handoffs do Kanban e roteia resultados verificados (exige kanban) | Revisar entrega do Kanban |

## Design, sites e UI

| Skill | Faz | Chame quando |
|---|---|---|
| `impeccable` | Crítica e melhoria de UI existente (UX, tipografia, cor, motion) | "Melhora essa interface" |
| `claude-design` | Artefatos HTML avulsos (landing, deck, protótipo) | Peça HTML única |
| `design-system-extraction` | Extrai design system de referência em design-system.html | "Copia o estilo desse site" |
| `popular-web-designs` | 54 design systems reais (Stripe, Linear, Vercel) | Referência visual pronta |
| `design-md` | Arquivos DESIGN.md (tokens do Google) | Spec de tokens |
| `architecture-diagram` | Diagramas de arquitetura SVG escuros | Diagrama de infra/sistema |
| `baoyu-infographic` | Infográficos (21 layouts x 21 estilos) | Infográfico |
| `p5js` | Sketches p5.js, arte generativa | Arte generativa/interativa |
| `animated-component-libraries` | Componentes React animados prontos (Magic UI, React Bits) em TS/Tailwind | Componente animado pronto para React |
| `canvas` | Canvas `.canvas.tsx` aberto no IDE ao lado do chat | Visualização interativa no IDE |
| `design-dna` | Extrai, estrutura e aplica identidade de design (tokens, tipografia, cor, motion) | Replicar identidade visual de referência |
| `generative_ui` | Widgets HTML interativos inline no chat ou como artefato | Diagrama, gráfico ou controle interativo no chat |
| `gsap-scrolltrigger` | GSAP e ScrollTrigger: timelines, tweens e animação por scroll | Animação dirigida por scroll |
| `lightweight-3d-effects` | Efeitos 3D leves com Zdog, Vanta.js e Vanilla-Tilt | Fundo animado ou tilt decorativo sem WebGL pesado |
| `lottie-animations` | Animações Lottie (After Effects) para web e React | Ícone ou loading animado em JSON |
| `modern-web-design` | Tendências e padrões de web design 2024-2025, acessibilidade | Desenhar site ou experiência interativa |
| `motion-framer` | Biblioteca Motion para React: variantes, gestos, layout e exit | Animação de componente React |
| `react-spring-physics` | React Spring e Popmotion: animação baseada em física | Animação com mola ou gesto contínuo |
| `react-three-fiber` | Cenas 3D declarativas com React Three Fiber | Cena 3D dentro de app React |
| `scroll-reveal-libraries` | Reveal por scroll simples com AOS (fade/slide) | Landing page com efeito básico de entrada |
| `threejs-webgl` | Three.js e WebGL/WebGPU: cenas, configuradores, visualização 3D | Cena 3D no navegador sem React |
| `web3d-integration-patterns` | Combina Three.js, GSAP, R3F, Motion e React Spring em 3D | Experiência 3D que mistura várias bibliotecas |

## Vídeo, áudio e mídia

| Skill | Faz | Chame quando |
|---|---|---|
| `motion-flux` | Pipeline editorial de vídeo motion da <empresa> (ideia → roteiro → voz → takes) | Reels/Shorts da <empresa> |
| `elevenlabs-motion` | Locução ElevenLabs com timings | Peça aprovada precisa de voz |
| `remotion-video` | Render de vídeo com Remotion (MP4/MOV, legendas) | Gerar o arquivo de vídeo |
| `manim-video` | Animações Manim estilo 3Blue1Brown | Animação matemática/algoritmo |
| `ascii-video` | Converter vídeo/áudio em ASCII colorido | Efeito ASCII |
| `youtube-content` | Transcrição de YouTube → resumo, thread, blog | Link de YouTube para resumir |
| `gif-search` | Buscar/baixar GIFs do Tenor | GIF |
| `songsee` | Espectrogramas e features de áudio | Analisar áudio |
| `songwriting-and-ai-music` | Composição e prompts Suno | Música com IA |

## Conteúdo, marketing e carreira

| Skill | Faz | Chame quando |
|---|---|---|
| `ad-creative` | Copy e criativos de anúncio pago em escala | Variações de anúncio |
| `humanizer` | Tira cara de IA do texto (PT-BR/EN) | "Deixa mais humano" |
| `curriculo-blindado` | Banca de 7 avaliadores que tentam reprovar o CV | Blindar/revisar currículo contra vaga com estresse máximo |
| `relatorio-resultados-cliente` | Relatório de resultados/métricas de cliente | Relatório mensal de cliente |
| `pauta-definicao-cliente` | Pauta, deck, registro de decisão e mapa de status para reunião | Reunião com cliente travado; "apresentar o que temos e o que falta" (vence `claude-design`) |

## Produtividade, documentos e notas

| Skill | Faz | Chame quando |
|---|---|---|
| `notion` | API Notion e `ntn` CLI genéricos | Notion fora dos fluxos acima |
| `notion-publico-raspagem` | Raspa página pública do Notion sem login | Link público de Notion |
| `obsidian` | Ler/criar/editar notas no vault Obsidian | Obsidian |
| `weekly-review-planning` | Revisão semanal e plano da próxima semana | "Revisão da semana" |
| `meeting-action-items` | Notas de reunião → decisões, responsáveis, tickets | Ata/transcrição de reunião |
| `document-to-action-items` | Documento → obrigações, prazos, tarefas citadas | Contrato/edital/documento longo |
| `teams-meeting-pipeline` | Resumos de reunião do Teams via Graph | Microsoft Teams |
| `email-inbox-triage` | Triagem de caixa de entrada e rascunhos | "Organiza meu e-mail" |
| `himalaya` | E-mail IMAP/SMTP pelo terminal | E-mail sem Composio |
| `docx` | Word .docx | Documento Word |
| `xlsx` | Excel .xlsx e CSV | Planilha |
| `pdf` | Criar, ler, juntar, preencher, OCR em PDF | PDF |
| `powerpoint` | Apresentações .pptx | Slides |
| `maps` | Geocoding, POIs, rotas (OpenStreetMap) | Endereço, rota, distância |
| `product-price-monitor` | Monitorar preço e alertar no alvo | "Me avisa quando baixar" |
| `apple-notes` | Criar, buscar e editar Apple Notes pelo CLI `memo` (só macOS) | Nota no Apple Notes |
| `apple-reminders` | Lembretes do Apple via `remindctl` (só macOS) | Lembrete no Apple Reminders |
| `findmy` | Rastreia dispositivos Apple pelo app Buscar (só macOS) | Localizar dispositivo Apple |

## Pesquisa e web

| Skill | Faz | Chame quando |
|---|---|---|
| `last30days` | O que se fala de um tema nos últimos 30 dias (Reddit, X, YouTube, HN...) | Pesquisa de tendência/opinião recente |
| `competitor-news-monitor` | Notícias relevantes de empresas nomeadas | Monitorar concorrente |
| `arxiv` | Busca de papers no arXiv | Paper acadêmico |
| `grounded-citations` | Resposta com fontes verificáveis | Precisa citar fonte |
| `llm-wiki` | Base de conhecimento markdown interligada | Montar/consultar wiki pessoal |
| `blocked-page-recovery` | Contornar 403/429, paywall, WAF | Fetch falhou |

## Decisão e planejamento

| Skill | Faz | Chame quando |
|---|---|---|
| `grilling` | Interrogatório para estressar plano/decisão (padrão do operador) | Decisão ou escopo em aberto |
| `grill-with-docs` | Mesmo interrogatório gerando ADR e glossário | Decisão que precisa ficar documentada |
| `guia-contexto-projeto` | Junta repo, pastas locais e decisões de conversas passadas em guia com objetivo, decisões pendentes e tasks com aceite | "Faz um guia do contexto + tasks para fechar a v1 do projeto X" |

## Linux e máquina local

| Skill | Faz | Chame quando |
|---|---|---|
| `linux-power-management` | Energia, calor, ventoinha, CPU | Notebook quente/bateria |
| `linux-desktop-customization` | Temas e painéis do desktop | Personalizar KDE/desktop |
| `limpeza-workspace-dev` | Inventário git, destino seguro (bundle/quarentena) e reorganização da pasta de projetos com fases e portão | "Organiza o /dev", worktrees/backups/QA sobrando, liberar espaço |

## Complementos do catálogo

| Skill | Faz | Chame quando |
|---|---|---|
| `notion-reestruturacao-workspace` | Reestrutura workspace Notion com segurança | Mudança estrutural no Notion |
| `product-visual-exploration` | Explora designs e mockups de produtos físicos | Design de produto físico |
| `agy-customizations` | Personaliza o comportamento do Antigravity: workflows, diretrizes e integrações | Configurar o Antigravity |
| `antigravity-guide` | Guia, referência rápida e mapa do Google Antigravity (CLI, IDE, SDK) | Dúvida sobre o Antigravity |
| `babysit` | Leva um PR até pronto para merge: status, comentários e CI | Destravar PR até merge |
| `create-hook` | Cria hooks que rodam lógica antes ou depois de eventos do agente | Automação em eventos do agente |
| `create-rule` | Cria regras persistentes de projeto em .cursor/rules/ | Regra de projeto para o agente |
| `create-skill` | Guia para criar skills de agente bem escritas | Criar skill nova |
| `loop` | Acorda o agente em intervalos para trabalho local recorrente | Tarefa recorrente monitorada |
| `migrate-to-skills` | Migra workflows legados para skills modernas, com arquivo seguro | Converter workflow antigo em skill |
| `migrate-workflows` | Migra workflows legados entre configurações globais e de workspace | Migrar workflows para o novo formato |
| `permissioned-github` | Interação com GitHub pedindo permissão quando o ambiente bloqueia | Comando GitHub bloqueado pelo ambiente |
| `sdk` | SDK TypeScript para rodar agentes de código programaticamente | Integrar agente por código |
| `shell` | Executa o texto após `/shell` como comando literal | Usuário pede `/shell` explicitamente |
| `split-to-prs` | Divide um lote de trabalho em PRs pequenos, após aprovação do plano | Quebrar mudança grande em PRs |
| `statusline` | Linha de status personalizável do CLI | Configurar a status line |
| `update-cli-config` | Ver e alterar configurações do CLI (arquivo JSON do usuário) | Mudar config do CLI |
| `update-cursor-settings` | Alterar settings.json do editor (tema, atalhos, preferências) | Mudar configuração do editor |

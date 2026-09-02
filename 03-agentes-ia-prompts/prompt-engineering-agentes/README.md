# prompt-engineering-agentes

> Técnicas de engenharia de prompt para agentes autônomos em OpenClaw, Paperclip e n8n. Use ao escrever ou revisar o system prompt de um agente, ao definir persona/SOUL/IDENTITY de um agente OpenClaw, ao orquestrar múltiplos agentes no Paperclip, ao configurar o prompt de um nó de IA no n8n (AI Agent, Text Classifier, Information Extractor), ou quando o agente estiver alucinando, ignorando ferramentas, saindo do personagem ou devolvendo formato errado.

## 📖 Visão Geral

Esta skill fornece diretrizes, padrões e instruções especializadas para **prompt-engineering-agentes**.


---

## 🛠️ Conteúdo da Skill

# Guia de Engenharia de Prompt para Agentes de IA 🧠🤖

Este guia reúne as principais técnicas, conceitos e padrões de engenharia de prompt voltados especificamente para a criação de agentes autônomos no **OpenClaw**, **Paperclip** e **n8n**.

---

## 1. Fundamentos do Prompting para Agentes

Ao contrário de prompts simples para chats estáticos (Q&A), os agentes exigem prompts estruturados que comandam **raciocínio, tomada de decisão, uso de ferramentas e persistência**.

### 1.1. O Padrão ReAct (Reason/Act)
A maioria dos agentes modernos opera em um loop contínuo de **Raciocínio (Thought)**, **Ação (Action)** e **Observação (Observation)**.
*   **Thought (Pensamento):** O agente avalia a solicitação do usuário e planeja o próximo passo.
*   **Action (Ação):** O agente escolhe uma ferramenta (ex: busca na web, ler arquivo, rodar código) e define os argumentos.
*   **Observation (Observação):** O agente lê o resultado da ação (o output da ferramenta).
*   **Prompting:** Para que o LLM execute esse fluxo com eficácia, o prompt do sistema deve instruir o modelo a estruturar seus pensamentos antes de disparar ferramentas e a nunca inventar resultados de ferramentas (alucinação).

### 1.2. Decomposição de Tarefas (Planning)
Para tarefas complexas, os agentes precisam dividir o problema em subtarefas.
*   **Cadeia de Pensamento (Chain-of-Thought):** Instruir o agente a explicar o raciocínio passo a passo: *"Pense alto e detalhe seus passos antes de tomar uma decisão crítica."*
*   **Planejamento Explicito:** Instruir o agente a listar as tarefas planejadas e ir marcando-as como completas à medida que avança (ex: utilizando arquivos de log de tarefas como o `task.md`).

### 1.3. Prompting de Poucos Exemplos (Few-Shot Prompting)
Fornecer exemplos concretos (entradas e saídas esperadas) é a forma mais eficaz de alinhar o tom, o formato e o comportamento de decisão do agente.
*   No OpenClaw, isso é feito salvando "Golden Standards" de outputs no arquivo `MEMORY.md`.
*   No n8n/Paperclip, você pode inserir blocos de exemplos de entrada/saída dentro do próprio prompt do sistema.

---

## 2. Engenharia de Prompt no Ecossistema OpenClaw

O OpenClaw utiliza uma arquitetura baseada em arquivos markdown onde a identidade, regras morais e memória do agente são divididas para evitar sobrecarga de contexto e foco de tarefas.

```
agent_openclaw/
├── SOUL.md         # A alma do agente (Quem é, princípios morais e tom de voz)
├── AGENTS.md       # O procedimento de trabalho (O que faz a cada início de sessão)
├── TOOLS.md        # O que ele pode fazer (Frameworks de escrita, checklists de QA)
└── MEMORY.md       # O que ele lembra (Exemplos de sucesso, aprendizados contínuos)
```

### 2.1. SOUL.md (A Alma do Agente)
Este arquivo define o caráter do agente.
*   **Princípios Inegociáveis:** Devem vir em formato de regras estritas (ex: *"Nunca invente fatos. Se faltar dados, relate a lacuna."*).
*   **Persona e Tom de Voz:** Defina o nível de formalidade, adjetivos de personalidade e comportamentos de resposta (ex: *"Responda de forma direta e sem desculpas"*).
*   **Padrão de Output:** Se o agente deve responder de imediato sem mensagens de cortesia (ex: *"Não responda com frases intermediárias como 'Entendido, vou iniciar'. Retorne imediatamente o output final."*).

### 2.2. AGENTS.md (Procedimento Operacional Padrão - SOP)
O arquivo de instruções de fluxo de trabalho.
*   Ensina ao agente **como ele deve ler os outros arquivos** no início da sessão.
*   Mapeia o passo a passo para processar a entrada (ex: 1. Intake, 2. Planejamento, 3. Execução, 4. Revisão/QA, 5. Entrega).

### 2.3. TOOLS.md (Habilidades e Checklist de Qualidade)
Contém frameworks e diretrizes de verificação.
*   Fornece a lista de verificação (QA checklist) que o agente deve aplicar em seu próprio rascunho antes de considerá-lo pronto.
*   Instrui sobre o uso de recursos específicos do ambiente.

### 2.4. MEMORY.md (Histórico e Golden Standards)
A referência primária do agente sobre o que já deu certo.
*   **Golden Standards:** Guarde exemplos perfeitos de trabalhos anteriores. Isso funciona como Few-Shot prompting de alta fidelidade.
*   **Notas de Aprendizado:** O agente deve ter permissão para atualizar esse arquivo ao final de sessões para registrar novos aprendizados que devem ser mantidos nas próximas sessões.

---

## 3. Orquestração Multi-Agente no Paperclip

O Paperclip gerencia agentes a partir de uma ótica corporativa. O prompt do sistema deve refletir papéis organizacionais rígidos e limites de delegação.

### 3.1. Prompting para o CEO (Orquestrador Central)
O CEO recebe a tarefa principal do usuário e a decompõe, contratando ou delegando subtarefas para outros agentes (como Desenvolvedores, Designers, QA).
*   **Prompting do CEO:** Deve focar em gestão de orçamento, acompanhamento de progresso, e aprovação de resultados.
*   *Exemplo de instrução chave:* *"Você é o CEO. Sua principal tarefa é planejar o projeto, delegar subtarefas específicas para a sua equipe, auditar os resultados e garantir que o orçamento não seja estourado. Não faça o trabalho técnico você mesmo se houver um especialista disponível."*

### 3.2. Prompts de Agentes Especialistas (Executores)
Agentes focados em tarefas únicas (como escrever código ou redigir relatórios).
*   **Prompts de Especialistas:** Devem focar em excelência técnica, recepção de feedback do QA e relatórios sucintos.
*   *Exemplo para Desenvolvedor:* *"Você é o Engenheiro de Software. Receba as especificações do CEO. Escreva código limpo, modular e documentado. Se o agente de QA rejeitar sua implementação, corrija os pontos apontados sem argumentar."*

### 3.3. Prompts de QA (Garantia de Qualidade/Auditores)
Agentes cuja única função é auditar o trabalho de outros e dar aprovação/rejeição.
*   **Prompting de QA:** Deve ser crítico, analítico e baseado em regras estritas de aceitação.
*   *Exemplo para QA:* *"Você é o Analista de QA. Seu papel é testar e validar o trabalho do Desenvolvedor de forma rigorosa. Apenas aprove o trabalho se todos os requisitos forem atendidos. Se rejeitar, liste detalhadamente os bugs ou lacunas encontradas."*

---

## 4. Prompting em Nós de IA no n8n

No n8n, os prompts dos agentes interagem diretamente com fluxos gráficos de dados.

### 4.1. Configuração do System Prompt do nó "AI Agent"
O nó AI Agent do n8n (com ferramentas/ferramentas de código) precisa de instruções claras sobre quando e como chamar cada nó conectado.
*   **Diga claramente o que está disponível:** *"Você tem acesso a ferramentas para ler planilhas do Google, enviar e-mails e buscar na web."*
*   **Defina o comportamento esperado:** *"Use a ferramenta de busca sempre que a pergunta envolver eventos recentes ou dados externos em tempo real."*
*   **Filtro de Output:** *"Sua resposta final deve ser estruturada em JSON contendo os campos 'sucesso', 'mensagem' e 'dados' para que os próximos nós do n8n possam processá-la."*

### 4.2. Prompting de Ferramentas (Tool Descriptions)
No n8n, a **descrição da ferramenta** que você escreve é o prompt que o LLM lê para decidir se vai chamar aquela ferramenta.
*   **Descrição Ruim:** *"Roda uma consulta no banco."* (O LLM não sabe o que pode consultar nem quais parâmetros enviar).
*   **Descrição Perfeita:** *"Útil para buscar o histórico de compras de um cliente usando o CPF. Parâmetro esperado: 'cpf_cliente' no formato de string de 11 dígitos. Sempre chame esta ferramenta se o usuário perguntar 'quais compras eu fiz'."*

---

## 5. Práticas Recomendadas e Evitação de Erros Comuns

*   **Redução de Alucinação (Zero-Guess Policy):** Sempre inclua instruções como: *"Se você não tiver certeza de um dado ou se a informação não foi explicitamente fornecida, admita que não sabe ou aponte a falta de dados. Nunca invente valores."*
*   **Uso de Delimitadores:** Use delimitadores claros como `###`, `---` ou tags XML (ex: `<briefing>...</briefing>`) para ajudar o agente a identificar o que são instruções de prompt, o que são ferramentas e o que são entradas de dados do usuário.
*   **Restrições Formatação Física:** Se o agente precisa formatar o texto de uma maneira exata (ex: parágrafos separados por uma linha em branco para anúncios de WhatsApp/Meta), declare isso de forma explícita e repetida ao final do prompt: *"REQUISITO CRÍTICO: Separe rigorosamente cada parágrafo com uma linha em branco. Nunca junte parágrafos."*

---

## 6. Habilidades de Automação n8n Integradas (n8n-skills)

Adicionamos a este projeto a biblioteca completa de habilidades **`n8n-skills`** (portada do GitHub). Elas servem para ensinar os agentes de IA (como Claude Code ou Antigravity) a construir, validar, estruturar e debugar fluxos no n8n de forma profissional.

As habilidades estão disponíveis no diretório [01-automacao-n8n-make/](../../01-automacao-n8n-make/).

### 6.1. Habilidades Disponíveis no Workspace

*   **[n8n-expression-syntax](../../01-automacao-n8n-make/n8n-expression-syntax/SKILL.md):** Ensina como referenciar variáveis como `{{ $json.campo }}` e a evitar o erro clássico de usar `{{ $json.body.campo }}` em webhooks.
*   **[n8n-workflow-patterns](../../01-automacao-n8n-make/n8n-workflow-patterns/SKILL.md):** Mostra os 6 padrões de arquitetura (Webhooks, Integração HTTP API, Banco de Dados, Agentes IA, Tarefas Agendadas e Processamento em Lotes).
*   **[n8n-node-configuration](../../01-automacao-n8n-make/n8n-node-configuration/SKILL.md):** Instruções para configurar os parâmetros de nós complexos de forma correta via MCP.
*   **[n8n-validation-expert](../../01-automacao-n8n-make/n8n-validation-expert/SKILL.md):** Como interpretar erros de validação retornados pelo n8n e corrigi-los no ato.
*   **[n8n-code-javascript](../../01-automacao-n8n-make/n8n-code-javascript/SKILL.md) & [n8n-code-python](../../01-automacao-n8n-make/n8n-code-python/SKILL.md):** Boas práticas para rodar scripts customizados dentro do nó "Code" do n8n.
*   **[n8n-agents](../../01-automacao-n8n-make/n8n-agents/SKILL.md):** Padrões específicos para configurar nós de Agente de IA com sub-ferramentas e memórias.

### 6.2. Como Usar com Antigravity / Claude Code

1.  **Antigravity:**
    *   Estas habilidades estão configuradas para serem descobertas no seu workspace.
    *   Quando você fizer perguntas complexas como *"Como crio um loop em lote (batch processing) no n8n?"*, o Antigravity lerá a habilidade [n8n-workflow-patterns](../../01-automacao-n8n-make/n8n-workflow-patterns/SKILL.md) e usará o padrão ideal automaticamente.
2.  **Claude Code:**
    *   Se você estiver usando o Claude Code, você pode adicionar a pasta `skills/` como plugins locais ou utilizar os markdowns como referências no seu contexto de prompt do sistema.

---
*Parte da [Skills Library](../../README.md)*

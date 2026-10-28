---
name: curriculo-blindado
description: Use ao submeter curriculo a banca de 7 avaliadores.
version: 1.0.0
author: <autor>, Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [carreira, curriculo, cv, ats, banca]
    related_skills: []
---

# Currículo Blindado — Banca de 7 Avaliadores

Protocolo adversarial para avaliação, estresse e blindagem de currículo contra uma vaga-alvo específica. Em vez de feedback complacente, simula uma banca de sete papéis com o mandato explícito de encontrar motivos para **reprovar** a candidatura. Aprovado apenas o que resistir ao escrutínio conjunto.

## When to Use

- Revisão e estresse máximo de currículo antes de aplicar para vaga de alta concorrência.
- Diagnóstico de por que um currículo não avança em processos seletivos.
- Reformulação completa de CV para passar por filtros ATS e liderança técnica.
- Preparação para entrevistas identificando antecipadamente as fraquezas do perfil.

## Entradas Obrigatórias

Antes de iniciar, exija o currículo e um alvo. Se faltar, pare e solicite:
1. **Currículo atual** (texto integral ou arquivo).
2. **Alvo**, em ordem de preferência:
   - **Descrição da vaga** (requisitos, diferenciais, contexto da empresa) → matriz de
     palavras-chave real;
   - ou, sem vaga, **cargo-alvo + senioridade** → a banca roda inteira, mas a matriz do ATS usa
     palavras-chave típicas do cargo e sai rotulada **"estimativa para o cargo (sem vaga)"**, assim
     como a nota ATS. Nunca apresente nota estimada como compatibilidade com vaga real.

Uma versão produto desta banca (app web) está documentada em
`<workspace>/<projeto>/docs/decisoes.md` — leia antes de mexer no prompt do app.

---

## A Banca de 7 Avaliadores

Cada avaliador atua de forma independente e impiedosa, sob sua respectiva ótica:

### 1. O Filtro Automático (ATS)
- **Papel:** Parser algorítmico de triagem inicial (Gupy, Greenhouse, Lever, Workday).
- **Critérios:**
  - Legibilidade estrutural (ausência de tabelas, colunas duplas, caixas de texto, ícones quebradores).
  - Matriz de palavras-chave da vaga: tabela categorizada em `TEM NO CV` | `NÃO TEM` | `TEM COM OUTRO NOME`.
  - Requisitos eliminatórios vs desejáveis.
- **Saída:**
  - Nota de compatibilidade: **0 a 100**.
  - Veredito: **PASSA** ou **BARRADO** (com motivo em 1 frase).

### 2. A Gestora da Vaga (Hiring Manager)
- **Papel:** Líder com pilha de 200 currículos e apenas **30 segundos** para decidir.
- **Critérios:** O que os olhos bateram primeiro? O que passou batido? Identificou senioridade real ou apenas volume de texto?
- **Saída:**
  - Diagnóstico dos 30 segundos.
  - Veredito: **CHAMARIA** ou **NÃO CHAMARIA** para entrevista (motivo principal).

### 3. O Futuro Chefe Direto (Tech Lead / Coordenador)
- **Pergunta central:** *"Essa pessoa resolve os problemas e gargalos do meu time ou vai me dar trabalho?"*
- **Critérios:** Profundidade técnica prática, domínio do ecossistema, autonomia, capacidade de entrega demonstrada.
- **Saída:** Primeira impressão em 1 frase, top 3 problemas/lacunas técnicas, nota de 0 a 10.

### 4. O Colega de Equipe (Par Técnico / Sênior)
- **Pergunta central:** *"Eu gostaria de trabalhar com essa pessoa e parear no dia a dia?"*
- **Critérios:** Clareza na comunicação, sinais de colaboração vs ego, capacidade de documentar e compartilhar contexto.
- **Saída:** Primeira impressão em 1 frase, top 3 ressalvas, nota de 0 a 10.

### 5. A Recrutadora (Talent Acquisition / RH)
- **Pergunta central:** *"O currículo é coerente, sem ruído, e consigo defendê-lo para a liderança?"*
- **Critérios:** Estabilidade e progressão na carreira, clareza das transições, ausência de clichês vazios ("proativo", "hands-on", "apaixonado por tech").
- **Saída:** Primeira impressão em 1 frase, top 3 inconsistências ou riscos, nota de 0 a 10.

### 6. O Concorrente (Outro Candidato à mesma vaga)
- **Pergunta central:** *"Onde o meu perfil ganha fácil desse currículo?"*
- **Critérios:** Falta de métricas concretas, ausência de certificações/cases de peso, descrições genéricas de atribuição em vez de impacto.
- **Saída:** Primeira impressão em 1 frase, top 3 pontos fracos exploráveis, nota de 0 a 10.

### 7. O Dono / Diretor (C-Level / Finanças)
- **Pergunta central:** *"Essa contratação gera retorno sobre o investimento ou é custo puro?"*
- **Critérios:** Percepção de impacto em receita, eficiência operacional, redução de custos ou risco de negócio.
- **Saída:** Primeira impressão em 1 frase, top 3 riscos de ROI, nota de 0 a 10.

---

## Protocolo de Execução Pós-Banca

Após colher os vereditos dos 7 avaliadores:

1. **Matriz Unificada de Problemas:**
   - Consolidar todos os apontamentos em lista única ordenada por gravidade (Eliminatório > Crítico > Melhoria), sem duplicidades.

2. **Versão Nova Blindada do Currículo:**
   - Reescrever o currículo corrigindo rigorosamente cada ponto levantado.
   - **Regra inegociável:** NUNCA inventar métricas, cargos ou tecnologias. Onde faltar dado concreto, inserir `[PREENCHER: métrica/resultado real]` para o usuário completar.
   - Estrutura de bullets sempre em STAR (Situação, Tarefa, Ação, Resultado) com verbos fortes de ação.
   - Formatação texto limpo/Markdown compatível com ATS (coluna única, cabeçalhos padrão).

3. **Re-teste Comparativo (Antes vs Depois):**
   - Submeter a versão nova novamente ao **Avaliador 1 (ATS)** e à **Avaliadora 2 (Gestora)**.
   - Apresentar: Score ATS (ex: 48 → 88) e Veredito da Gestora (Não chamaria → Chamaria).

4. **Preparação de Entrevista (5 Perguntas Ácidas):**
   - Listar as 5 perguntas mais difíceis que um entrevistador experiente fará ao ler o novo currículo, com a estratégia de resposta recomendada fundamentada na trajetória real do candidato.
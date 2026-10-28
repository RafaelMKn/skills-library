---
name: carreira-e-posicionamento
description: Use ao revisar currículo para ATS, reescrever LinkedIn, montar plano de estudos ou roadmap de carreira em tecnologia.
---

# Carreira e Posicionamento

Quatro rotinas separadas que compartilham a mesma exigência: realismo verificável em vez de aspiração. Nenhuma delas produz resultado útil com elogio — "seu perfil é fantástico" não passa em ATS nem convence recrutador.

| Rotina | Use quando |
|---|---|
| Currículo + ATS | Avaliar currículo contra vaga específica |
| LinkedIn | Reposicionar perfil para cargo alvo |
| Plano de estudos | Aprender uma skill com prazo e horas definidas |
| Roadmap de carreira | Planejar 12 a 36 meses |

**Regra que atravessa as quatro:** nunca inventar experiência, formação, certificação ou métrica. Currículo com dado inflado quebra na entrevista técnica, e aí o custo é a vaga inteira. Se falta métrica, pergunte ao usuário ou deixe o bullet sem número — não estime.

---

## 1. Currículo e adequação a ATS

Rode o prompt de `references/prompts.md` (seção "Currículo") com o currículo completo e a descrição da vaga.

A avaliação sai em cinco dimensões: match de palavra-chave (o que o ATS filtra), match de experiência (anos, stack, domínio), formação e certificação exigidas, soft skill sinalizada por verbo de ação, e compatibilidade de formato.

O que a entrega precisa ter:

- **Score de match 0-10 com justificativa.** Score sem justificativa é opinião.
- **Top 5 lacunas** separando o que é palavra-chave, o que é experiência real faltando e o que é formato.
- **3 a 5 bullets reescritos em STAR** (Situação-Tarefa-Ação-Resultado) com métrica concreta quando existir.
- **Reordenação de seções** e o que já está bom e não deve mudar.

Regras de formato para ATS: sem tabela, sem coluna, sem imagem, sem caractere especial quebrador, fonte legível. Parser de ATS ignora ou corrompe layout gráfico — currículo bonito em PDF de designer costuma entrar no sistema como texto embaralhado.

Proibido no texto: "player de equipe", "hands-on", "proativo", "apaixonado por tecnologia". Cada bullet abre com verbo forte e fecha em resultado.

---

## 2. LinkedIn

Reescreve Headline, About e as três últimas experiências para um cargo alvo declarado.

- **Headline** — 3 opções, cada uma com palavra-chave que recrutador digita na busca. Headline é campo indexado: "Desenvolvedor" perde de "Desenvolvedor Backend Python | n8n | Automação".
- **About** — 3 a 4 parágrafos: quem é, o que entrega, prova concreta, próximo passo. Sem clichê, com número.
- **Experiências** — bullets STAR, métrica quando existir.
- **Skills** — o que adicionar e o que remover (skill irrelevante dilui o perfil na busca).
- **Conteúdo** — 3 ideias de post que reforçam o posicionamento declarado.

Idioma segue o público: perfil para vaga internacional em inglês, mercado brasileiro em PT-BR. Perfil bilíngue mal feito fica pior que monolíngue bem feito.

---

## 3. Plano de estudos

Precisa de cinco dados antes de começar: skill alvo específica, nível atual, objetivo final, prazo e **horas reais por semana** — não as ideais.

A entrega cobre diagnóstico do nível, sequência de tópicos com justificativa de ordem, cronograma semanal com blocos de estudo/prática/revisão, três projetos crescentes em complexidade, marcos mensuráveis, estratégia de repetição espaçada e o que fazer ao travar.

Dois critérios que decidem se o plano serve:

- **80% prática, 20% teoria.** Programação não se aprende lendo.
- **Marco mensurável.** "Consigo construir X em Y horas" serve. "Domino Z" não serve — não há como verificar.

Cronograma feito sobre horas ideais é abandonado na segunda semana. Pergunte quantas horas a pessoa realmente tem, e planeje com menos do que ela disser.

---

## 4. Roadmap de carreira

Horizonte de 12 a 36 meses, em quatro trimestres: fundamentos, aprofundamento com projeto, posicionamento público, aplicação ou transição.

Precisa de: nível atual, stack, domínio, objetivo de 1 a 3 anos, valores não-negociáveis (salário, remoto, work-life) e riscos atuais.

A entrega inclui gap analysis, skills técnicas priorizadas **por retorno de carreira e não por hype**, skills de posicionamento (LinkedIn, conteúdo, networking), marcos trimestrais, plano B desde o dia 1 e riscos a monitorar — incluindo o impacto de IA sobre o domínio escolhido, que hoje é variável de primeira ordem e não nota de rodapé.

Não sugira troca de stack sem motivo de carreira claro. Aprender framework novo porque está em alta, sem vaga ou projeto que peça, é custo sem retorno.

---

## Como conduzir

Estas rotinas dependem de dado que só o usuário tem. Falta de informação se resolve perguntando, não estimando — e vale perguntar em bloco antes de produzir, em vez de entregar algo genérico e corrigir depois.

O tom da entrega é análise técnica: direto, com crítica onde cabe. "Você é fantástico" não ajuda ninguém a passar em ATS.

---

## Referências

- `references/prompts.md` — os quatro prompts XML completos

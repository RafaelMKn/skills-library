# Camada PT-BR: padrões de IA em português brasileiro

Os 34 padrões do SKILL.md principal foram catalogados a partir de texto em inglês. Eles pegam o vício conceitual (abstração vazia, elogio genérico, conclusão que se autoelogia), mas não pegam o vício **sintático** que texto de IA em português exibe — e alguns não têm equivalente em inglês.

Carregue esta referência quando o texto a humanizar estiver em português brasileiro. Ela soma ao SKILL.md; não substitui.

Adaptado do System Prompt AntIA v3 (Felipe / PycodeBR), com as seções de identidade editorial removidas: aqui ficam só as regras de língua.

---

## 1. O vício central: fragmentação sintática

O erro mais comum de IA escrevendo em português não é vocabulário, é **quebrar em fragmentos o que deveria ser um período articulado**. O modelo aprendeu que frase curta parece impactante, e aplica isso mecanicamente.

Artificial:

> Ferramenta. Custo. Equipe. Decisão.

Natural:

> A equipe compara o custo da ferramenta antes de decidir se ela cabe no projeto.

**Regra:** três ou mais períodos muito curtos em sequência, com a mesma cadência e o mesmo tipo de verbo, são parataxe rítmica. Una-os, ou transforme em lista se lista for genuinamente a melhor forma.

Período curto é permitido em capa, título, rótulo, comando, diálogo e CTA — onde o formato exige economia. No corpo explicativo, sequência de cortes artificiais não.

## 2. Palavras funcionais não são ruído

Artigo, preposição, conjunção, pronome e locução conectiva fazem parte da construção da mensagem. Texto de IA as remove para "enxugar", e o resultado lê como telegrama.

Preserve `e`, `o`, `a`, `com`, `para`, `de`, `da`, `do`, `em`, `no`, `na`, `por`, `que`, `porque`, `quando`, `enquanto`, `embora`, `mas`, `então`, `por isso` sempre que a gramática e a relação entre as ideias pedirem.

- Nunca elimine artigo, preposição ou conjunção só para encurtar.
- Nunca retire o conectivo que informa causa, contraste, consequência, condição ou tempo. A relação lógica desaparece com ele.
- Ao encurtar, remova **redundância, detalhe secundário e adjetivo vazio** — nunca estrutura gramatical.
- Mantenha as contrações naturais (`do`, `da`, `no`, `na`, `ao`, `à`, `pelo`, `pela`) quando forem a construção adequada.
- Conectivo se escolhe pelo sentido. Não encha o texto de conectores para simular fluidez.

## 3. Pontuação

- **Travessão (—) não se usa como pontuação** em texto produzido. Este é o tell nº 1 de IA em português brasileiro — o em-dash é comum em inglês editorial e raríssimo em escrita natural em PT-BR.
- `....` não é encerramento de frase. Nunca em copy, legenda, roteiro, anúncio ou material didático.
- `...` só quando reproduz interrupção, hesitação, diálogo ou citação preservada. Não para deixar o leitor esperando revelação.
- Não empilhe `!!!`, `??` ou `?!` para compensar argumento fraco.
- Dois-pontos organiza ou introduz. Não anuncia revelação dramática.
- Pergunta retórica pode existir quando é genuína. Em série, simula conversa e soa falso.

## 4. Moldes retóricos proibidos

### Oposição fabricada

- "Não é X. É Y."
- "Não é X, mas sim Y."
- "Não é sobre X, é sobre Y."
- "Não faça isso. Faça aquilo."

Qualquer construção que negue uma opção só para apresentar a seguinte como revelação. Negação é legítima quando corrige fato, delimita conceito ou evita interpretação errada — o bloqueio é contra o molde automático, não contra a palavra "não".

### Antecipação e teatralização

- "Resultado? X."
- "E isso muda tudo."
- "E aqui está o ponto."
- "E é aqui que o jogo muda." / "...que a mágica acontece."
- "Esse é o ponto que separa..."
- "A verdade é que..." quando só dramatiza
- "o segredo é" / "a revelação é" / "aqui vai o segredo:" como preparação vazia
- "no fim, fica assim:" como fórmula de conclusão
- "você ainda não está pronto para"

### Fórmulas e abstração

- Título no molde "Do X ao Y" quando existe alternativa descritiva.
- "X é Y", "X exige Y", "X define Y" repetidos sem contexto.
- Sujeito abstrato com verbo genérico e sem referente.
- Texto que caberia em qualquer perfil sem trocar uma palavra.
- Conclusão positiva genérica que só elogia o próprio texto.
- Enumeração técnica no lugar de explicação.
- Abertura pela sigla, ferramenta ou arquitetura antes de situar o problema.
- Metáfora literária onde descrição de engenharia é mais precisa.
- Antropomorfismo: ferramenta com intenção, opinião ou ação humana.

### Registro

- Ênclise em excesso em marketing e redes (`trata-se`, `percebe-se`, `dá-se`).
- Mesóclise em qualquer contexto (`dar-lhe-ei`, `fá-lo-ei`, `dir-se-ia`).
- Tom de anúncio apelativo, ritmo teatral, tom professoral exagerado.

## 5. Vocabulário a evitar

Sobretudo quando usado como abstração, ênfase ou muleta:

| Evitar | Por quê |
|---|---|
| clareza, claro, claramente | abstração sem referente |
| real, reais, realmente | ênfase vazia |
| travar, destravar, destrave | muleta de marketing digital BR |
| direção, direcionar, direcionamento | genérico |
| chave (como metáfora de solução) | "a chave é..." |
| jornada | clichê de infoproduto |
| transformar sua vida, mudar tudo | promessa não sustentada |
| game changer, revolucionário | hipérbole importada |
| poderoso, absurdo, incrível | adjetivo de entusiasmo |
| simplesmente, de verdade | filler |
| sem esforço, fácil, garantido | promessa falsa |

Prefira o termo específico que descreve o fato: `precisão`, `concreto`, `verificável`, `parar de responder`, `ficar bloqueado`, `apresentar uma falha`, `critério`, `prioridade`, `próximo passo`.

**Não troque palavra proibida por sinônimo automático.** Se o conceito não pode ser afirmado com precisão, reescreva a frase. Preserve o termo quando faz parte de nome próprio, citação, título oficial ou fato técnico indispensável.

## 6. Fluxo

O texto precisa progredir: o problema aparece com contexto suficiente, a causa ou o mecanismo é explicado, a consequência se relaciona ao leitor, o exemplo mostra o que fazer com a informação, o fechamento decorre do argumento.

Evite frase empilhada sem relação explícita, checklist disfarçado, bloco desconectado, parágrafo que abre e fecha com a mesma afirmação, impacto forçado em toda linha.

Lista organiza itens independentes — não substitui parágrafo automaticamente. Título orienta a leitura e descreve o cenário; não rotula etapa.

## 7. Checklist final (PT-BR)

Antes de entregar, valide silenciosamente:

1. Soaria natural em voz alta?
2. Cada parágrafo faz uma ideia avançar?
3. Artigos, preposições e conjunções necessárias estão preservados?
4. Virou sequência de palavras-chave ou fragmentos?
5. Tem `...`, `....`, `!!!`, `??` sem função?
6. Usa "Não é X. É Y." ou variação como fórmula?
7. Tem vocabulário da tabela acima sem necessidade semântica?
8. Repete o mesmo molde de frase em série?
9. Tem travessão como pontuação?
10. Depende de antecipação, suspense ou frase de efeito?
11. Tem referente e conectivo que permitem acompanhar o raciocínio?
12. Respeita o limite de tamanho sem mutilar a sintaxe?
13. Acentuação revisada?

## 8. Ao revisar texto recebido

Compare o antes e o depois para garantir que causa, condição, contraste e consequência **não desapareceram**. Preserve fato, nome, número, link e intenção. Altere só o que o pedido autoriza. Não invente experiência pessoal para dar voz ao texto.

A correção não é aplicar a fórmula inversa: recuperar a sintaxe adequada não significa transformar tudo em período longo.

---

Fonte: System Prompt AntIA v3, PycodeBR — seções 3 a 7 e 13, sem a camada de identidade editorial.

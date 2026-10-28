# Prompt de Execução — Banca de 7 Avaliadores

Caso deseje rodar a banca em uma única sessão ou enviar para um modelo externo, utilize o prompt abaixo:

```text
Você vai montar uma BANCA DE SETE AVALIADORES cujo trabalho é tentar REPROVAR o meu currículo para a vaga abaixo. Seja duro e específico, como uma empresa de verdade seria. Não invente nada sobre mim: use só o que está no currículo.

Antes de começar, se faltar o currículo, ou se faltarem ao mesmo tempo a vaga e o cargo-alvo com senioridade, peça o que falta e pare.
Se vier só cargo-alvo + senioridade (sem vaga), rode a banca inteira usando as palavras-chave típicas desse cargo e rotule a tabela e a nota do Avaliador 1 como "ESTIMATIVA PARA O CARGO (SEM VAGA)".

AVALIADOR 1: O FILTRO AUTOMÁTICO (ATS)
Faça o papel do sistema que filtra currículos antes de qualquer humano ler.
- Compare o currículo com os requisitos e as palavras-chave da vaga.
- Aponte o que um sistema desses não conseguiria ler (tabelas, colunas, imagens, títulos fora do padrão).
- Monte uma tabela com as palavras-chave da vaga: TEM no currículo / NÃO TEM / TEM COM OUTRO NOME.
- Dê uma nota de compatibilidade de 0 a 100.
- Veredito: PASSA ou BARRADO, e o motivo em uma frase.

AVALIADOR 2: A GESTORA DA VAGA
Faça o papel de quem decide quem vai para a entrevista.
- Você tem 30 segundos para olhar o currículo. Diga o que os seus olhos pegaram primeiro e o que passou batido.
- Veredito: CHAMARIA ou NÃO CHAMARIA para entrevista, e o motivo principal.

AVALIADORES 3 A 7: CINCO LEITORES, CADA UM COM SEU OLHAR
Cada um avalia sozinho, sem ler a opinião dos outros:
3. O futuro chefe direto: essa pessoa resolve os problemas do meu time?
4. Um colega de equipe: eu gostaria de trabalhar com essa pessoa?
5. A recrutadora: o currículo é claro, sem erros e fácil de defender para a gestora?
6. Outro candidato à mesma vaga: onde eu sou mais forte que esse currículo?
7. O dono da empresa: essa contratação vale o salário?
Para cada um: primeira impressão em uma frase, os 3 maiores problemas e uma nota de 0 a 10.

DEPOIS DA BANCA
1. Junte todos os problemas apontados numa lista única, do mais grave para o menos grave, sem repetir.
2. Escreva uma VERSÃO NOVA do meu currículo corrigindo cada problema da lista. Mantenha só fatos verdadeiros do currículo original; onde faltar uma informação (um número, um resultado), escreva [PREENCHER: o que falta] em vez de inventar.
   Use verbos de ação e resultados, coloque as palavras-chave da vaga onde elas forem verdade e mantenha o formato simples (sem tabelas, colunas ou imagens), para o filtro automático conseguir ler.
3. Passe a versão nova de novo pelo Avaliador 1 e pela Avaliadora 2 e mostre os vereditos e a nota de compatibilidade novos (antes → depois).
4. Liste as 5 perguntas que um entrevistador faria ao ler a versão nova, com uma dica curta de como eu responderia cada uma usando o que está no currículo.

Responda em português do Brasil.

MEU CURRÍCULO:
[cole aqui]

A VAGA (opcional):
[cole aqui o anúncio da vaga]

CARGO-ALVO E SENIORIDADE (obrigatório se não houver vaga):
[ex.: Analista de Dados Pleno]
```

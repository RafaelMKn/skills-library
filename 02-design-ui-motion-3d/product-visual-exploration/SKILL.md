---
name: product-visual-exploration
description: "Use when exploring physical-product designs and mockups."
version: 1.0.0
author: "<autor>"
license: MIT
metadata:
  hermes:
    tags: [design, references, apparel, mockups, physical-products]
    related_skills: [claude-design]
---

# Exploração visual de produtos físicos

Use para uniformes, vestuário e outros produtos físicos que passam por referências, alternativas de desenho e apresentação de uma direção aprovada. Use `claude-design` como apoio para a página de comparação, não como substituto do design do produto.

## When to Use

- Pesquisar referências e organizar opções para um produto físico.
- Criar ou revisar rotas de uniformes e vestuário.
- Converter uma direção aprovada em mockups de apresentação.

## Procedimento

1. **Fixe as restrições do produto.** Separe requisitos obrigatórios de preferências: cores, posições de marcas, versões, referências aprovadas e limitações de fabricação ou uso. Em continuação, aproveite o briefing existente; não reabra decisões resolvidas.
2. **Colete e confira referências reais.** Pesquise fontes de fabricantes e publicações; registre URL da página, URL original da imagem e caminho local. Baixe as fotos e confira visualmente antes de escrever motivos. Use folha de contato para triagem e imagens individuais para detalhes pequenos. Pesquisa de tendências recentes só é necessária quando recência muda a decisão.
3. **Entregue primeiro uma comparação simples.** Foto ao lado de motivo, aplicação e cuidado, com números estáveis para selecionar. Quando o pedido for apenas subir referências em localhost, priorize HTML utilizável e fotos sobre filtros, favoritos e refinamento do front. Não deixe a primeira entrega depender de um painel sofisticado.
4. **Sirva e confira a página exata.** Use um diretório do projeto e servidor ligado ao loopback, por exemplo `python3 -m http.server <porta> --bind 127.0.0.1 --directory <diretório>`. Leia o HTML servido e confira os assets: HTTP 200 de uma listagem de diretório não prova entrega do painel. Inspecione screenshot quando aparência for critério de aceitação.
5. **Converta a seleção em rotas distintas.** Restrinja as novas rotas às referências escolhidas; explique o que cada uma fornece sem copiar marcas ou estampas. Varie construção, direção de linhas, distribuição e densidade do grafismo, não apenas cores. Inclua duas versões coordenadas quando exigido. Para roupas, mostre frente e costas e mantenha a identidade nas costas.
6. **Itere no produto, não no recipiente.** Quando o feedback for que ficou minimalista, acrescente detalhes coerentes à peça: painéis, acabamentos, mangas, recortes e grafismo. Não responda apenas decorando o painel HTML. Preserve versões anteriores para comparação. Quando o usuário pedir mais influência de uma referência ousada, faça essa influência aparecer no tamanho e presença do grafismo, em vez de reduzi-la a textura invisível.
7. **Consolide a direção aprovada antes do realismo.** Para mockup fotorealista, renderize frente e costas aprovadas como referências raster e forneça a marca real separadamente ao gerador solicitado. Preserve geometria, cores e posição da marca; não use geração como pretexto para redesenhar. Quando a decisão for entre cores obrigatórias marcantes e discretas, cruze essas duas intensidades com cada base do par aprovado, mantendo enquadramento, luz e escala constantes; não mude simultaneamente o corte ou a geometria. Gere primeiro pranchas de produto frente/costas e use atletas apenas como complemento de caimento. Só declare geração por um modelo depois de receber imagens reais e confira os metadados retornados. Não apresente SVG como fotografia gerada nem caminho ainda não exercitado como receita validada. Consulte `references/image-generation-fidelity.md` para execução, recibos e conferência de fidelidade.
8. **Confira e entregue.** Inspecione todas as versões em escala legível; confira marcas, cores obrigatórias e continuidade frente/costas. Diga brevemente o que mudou, onde abrir e o que depende de arte oficial ou produção. Se solicitado abrir no navegador, execute a abertura; confira o navegador escolhido em vez de assumir que o padrão é o pedido.

## Regras para uniformes e silhueta

- Interprete lados pelo corpo de quem veste: peito esquerdo do atleta aparece à direita de quem olha uma vista frontal. Preserve essa orientação ao gerar imagens, que podem espelhar o desenho.
- Use o arquivo real da marca. Identifique recorte de banner como provisório e solicite vetor para produção; não redesenhe uma marca tipográfica e apresente como oficial.
- Faça a cor predominante mudar no corpo inteiro e nas costas entre versões — trocar apenas punhos ou mangas não resolve conflito.
- Mantenha todas as cores obrigatórias visíveis em cada versão; um requisito de paleta não é satisfeito apenas pelo conjunto de versões.
- Para valorizar visualmente a silhueta, explore diagonais que abrem nos ombros e convergem na cintura, painéis laterais escuros e linhas longitudinais ou curvas que acompanham o torso. Descreva como intenção visual, não como efeito físico comprovado. Evite barras horizontais grossas na cintura quando a intenção for afunilar.
- Reserve uma área de leitura para a marca sem tornar todo o peito vazio por padrão; densidade e legibilidade podem coexistir.
- Diferencie presença de cor de continuidade de linha. Quando o usuário pedir acentos isolados, use segmentos com vãos visíveis e pontas livres; não una ombros, laterais e cintura em molduras nem feche chevrons, gola e punhos por padrão. Preserve o grafismo aprovado e altere apenas a conexão dos acentos — linhas corridas mudam a leitura da peça mesmo com a mesma paleta.
- Trate contraste esportivo como requisito de uso real. Não use razão WCAG de cores digitais como prova de distinção entre uniformes ou contraste com a bola. Leia o regulamento aplicável e valide bola, iluminação, tecido e amostra; não declare homologação por estudo visual.
- Separe esquema vetorial, mockup de apresentação e arte de produção. Sombra e textura no SVG não o transformam em fotografia; imagem gerada não prova fidelidade de estampa, corte ou marca.

## Limite de escopo

Esta skill governa a escolha e evolução do desenho de um produto físico. Para UI/frontend, use `claude-design` ou `impeccable`; para integração de provedor de imagens, consulte documentação e infraestrutura atuais antes de executar. Não fixe comandos de autenticação ou modelos não verificados aqui.

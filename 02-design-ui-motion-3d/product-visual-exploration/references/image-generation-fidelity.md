# Mockups gerados: execução e fidelidade

## 1. Prepare referências com hierarquia

- Renderize a direção aprovada em PNG, frente e costas, para cada cor predominante. Inclua a marca real como arquivo separado.
- Indique no prompt que a geometria aprovada prevalece sobre fotografias anteriores; usar apenas um mockup anterior como referência propaga suas alterações.
- Descreva explicitamente a característica aprovada: facetas longas orientadas em V não equivalem a triângulos curtos aleatórios. Fixe comprimento, direção, área de aplicação e alinhamento com cintura/ombros.
- Preserve a geometria ao explorar intensidade de cores. Compare uma matriz simples: base escura/clara ou preta/vermelha × tricolor protagonista/discreto. Exija as cores obrigatórias também nos detalhes discretos e nas costas.

## 2. Execute pelo provedor solicitado

1. Confira a ferramenta de imagem disponível e a documentação atual; não presuma que o provedor de conversa também gera imagens.
2. Se não houver ferramenta exposta, inspecione a integração instalada antes de substituir o modelo. A integração Hermes `plugins/image_gen/openai-codex/__init__.py` foi exercitada para gerar imagens com referências locais via a classe `OpenAICodexImageGenProvider`; confira a assinatura atual de `generate` e o formato do resultado antes de chamar.
3. Reuse a resolução de autenticação da integração, sem ler ou imprimir credenciais. Essa rota utilizou autenticação Codex existente; não invente uma API pública equivalente nem modifique configuração global para uma rodada de mockups.
4. Use um intérprete que tenha as dependências da integração. Reuse scripts de geração já exercitados no projeto quando existirem, lendo-os primeiro.
5. Grave prompts e recibos JSON com ID da requisição, provedor, modelo solicitado, parâmetros solicitados, valores reportados, entradas e caminho de saída. Exclua credenciais e base64 dos recibos.
6. Copie imagens materializadas para o diretório do projeto e crie uma galeria com assets locais. A geração precisa produzir arquivos reais, não apenas links previstos.

### Edição localizada de linhas e acabamentos

1. Use a variante que o usuário apontou como imagem principal; acrescente o exemplo anterior apenas como referência da característica solicitada, junto da marca real.
2. Especifique o delta e os invariantes: alterar somente a continuidade dos acentos, mantendo base, facetas, caimento, posição da marca, enquadramento e vistas. Não gere também outras cores quando a correção se refere a uma opção.
3. Para linhas isoladas, peça segmentos curtos e médios de comprimento variável, separados por tecido, sem pontas que se tocam, circuitos ombro–lateral–cintura, V contínuo ou anéis completos em gola/punhos.
4. Confira visualmente os vãos nas duas vistas; não aceite simplesmente menos contraste como cumprimento de uma alteração de geometria. Preserve as cores obrigatórias mesmo com acentos interrompidos.
5. Salve uma nova imagem e uma comparação antes/depois; mantenha o original para que o usuário veja a intervenção específica.

## 3. Separe solicitado de reportado

- Registre qualidade e tamanho retornados: o backend pode devolver qualidade média apesar de alta solicitada, e dimensões diferentes do pedido.
- Não trate o campo de modelo montado pelo cliente como confirmação independente do modelo executado. Quando o backend não reportar o modelo, identifique a integração usada e o modelo solicitado sem alegar comprovação extra.
- Não chame o resultado de alta qualidade técnica apenas porque o pedido continha `high`; relate a qualidade reportada quando ela divergir.

## 4. Confira antes da apresentação

- Abra cada imagem e confirme dimensões, integridade, logo no lado anatômico correto, paleta em cada peça, geometria do desenho e costas. Inspecione cada prancha em tamanho legível, não somente uma miniatura de página inteira.
- Compare o mockup ao raster aprovado. Examine facetas, convergência do V, chevron da cintura, punhos e linhas laterais: realismo convincente pode esconder redesenho.
- Corrija a característica principal aprovada quando ela se perder; use um recorte ampliado da geometria como referência adicional, em vez de gerar repetidamente com o mesmo prompt genérico.
- Informe desvios remanescentes na galeria e na entrega. Não descreva o mockup como reprodução exata quando a IA alterou os grafismos.
- Confira a URL da galeria e cada imagem servida. Mostre o resultado com aviso de simulação, marca provisória quando aplicável e necessidade de arte de produção separada.

## 5. Preparação para compartilhar os mockups

1. Enumere os arquivos de saída reais das rodadas e exclua imagens de entrada, logo isolada, referências de terceiros e esquemas vetoriais; o pedido de todos os realistas não inclui todo PNG da pasta.
2. Monte um manifesto com caminho, tamanho e hash, deduplique por conteúdo e derive a contagem em código. Se empacotar em ZIP, confira a integridade e a quantidade de imagens internas antes de entregar.
3. Antes de prometer envio, confira destinatário e suporte a mídia no canal efetivamente conectado. Capacidade de enviar texto não comprova capacidade de anexar imagens; preparar um ZIP não equivale a enviá-lo.
4. Identifique o material como simulação para apresentação, com marca provisória quando aplicável. Guarde comprovantes de envio separados dos recibos de geração.

## 6. Pesquisa de semelhança

- Compare fotos reais de uniformes, distinguindo paleta, estrutura de faixas, geometria e marcas; associação de cores não prova cópia.
- Rotule impressões visuais como interpretações, não como resultado de pesquisa. Sem comparação verificável, não declare que não existe time semelhante nem certifique originalidade.
- Mantenha a pesquisa de semelhança separada da homologação esportiva e de uma avaliação jurídica: cada uma exige evidências próprias.

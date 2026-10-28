# Integração de imagens editoriais

1. Abra a imagem e observe o que mostra antes de escrever alt ou legenda. Atribuí-la a um personagem fictício não identifica a pessoa real nem comprova origem, autoria ou licença.
2. Escolha os IDs de reportagens pelo assunto. Reutilizar a foto de um casal na aproximação e no encontro é coerente; apresentar retrato de suspeito como prova de crime não é.
3. Confira detalhes que contradizem a interpretação literal. Uma foto de luto com outro nome na lápide pode servir como ambientação, com legenda informando que não é o túmulo do personagem. Não altere o nome nem invente o contexto da cena.
4. Preserve o original em assets de desenvolvimento. Gere WebP/JPEG de boa qualidade com Pillow, medindo dimensões e hashes por ferramenta. Cartazes exigem legibilidade de palavras; fotos precisam preservar rostos e objetos relevantes.
5. Incorpore data URI para HTML único offline. Centralize assets reutilizados quando possível para evitar payload repetido sem necessidade.
6. Preserve composição integral e altura proporcional no artigo. Use `object-fit: contain` nas miniaturas de cartazes e cenas com pessoas separadas, pois `cover` pode cortar palavras, rosto ou objeto importante.
7. Use alt descritivo e legenda contextual. Registre material recebido como fornecido pelo usuário, com autoria/licença não informadas quando desconhecidas. Para stock, registre URLs da página e arquivo, autor e licença apenas quando verificados.

## Buscar o que falta

Priorize fotos recebidas para coerência dos personagens. Sem registro adequado, busque objetos/ambientes pertinentes: flores para despedida, microfone para transmissão, celular para postagem. Identifique como ilustração, não registro do fato. Valide download real, tipo de arquivo e imagem visualmente. Se a página bloquear mas o arquivo oficial estiver acessível, valide esse arquivo e declare as lacunas de autoria, sem inventar dados da página. Não use pessoas reais aleatórias para representar acusados ou romances só porque a busca retornou um retrato.

## Regressão

Capture baseline dos dados antes da troca. Compare hashes dos registros não afetados e textos de todo o catálogo. Confirme que capa, busca e artigo usam o mesmo novo asset; confira dimensões naturais, proporção e enquadramento nas duas larguras. Observe rede e erros JS para entrega offline. Atualize expectativas legítimas de reutilização de fotos sem enfraquecer os testes de preservação.

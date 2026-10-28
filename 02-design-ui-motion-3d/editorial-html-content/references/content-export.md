# Exportar conteúdo para história ou podcast

1. Leia o catálogo atual do artefato ou sua fonte estruturada realmente utilizada. A conversa contém matérias excluídas e versões substituídas.
2. Extraia títulos, subtítulos e corpos; exclua data URIs, menus, alts e controles. Para JSON incorporado ao script, delimite sua declaração e use `json.loads`, não `eval`. Converta parágrafos com `HTMLParser` ou parser equivalente, preservando entidades, acentos e ordem.
3. Conte programaticamente as reportagens e compare com o catálogo vigente. Confira ausência dos itens descartados e suas frases exclusivas.
4. Produza Markdown com título, contexto ficcional, personagens e textos completos na sequência dos fatos. Cabeçalhos de assunto não precisam virar episódios de podcast. Não acrescente diálogos dramatizados a um pedido de compilação.
5. Separe orientações à IA do conteúdo narrativo. Registre incertezas que o podcast não deve resolver: romance não confirmado, suspeito sem culpa comprovada, causa de morte desconhecida e desfecho removido. Não invente provas, testemunhos, datas ou conclusões para criar drama.
6. Distinga adaptação de obra original e não atribua ao autor original frases criadas para o projeto.
7. Preserve o conteúdo aprovado quando o pedido for reunir informações. Use humanizer para oralidade apenas quando houver pedido de reescrita, mantendo a mesma cadeia de fatos.
8. Grave o Markdown, valide cobertura e ausência de tags HTML, e entregue o arquivo no chat. Não gere áudio, publique podcast ou estime duração como fato sem pedido e execução correspondentes.

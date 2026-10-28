# Spec técnica a partir de proposta funcional

Use quando já existe proposta funcional/decisões (Q#) e o pedido é "fechar a spec técnica" ou
"o que falta decidir". Entregável: `docs/spec-tecnica.md`, novo arquivo; não edite os docs existentes.

## Esqueleto

1. Cabeçalho: status ("esqueleto com decisões pendentes, não autoriza implementação"), docs-base,
   sessão de origem, e duas linhas de estado: conta/sistema inspecionado? validação do cliente registrada?
2. Legenda de fonte: `[doc]` arquivo do projeto, `[<Fornecedor>]` doc oficial conferida (ID do artigo),
   `[não confirmado]` afirmado por pesquisa sem prova na página.
3. §0 Pré-condições (P#): validação do cliente, inspeção somente leitura, acesso necessário.
4. Uma seção por etapa da proposta: o que a plataforma oferece (com fonte) → matriz/desenho proposto
   (célula sem decisão aponta para o D#) → proibições conhecidas → roteiro de teste T# com backup/rollback
   antes da mudança e critério de aceite.
5. Quando houver mais de um mecanismo viável, liste A/B/C com custo e fonte e deixe como D#; não escolha
   antes da inspeção.
6. Regras já decididas: só referência ao Q#, sem reabrir.
7. Tabela D# | decisão | quem decide | bloqueia o quê. D0 = validação do cliente, quando faltar.
   Inclua sempre "quem executa" (a agência configura x entrega roteiro).
8. Divergência entre o pedido original do cliente e a decisão tomada: registrar com consequência se
   o cliente insistir.

## Na resposta ao usuário

Agrupe as D# por quem destrava: só o cliente / usuário agora / usuário depois da inspeção. Diga o que foi
confirmado na doc oficial, o que ficou `[não confirmado]` e qualquer erro de subagente corrigido.
Próximo passo típico: rodada de `grilling` para as D# do usuário + mensagem ao cliente com as dele.

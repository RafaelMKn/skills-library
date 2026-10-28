---
name: documentos-dados-publicos
description: "Use ao coletar documentos e bases oficiais em lote."
metadata:
  hermes:
    tags: [research, dados-publicos, documentos]
    related_skills: [grounded-citations, pdf]
---

# Documentos e dados públicos

## Procedimento

1. Defina órgão, período, categoria e universo solicitado. Pergunte apenas quando a ambiguidade muda a fonte ou o conjunto de arquivos; não escolha silenciosamente uma eleição ou edição.
2. Localize o catálogo oficial antes de construir URLs de download. Prefira recursos estruturados e pacotes em lote a abrir uma página por registro. Em CKAN, consulte `api/3/action/package_show?id=<dataset>` e use `resources[].url`. Para dados eleitorais brasileiros, siga [references/tse.md](references/tse.md).
3. Registre as fontes com `grounded-citations`. Baixe com falha explícita em erro HTTP (`curl -fL --max-time ... -o ...`). Se a extração web falhar, tente catálogo/API ou download direto observado; uma falha do extrator não prova indisponibilidade da fonte.
4. Leia esquema e data de geração dentro da base. Filtre a categoria pelo campo próprio e deduplique por identificador estável; agregados nacionais podem repetir registros regionais.
5. Una informações complementares pelo identificador, especialmente situação do registro. Separe registro encontrado, aprovação, substituição e presença no conjunto atual; um campo não prova os outros.
6. Grave manifesto com identificador, nome, fonte, situação, arquivo e páginas quando aplicável. Reconcilie programaticamente os IDs da base com os documentos; declare ausentes e extras em vez de afirmar cobertura completa só pelo número de downloads.
7. Preserve os bytes dos originais. Entregue documentos individuais com nomes identificáveis, índice e, quando útil, PDF consolidado com marcadores por registro. Identifique fichas produzidas a partir de dados como **compilações**, nunca como cópias de formulários oficiais. Não inclua CPF, título eleitoral ou outros identificadores pessoais desnecessários.
8. Verifique integridade do ZIP, abertura dos PDFs, quantidade de registros únicos e soma das páginas do consolidado. Carregue `pdf` para manipulação e confira visualmente uma página representativa da ficha gerada. Preserve os originais mesmo quando o leitor reparar estruturas durante a consolidação.
9. Entregue arquivos, não apenas links ou instruções. Informe escopo, origem, data da base e exceções relevantes; use totais calculados pelo manifesto. Não transforme coleta em análise de conteúdo que não foi realizada.

## Regras de escopo

- Diferencie documento formal de coleção exaustiva de declarações: um plano de governo não contém necessariamente todas as promessas de campanha.
- Não descarte registros históricos/substituídos sem explicar o recorte; “todos” pode incluir registros fora da lista atual.
- Não infira ausência de documento por uma URL construída que retorna 404; descubra o recurso no catálogo, pois pacotes nacionais e regionais podem usar convenções diferentes.

## Conclusão

Confirme universo e IDs únicos; reconciliação do manifesto; exceções descritas sem equivalências falsas; originais preservados e compilações rotuladas; arquivos abertos e entregues. Nenhuma contagem vem da memória.

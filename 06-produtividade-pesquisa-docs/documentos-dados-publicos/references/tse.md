# TSE: candidaturas e propostas de governo

## Descoberta

1. Confirme o ano eleitoral.
2. Consulte `https://dadosabertos.tse.jus.br/api/3/action/package_show?id=candidatos-<ANO>`.
3. Verifique `success` e selecione em `result.resources` **Candidatos**, **Candidatos - Informações complementares** e **BR - Proposta de governo** para Presidência. Use as URLs retornadas, não adivinhe sufixos.
4. Registre catálogo e downloads como fontes. DivulgaCandContas é alternativa para consulta individual, não precisa ser a primeira rota de uma coleta em lote.

## Leitura e reconciliação

Os pacotes consultados usam CSV separado por `;` e Latin-1. Inspecione cabeçalhos e encoding antes de generalizar para outras edições.

```python
import csv, io, zipfile
rows = {}
with zipfile.ZipFile(candidatos_zip) as z:
    for member in z.namelist():
        if not member.lower().endswith('.csv'):
            continue
        reader = csv.DictReader(
            io.StringIO(z.read(member).decode('latin1')), delimiter=';'
        )
        for row in reader:
            if row.get('DS_CARGO') == 'PRESIDENTE':
                rows[row['SQ_CANDIDATO']] = row
```

- Una a base complementar por `SQ_CANDIDATO`.
- Leia `DT_GERACAO` e `HH_GERACAO` dos registros, não da coleta nem de notícias.
- Consulte `DS_SITUACAO_JULGAMENTO`, `ST_SUBSTITUIDO` e `ST_CANDIDATO_INSERIDO_URNA` na base complementar. Preserve valores literais; presença na urna não prova deferimento.
- Não interprete `#NE` ou `#NULO` como status jurídico; busque os campos específicos e declare lacunas.
- Os documentos presidenciais observados seguem `BR/<ANO>BR<SQ_CANDIDATO>_01.pdf`. Inspecione o ZIP antes de usar esse padrão: outras edições podem ter múltiplas versões ou nomenclatura diferente.
- Exclua arquivos de instruções, como `leiame.pdf`, da contagem. Compare IDs extraídos dos nomes com IDs das candidaturas e liste diferenças.

## Entrega

- Fichas compiladas: nome completo e de urna, número, partido, coligação, ocupação/escolaridade quando úteis, situação e ID do TSE.
- Planos: original por candidatura com nome identificável; opcionalmente PDF único com marcadores.
- Manifesto: ID, nome, partido, número, situação, arquivo e páginas.
- Informe separadamente registros da base, inseridos na urna e documentos encontrados. Mantenha substituídos como históricos quando o pedido for amplo, sem apresentá-los como candidatos atuais.
- Use **plano de governo** ou **proposta de governo registrada no TSE**, não “levantamento completo de promessas de campanha”.

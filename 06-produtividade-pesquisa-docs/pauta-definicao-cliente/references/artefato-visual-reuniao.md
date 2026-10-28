# Artefato visual de reunião — render, conferência e ajuste de página

Para deck e registro de decisão da <empresa>. Tokens da marca:
`<workspace>/<projeto-de-marca>/identidade-visual.md` — leia antes, não invente cor.

## Onde o arquivo vive

`clientes/<cliente>/projetos/<projeto>/docs/<tipo>-<tema>-<AAAA-MM-DD>.html`, com o PDF irmão ao
lado (reunião interna/sócio: `<workspace>/operacao/reunioes/<AAAA-MM-DD>-<pessoa>/`). No chat, entregue os dois: `::preview{file="...html"}` para ver na hora e `MEDIA:<caminho>.pdf`
para mandar adiante.

## Render e conferência

Chrome headless resolve render, screenshot e PDF sem dependência extra:

```bash
# PNG para conferir
google-chrome --headless --disable-gpu --hide-scrollbars \
  --window-size=1200,<altura> --screenshot=<saida>.png \
  --virtual-time-budget=6000 "file://$PWD/<arquivo>.html"

# PDF para circular
google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=<arquivo>.pdf --virtual-time-budget=7000 "file://$PWD/<arquivo>.html"
```

`--virtual-time-budget` precisa ser generoso: sem ele a fonte do Google Fonts não carrega e você
confere um layout que não é o que o cliente vê.

**Deck em slides não rola:** um screenshot só mostra o slide ativo, e conferir apenas a capa aprova
o resto sem ver. Gere um PNG por slide em 1920×1080: para cada n, faça uma cópia temporária
do HTML trocando `go(0)` por `go(n)`, rode o screenshot nela e olhe todos os PNGs. O esqueleto ainda vazio
também passa por essa conferência antes de ser entregue.

**Confira em fatias, não na peça inteira.** Screenshot de página longa reduzido para visão fica
ilegível e você aprova defeito sem ver. Corte em faixas de ~1300px e olhe cada uma:

```python
from PIL import Image
im = Image.open('peca.png')
for i in range(0, im.size[1], 1300):
    im.crop((0, i, im.size[0], min(i+1310, im.size[1]))).save(f'fatia{i//1300}.png')
```

O que procurar: rótulo quebrando em duas linhas, card desalinhado, texto cortado na borda, rodapé
incompleto. Rótulo curto de duas palavras (`PASSO 2`) quebra quando a coluna da grade é estreita —
alargue a coluna e ponha `white-space:nowrap`, não diminua a fonte.

## Fechar em uma página A4

A contagem de páginas do PDF é a **única** medida confiável. Todas as tentativas de medir altura no
DOM enganam:

- `height:297mm` + `overflow:hidden` esconde o excesso — o elemento reporta a altura fixa e você
  conclui que coube;
- `min-height:297mm` contamina `scrollHeight` — o conteúdo natural fica mascarado pelo mínimo;
- varrer pixel de conteúdo no screenshot depende da janela pedida, não do que a impressão faz.

Leia a contagem direto do PDF e busque o fator por bisseção:

```python
import re, subprocess

def paginas(scale, src, tmp_html, tmp_pdf):
    base = open(src, encoding='utf-8').read()
    css = f'@media print{{ .page{{ zoom:{scale}; }} }}'
    open(tmp_html, 'w', encoding='utf-8').write(base.replace('</style>', css + '</style>'))
    subprocess.run(['google-chrome', '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={tmp_pdf}', '--virtual-time-budget=6000',
                    f'file://{tmp_html}'], capture_output=True)
    d = open(tmp_pdf, 'rb').read()
    return int(re.search(rb'/Type\s*/Pages.*?/Count\s+(\d+)', d, re.S).group(1))

for sc in ['1.0', '0.96', '0.94', '0.92', '0.90']:
    print(sc, paginas(sc, ...))
```

Ache o primeiro fator que devolve `1` e **aplique um degrau abaixo dele** — o limite exato não tem
margem para a fonte renderizar um pixel diferente noutra máquina.

O `zoom` fica em `@media print`, nunca global: na tela a peça continua em tamanho cheio, e só a
impressão encolhe. Antes de recorrer ao `zoom`, corte de verdade — cabeçalho, entrelinha e as duas
frases mais longas costumam render 20% sozinhos, e texto cortado lê melhor que texto reduzido.

**PDF com bytes idênticos depois de editar o HTML significa cache.** Apague o PDF antes de
regerar, e confirme a edição no arquivo (`grep` do trecho novo) antes de culpar o CSS.

## Mapa de status (o que temos × o que falta)

Página para abrir no navegador e conduzir a conversa. Ordem:

1. **Cabeçalho**: sobrancelha (projeto · fase), título, uma frase com o critério de pronto, e um menu
   de âncoras para as seções.
2. **Placar de 3 números**: prontos · prontos sem prova real · faltam fazer. O card que "falta" tem
   borda no acento de alerta.
3. **Trilho do caminho ponta a ponta** (do ponto de vista do lead ou usuário), um passo por linha:
   bolinha numerada na cor do estado, título em linguagem leiga, etiqueta do sistema que executa
   (`GHL`, `n8n`, `GHL → n8n`, `Equipe`), uma frase, links do passo, selo de estado e quem faz. Fundo
   tingido nas linhas que faltam.
4. **Inventário em grade 2×2**, um card por sistema (CRM · automação · banco · pendências nossas),
   item com selo à direita. Item que existe mas está fora do escopo fica esmaecido, com selo cinza
   ("Reserva", "Sem uso"), e não é apagado da peça: explica por que existe.
5. **Tabela de referências**: o quê × onde, com o aviso de quais links pedem login e quais são
   locais. Documento desatualizado ganha a nota em vermelho.

Quatro estados com cor fixa: verde pronto, âmbar pronto sem prova real, vermelho falta, cinza fora
do escopo. "Instalado" não é "pronto": o que nunca rodou em execução real é âmbar.

**Links:**
- Workflow n8n: `https://<instância>/workflow/<id>`. Pegue os IDs dos subfluxos no JSON do fluxo
  principal (`parameters.workflowId.value` dos nós `executeWorkflow`/`toolWorkflow`), porque a
  documentação costuma esquecer algum.
- Arquivo do repo: caminho relativo à pasta do HTML, e todos testados:
  `grep -oE 'href="[^"#h][^"]*"' x.html | sed 's/href="//;s/"$//' | while read p; do [ -e "$p" ] || echo FALTA $p; done`
- Não chute formato de URL que você não confirmou (workflow individual do GHL, painel do Supabase).
  Use a página de lista confirmada e diga que falta o link direto.
- Externos com `target="_blank"` e um `↗` via `a.ext::after`. Na impressão, o `↗` sai.

**Conferência no navegador:** `new_tab("file://...")` e fixe a viewport com
`cdp('Emulation.setDeviceMetricsOverride', width=1280, height=1100, deviceScaleFactor=1, mobile=False)`
antes do screenshot. Com `scroll-behavior:smooth` na página, `scrollIntoView` captura no meio da
rolagem: desligue (`document.documentElement.style.scrollBehavior='auto'`) e use `window.scrollTo`.
O que costuma quebrar: selo em `grid` esticando para oval na altura do item. Resolva com
`align-self:start` no selo.

## Estrutura do registro de decisão

Uma página, nesta ordem:

1. **Cabeçalho escuro** — título com a decisão em destaque no acento, uma linha de contexto.
2. **Faixa de três números** que enquadram a lacuna.
3. **Grade 2×2 de cards**, um por ponto a decidir. Cada card: índice, título, etiqueta de gravidade
   (`TRAVA O CRM`, `BLOQUEIO`), quem decide, duas a três frases de contexto, opções A/B/C com a
   recomendada em destaque, e a linha de marcar com caixas.
4. **Fecho** — a frase que justifica decidir hoje, ao lado da sequência do que acontece depois.
5. **Rodapé** — situação em uma linha (`especificado, nada construído, nada aplicado`) e onde está o
   detalhamento técnico.

A etiqueta de gravidade é o que faz a reunião atacar na ordem certa sem você conduzir.

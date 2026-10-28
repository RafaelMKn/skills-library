# HTML do relatório e gráficos Spell UI

O usuário quer os gráficos do relatório com **Spell UI** (spell.sh).

## O componente `@spell/chart`

Inspecione sem instalar: `curl -sL https://spell.sh/r/chart.json` (registry shadcn; o código
fica em `files[0].content`). Depende só de `react` + `@/lib/utils` (`cn`). Salve uma cópia em
`<projeto>/referencias/spell-chart.tsx` para o subagente usar sem rede.

Props: `data: number[]`, `labels?: string[]`, `name`, `color` (hex), `width` (aspecto fixo
640:220), `formatValue`, `defaultIndex`, `showXAxis`, `reveal`, `showFill`, `showDot`,
`animated`, `tickCount`.

Limites — decida o desenho do relatório em torno deles:
- **Uma série por gráfico.** Comparar total × agente = dois gráficos lado a lado.
- **Sem linha de marcação/anotação.** Marque a data de mudança de regra no `labels` do ponto
  (ex.: `"17/08 ▸ nova regra"`) ou em texto ao lado.
- **Só linha** — sem barra, funil ou pizza. Séries com 3 pontos (meses) e funis ficam melhores
  como cards/tabela.

Use para série semanal (≥ 8 pontos). Não customize o componente para multi-série sem o usuário
pedir — custo alto, ganho pequeno numa call.

## Armadilhas do chart no estado estático (screenshot, PDF, início da call)

Peça no briefing, não descubra na revisão:
- **Tooltip aparece aberto no último ponto e cobre rótulos do eixo X.** Esconda o card até haver
  hover (opacidade 0 via CSS no wrapper), sem mexer na lógica do componente.
- **Ticks automáticos pulam o ponto que importa.** A semana da mudança de regra precisa aparecer
  no eixo — exija no briefing e confira no screenshot.
- **Semana parcial no fim cria queda falsa.** Corte a última semana incompleta das séries (os
  cards continuam com o total do período) e diga isso no rodapé de método.
- **Rótulo de período mente fácil:** "meses cheios" com o último mês cortado na data da coleta
  é falso — escreva "julho a setembro (setembro até dd/mm)".

## Build para um `.html` único

O componente é React; o entregável é um arquivo que abre no navegador sem servidor:
Vite + React + TS + Tailwind v4 (`@tailwindcss/vite`) + `vite-plugin-singlefile`, alias `@/`,
`npm run build` → copiar `app/dist/index.html` para o HTML final. Dados entram como JSON
agregado importado no build (`numeros.json`, gerado pelo script de cálculo; arredonde floats
lá) — nunca o dado bruto com PII. Nenhum número digitado à mão no código.

## Entrega por subagente e revisão

1. Principal escreve `SPEC.md` no projeto (seções, chave do JSON de cada número, regras de
   vocabulário, blocos `[PENDENTE]` como caixa tracejada sem conteúdo inventado) e delega com
   escopo travado: só `app/**` + o HTML final; proibido ler `dados-brutos-*/`.
2. Exija do filho: `npm test` + build, 0 scripts externos/Google Fonts no HTML, screenshot
   headless da página inteira, `innerText` sem `NaN`/`undefined`, valores-chave batendo com o
   JSON, e matar o Chrome headless que abriu.
3. Revise você mesmo: `cmp` do HTML com `dist/index.html`, grep de refs externas, e leia o
   screenshot **por recortes** (gráficos, tabela, rodapé) — a imagem inteira reduzida esconde
   rótulo cortado e sobreposição. Correções vão num 2º briefing com a lista numerada.
4. **O JSON importado vai inteiro para dentro do HTML**, não só o que é renderizado. Todo campo do
   `numeros.json` fica legível no código-fonte ("exibir código"). Mantenha no JSON só o que a
   página mostra; causa técnica de incidente, nomes de container e notas internas ficam no
   README. Confira com dois greps: no HTML bruto (vaza pelo bundle) e no texto renderizado
   (`google-chrome --headless=new --virtual-time-budget=5000 --dump-dom`, remova script/style e
   tags). Grep cru no HTML dá falso positivo com classes do Tailwind (`leading-*`, `container`)
   e com `NaN` dentro de palavras ("fu**ncionan**do") — o veredito é o texto renderizado,
   buscando `\bNaN\b`.

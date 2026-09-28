---
name: design-system-extraction
description: Use ao extrair design system de site ou app de referência. Gera design-system.html único que vira fonte obrigatória de UI para agentes.
---

# Extração de Design System

O problema que isto resolve: agente de IA gerando UI improvisa. Cada tela sai com botão diferente, espaçamento diferente, escala tipográfica diferente. Pedir "mantenha consistente" não funciona porque o modelo não tem referência do que é consistente — ele tem o treino dele, que muda a cada chamada.

A solução é um arquivo único, `design-system.html`, que demonstra cada componente com o HTML e o CSS reais de uma referência. Esse arquivo entra em todo prompt de UI como fonte obrigatória. O agente para de inventar porque tem de onde copiar.

**Quando usar:** projeto novo sem identidade visual, UI gerada por IA saindo inconsistente, ou quando você precisa de um padrão que sobreviva a troca de modelo.

**Quando não usar:** projeto que já tem design system em código (Tailwind config, tokens, biblioteca de componentes). Aí a fonte é o código existente, não uma extração.

---

## O que o arquivo contém

- **Tokens** — cores primárias e semânticas, escala tipográfica, spacing, border-radius, shadows
- **Componentes** — botões com variantes, inputs, cards, modais, tabs, alerts, badges, navbars, footers
- **Estados de interação** — hover, focus, active, disabled, error, loading, empty
- **Responsivo** — breakpoints, grid, comportamento mobile
- **Motion** — transições, keyframes, easings, com galeria demonstrando cada classe
- **Tema** — claro e escuro quando a referência tiver ambos

Tudo num HTML só. Não separe em CSS, JS e JSON: o agente precisa ler uma coisa, não caçar quatro.

---

## Pipeline

### 1. Escolher a referência

- **aura.build** — catálogo de design systems extraíveis
- **Produtos reais** — Stripe, Linear, Notion, Vercel, Supabase
- **Templates por tipo** — Duralux, Tailadmin para painel administrativo

A skill `popular-web-designs` tem 54 design systems reais já catalogados em HTML/CSS. Comece por ela: se o que você quer já está lá, pule a extração inteira.

### 2. Baixar

Extensão Website Downloader (Chrome), saveweb2zip.com, ou Ctrl+S no formato "HTML completo". Descompacte em `design_system/refs/<nome>/`.

Confira que o CSS veio junto. Site com Tailwind via CDN ou CSS-in-JS costuma vir sem os estilos computados — nesse caso a extração produz um arquivo vazio de estilo. Abra o `index.html` baixado no navegador antes de rodar o prompt: se abriu sem estilo, o download falhou.

### 3. Escolher o prompt

| Referência | Prompt |
|---|---|
| Landing page, institucional, página única | `references/prompt-sites.md` |
| CRM, dashboard, ERP, painel, app web complexo | `references/prompt-sistemas.md` |

Usar o de site numa referência de sistema perde tabela de dados, formulário denso, modal e estado semântico. O inverso gera seções vazias.

### 4. Rodar num modelo grande

Extração com modelo fraco produz token inconsistente e componente inventado, que é pior que não ter design system: você passa a confiar num arquivo errado. Use o modelo maior disponível.

### 5. Validar

Abra `design_system/design-system.html` no navegador:

- [ ] Cores batem com a referência (compare lado a lado, não de memória)
- [ ] Tipografia tem escala visível, não três tamanhos aleatórios
- [ ] Botões têm variantes e todos os estados
- [ ] Hover, focus e disabled realmente reagem
- [ ] Modal e formulário desenhados (sistemas)
- [ ] Tabela e card de dados presentes (sistemas)
- [ ] Breakpoint mobile funcionando
- [ ] Nenhum componente que não existe no original

Faltou algo: peça refinamento específico da seção, não regeneração do arquivo.

---

## Usar no fluxo

Todo prompt de UI referencia o design system e proíbe invenção:

```
Analise @PRD.md e @design_system/design-system.html. Implemente a tela
de [FUNCIONALIDADE] seguindo o padrão visual e os componentes definidos
no design system. Não invente componentes novos.
```

A palavra que carrega a instrução é **"não invente"**. Sem a proibição explícita o modelo improvisa, porque improvisar é o comportamento padrão dele quando o componente pedido não está claro na referência.

---

## Anti-padrões

| Anti-padrão | Consequência |
|---|---|
| Extrair com modelo fraco | Token inconsistente, componente inventado, arquivo em que você não pode confiar |
| Manter o DS em arquivos separados (CSS, JS, JSON) | Agente lê um e ignora os outros |
| Prompt de site em referência de sistema | Perde tabela, formulário denso, modal, estado semântico |
| Deixar cada feature "melhorar" o DS | Vira anarquia em três sprints |
| Atualizar o DS sem atualizar a referência no PRD | Agente segue o PRD antigo |
| Regenerar o DS por mudança cosmética | Perde ajuste manual acumulado; edite o arquivo direto |
| Não validar no navegador | Arquivo bonito no código e quebrado na renderização |

---

## Quando regenerar

Só quando mudou a identidade visual da marca, entrou nova família tipográfica ou trocou a paleta principal. Mudança pequena se edita direto no arquivo — regenerar joga fora todo refinamento manual que você fez desde a última extração.

---

## Relacionadas

- `popular-web-designs` — 54 design systems reais já catalogados; checar antes de extrair
- `impeccable` — crítica de design, depois que o DS existe
- `claude-design` — artefato HTML one-off
- `prompt-engineering-agentes` — a estrutura XML mandatória que os prompts desta skill usam

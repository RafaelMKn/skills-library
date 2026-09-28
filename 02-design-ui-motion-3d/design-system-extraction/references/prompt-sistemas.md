# Prompt curado — Extração de Design System para SISTEMAS

Use quando a referência é aplicação web complexa: CRM, dashboard, ERP, painel administrativo. Cobre Application Shell, navegação multinível, formulários densos, tabelas de dados, modais, estados semânticos e temas claro/escuro.

Substitua `[NOME_DA_REFERENCIA]` pelo diretório real em `design_system/refs/`.

```xml
<system>
Você é um especialista em construção de Design Systems e Pattern Libraries para aplicações web complexas (CRMs, Dashboards, ERPs, painéis administrativos).
Sua função é analisar o HTML, CSS e JS de uma aplicação web de referência e gerar um arquivo único que documenta todo o sistema de design utilizado, preservando fielmente o visual, comportamento e padrões de interface originais.
</system>

<context>
Você receberá o HTML, CSS e JS completos de uma aplicação web de referência como entrada.
A partir dele, deve criar um único arquivo chamado `design-system.html`, salvo na pasta @design_system.
Este arquivo funciona como uma biblioteca viva de padrões: ele documenta e demonstra cada elemento de interface da aplicação original com exemplos reais, interativos e navegáveis.

Diferente de sites institucionais ou landing pages, aplicações web possuem padrões complexos de interface: formulários densos, tabelas de dados, navegação multinível, estados de sistema, modais, feedback ao usuário e layouts compostos (sidebar + header + área de conteúdo). O design system extraído deve refletir essa complexidade.
</context>

<input>
@design_system/refs/[NOME_DA_REFERENCIA]/index.html
</input>

<objective>
Gerar um arquivo `@design_system/design-system.html` que preserve exatamente o visual e comportamento do design original da aplicação, reutilizando o HTML, classes CSS, animações, keyframes, transições, efeitos e padrões de layout — sem aproximações ou recriações.
</objective>

<hard_rules>
REGRAS INVIOLÁVEIS — siga todas sem exceção:

1. NÃO redesenhe nem invente estilos novos.
2. Reutilize exatamente os mesmos nomes de classes, animações, timings, easings e estados (hover, focus, active, disabled, loading, empty, error).
3. Referencie os mesmos arquivos CSS/JS usados pela aplicação original.
4. Se um estilo, componente ou padrão NÃO existe na aplicação de referência, NÃO o inclua.
5. O arquivo deve ser autodocumentado pela sua própria estrutura (cada seção = documentação).
6. Inclua uma navegação horizontal fixa no topo com âncoras para cada seção.
7. NENHUM estilo inline. Tipografia, cores, espaçamentos e gradientes DEVEM vir do CSS original.
8. Para componentes com múltiplos estados (ex: botão default/hover/disabled, input default/focus/error), documente TODOS os estados presentes no original, lado a lado.
9. Se a aplicação possui tema claro e escuro, documente ambos os temas.
</hard_rules>

<sections>
Organize o arquivo nas seguintes seções, nesta ordem:

<section id="0" name="Application Shell (Clone Exato)">
A primeira seção DEVE ser um clone direto do layout principal (shell) da aplicação:
- Sidebar/menu lateral (se existir)
- Header/topbar da aplicação
- Área de conteúdo principal
- Mesma estrutura HTML, classes CSS, disposição e proporções

ÚNICA alteração permitida:
- Substitua textos de conteúdo para apresentar o Design System (ex: título da página, breadcrumb)
- Mantenha a hierarquia e comprimento de texto similares ao original

PROIBIDO: alterar layout, espaçamento, alinhamento, proporções sidebar/conteúdo, ou adicionar/remover elementos estruturais.

Se a aplicação NÃO possui shell (ex: é uma tela de login isolada), clone a tela principal como referência.
</section>

<section id="1" name="Tipografia">
Renderize como uma tabela de especificações ou lista vertical.

Cada linha DEVE conter:
- Nome do estilo (ex: "Page Title", "Section Heading", "Table Header", "Body Text", "Caption")
- Preview ao vivo usando o elemento HTML e classes CSS originais exatos
- Tamanho/altura de linha alinhado à direita (formato: 16px / 24px)

Inclua APENAS estilos que existam na aplicação de referência, nesta ordem de prioridade:
Page Title → Section Heading → Card Title → Subtitle → Table Header → Body Text → Body Text Small → Label → Caption / Helper Text → Monospace (se usado em dados, código ou valores)

Regras adicionais:
- Se um estilo usa truncamento (text-overflow: ellipsis), demonstre o comportamento
- Se a aplicação usa fontes monospace para dados numéricos ou código, inclua como categoria separada
- Se um estilo não existe no original, NÃO o inclua
</section>

<section id="2" name="Cores, Superfícies e Estados Semânticos">
Documente dividindo em subseções:

2.1 — Cores de Interface
- Background principal da aplicação
- Background da sidebar/menu
- Background do header
- Background de cards e painéis
- Background de tabelas (linhas alternadas, se existir)

2.2 — Cores Semânticas de Estado
- Success / Sucesso (verde — aprovado, concluído, ativo)
- Warning / Alerta (amarelo/laranja — pendente, atenção)
- Error / Erro (vermelho — rejeitado, falha, obrigatório)
- Info / Informação (azul — informativo, neutro)
- Neutral / Desabilitado (cinza — inativo, desabilitado)

Para cada cor semântica, mostre como é aplicada no original:
- Badge/tag de status
- Mensagem de feedback (toast, alert, inline)
- Borda ou highlight de campo

2.3 — Superfícies e Efeitos
- Bordas e divisores (espessura, cor, estilo)
- Sombras (card shadow, dropdown shadow, modal shadow)
- Overlays (modal backdrop, se existir)
- Glass/blur (se existir)
- Gradientes (se existirem)
</section>

<section id="3" name="Navegação e Estrutura">
Documente APENAS padrões que existam na aplicação original:

3.1 — Menu / Sidebar
- Estado collapsed e expanded (se aplicável)
- Item de menu: default / hover / active (página atual)
- Submenus / agrupamentos (se existirem)
- Ícones de menu (se presentes)

3.2 — Header / Topbar
- Elementos presentes: logo, busca, notificações, avatar/perfil, etc.
- Comportamento e estados de cada elemento

3.3 — Breadcrumbs (se existirem)
3.4 — Tabs / Abas (se existirem) — estados: default / hover / active / disabled
3.5 — Paginação (se existir) — estados: default / hover / active / disabled / first-last

Se algum subitem NÃO existe na aplicação, omita-o.
</section>

<section id="4" name="Componentes de Formulário">
Seção CRÍTICA para aplicações web. Documente APENAS componentes que existam no original.

4.1 — Inputs de Texto: Default / Focus / Filled / Error / Disabled / Read-only
4.2 — Select / Dropdown: estado fechado e aberto
4.3 — Checkbox e Radio: unchecked / checked / indeterminate / disabled
4.4 — Toggle / Switch: off / on / disabled
4.5 — Textarea: estados análogos ao input
4.6 — Date Picker / File Upload / outros (se existirem)

4.7 — Composição de Formulário
- Mostre 1 exemplo de formulário completo extraído do original (cadastro, filtros, edição)
- Preservando grid, alinhamento de labels, espaçamento entre campos e posição dos botões
</section>

<section id="5" name="Tabelas e Exibição de Dados">
Documente APENAS se tabelas ou listas de dados existem na aplicação.

5.1 — Tabela de Dados
- Header da tabela (com ordenação, se existir)
- Linha padrão e linha alternada (zebra striping, se existir)
- Linha hover, linha selecionada
- Célula com ações (botões, ícones de editar/excluir)
- Célula com badge/status
- Tabela vazia / empty state

5.2 — Cards de Dados (se a aplicação usa cards em vez de tabela, ou ambos)
5.3 — Métricas / KPIs (se existirem)
5.4 — Gráficos (se existirem) — documente apenas o container e identifique a biblioteca usada

Se a aplicação não possui tabelas ou dados tabulares, OMITA esta seção.
</section>

<section id="6" name="Componentes de UI">
Documente APENAS componentes que existam no original e que NÃO foram cobertos nas seções anteriores.

6.1 — Botões: variantes (primary / secondary / outline / ghost / danger), estados, tamanhos, com ícone
6.2 — Badges / Tags / Status Pills
6.3 — Modais / Dialogs (padrão, confirmação destrutiva, overlay)
6.4 — Toast / Notifications / Alerts (success / error / warning / info)
6.5 — Tooltips e Popovers
6.6 — Dropdown Menu / Context Menu
6.7 — Avatar / User Badge
6.8 — Loading / Skeleton

Se um subitem NÃO existe na aplicação, omita-o.
</section>

<section id="7" name="Layout e Espaçamento">
- Estrutura do shell: proporções sidebar / conteúdo / margens
- Container principal e largura máxima
- Grid de cards / métricas (colunas e gaps)
- Espaçamento entre seções da página
- Padrão de formulário (grid de campos, alinhamento de labels)
- Responsividade: breakpoints e mudanças de layout

Mostre 2 a 3 padrões reais de layout extraídos do original:
- Layout de listagem (tabela + filtros + ações de topo)
- Layout de formulário / edição
- Layout de dashboard (se existir)
</section>

<section id="8" name="Motion e Interação">
Documente todos os comportamentos de movimento presentes:
- Transições de sidebar (expand/collapse)
- Animações de abertura de modal e dropdown
- Transições de hover em botões, linhas de tabela, cards
- Animações de entrada de toast/notificação
- Loading/spinner animations
- Transições de página ou aba (se existirem)

Inclua uma "Galeria de Motion" demonstrando cada classe de animação em ação.

Se a aplicação NÃO possui animações, OMITA esta seção.
</section>

<section id="9" name="Ícones">
SE a aplicação utiliza ícones:
- Identifique o sistema/biblioteca de ícones (Lucide, Heroicons, FontAwesome, Material, SVG custom, etc.)
- Exiba todos os ícones utilizados, organizados por contexto (navegação, ações, status, dados)
- Mostre variantes de tamanho e herança de cor
- Use a mesma marcação e classes do original

SE ícones NÃO estão presentes, OMITA esta seção inteiramente.
</section>
</sections>

<output_format>
- Um único arquivo: `design-system.html`
- Salvo na pasta @design_system
- Autocontido e navegável, com nav fixa no topo
- Todas as referências CSS/JS apontando para os mesmos assets do original
- Cada seção com ID para navegação por âncoras
</output_format>
```

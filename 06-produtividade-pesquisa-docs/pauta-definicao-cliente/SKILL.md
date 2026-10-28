---
name: pauta-definicao-cliente
description: Monta pauta de reunião para destravar decisão de cliente.
version: 1.0.0
author: <autor>
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Clientes, Reuniao, Escopo, PT-BR]
    category: <categoria>
    related_skills: [agent-creator-hub, n8n-flow-builder, prompt-engineering-agentes]
---

# Pauta de definição com cliente

Use quando o que trava a construção não é técnica e sim **decisão de negócio** — o que a IA deve
perguntar, para quem vai o lead, qual produto ela oferece, qual o processo comercial. A entrega
desta sessão **não é código, é a pauta**: o fluxo desenhado até o ponto indefinido e a lista de
perguntas que o dono da decisão precisa responder.

Gatilhos: "precisamos desenhar com o/a `<pessoa>` o fluxo", "achar algumas perguntas", "levantar o
que perguntar pra ele/ela", "montar a pauta da reunião", "salvar essa demanda", "quero fazer uma
apresentação pra mostrar pro <pessoa>".

**Também vale para reunião interna** (sócio da <empresa>, por exemplo <pessoa>). Aí não existe pasta de
cliente: os arquivos vão em `<workspace>/operacao/reunioes/<AAAA-MM-DD>-<pessoa>/` (`pauta.md` +
`apresentacao.html`). Pessoa que não aparece no repo pode ser sócio ou parceiro, não só cliente. Antes
de perguntar quem ela é, consulte o histórico com `session_search`.

Escreva tudo em **PT-BR**. Layout do workspace, instâncias e regras de cliente: `agent-creator-hub`.

## Antes de escrever qualquer pergunta

1. **Feche as lacunas do enunciado com o usuário, uma pergunta de cada vez.** O pedido inicial quase
   nunca diz qual sistema, quem decide o quê e quando é a sessão. Pergunte o que falta e **registre
   a lacuna no arquivo em vez de preencher com estimativa** — pauta com premissa inventada queima a
   reunião inteira.
2. **Se a resposta não bater com nenhuma opção que você ofereceu, pare e releia o pedido.**
   "Não entendi a pergunta" quase sempre significa que você enquadrou o problema errado, não que ele
   não sabe a resposta. Reenquadre a partir da explicação dele, não insista na sua taxonomia.
3. **Levante o que já existe antes de perguntar.** `README.md` do projeto, `docs/` do cliente, a
   versão em vigor do prompt, o inventário do fluxo. Pergunta cuja resposta já está escrita no repo
   queima tempo de reunião e credibilidade.
4. **Consulte também os sistemas do cliente, não só o repo.** Havendo token no `.env` do cliente
   (CRM, ClickUp, planilha), a modelagem real está lá: estágios de pipeline, campos, status
   existentes. Metade das perguntas de "como vocês fazem X?" já tem resposta observável por API — e
   a resposta observada costuma **contradizer** a decisão que o usuário acabou de tomar no chat, o
   que é exatamente o conflito que a pauta existe para levantar.
5. **Pedido ditado por voz: termo incompreensível nunca é descartado.** A transcrição troca palavras
   ("viantigo", "week word" = wake word). Mantenha cada termo que você não entendeu numa lista de
   abertos e pergunte por ele de forma explícita, citando a palavra transcrita, até que seja resolvido.
   Antes de perguntar, procure no repo e no `session_search`. Seguir em frente calado sobre uma parte
   do pedido é tratado como ignorar essa parte.
6. **Os assuntos chegam aos poucos.** Quando o usuário diz "vou te falando o que tenho que falar",
   monte só o esqueleto (capa, pauta e fechamento) e vá acumulando cada assunto que ele mandar no
   `pauta.md`. Os slides de conteúdo só são montados quando ele disser que acabou. Mensagem dele no
   meio da coleta que pede outra coisa (por exemplo, ajustar config) é executada na hora, e depois a
   coleta continua.
7. **Resposta do usuário que devolve pergunta é tarefa, não impasse.** "Pode aplicar — me diga como
   você acessa" significa vá descobrir o acesso e volte com opções avaliadas, não repita a pergunta
   com outras palavras. Verifique o que você de fato tem (chaves no `.env`, binários instalados,
   endpoints que respondem) e apresente os caminhos com a recomendação e o custo de cada um.

## Estrutura da pauta

Arquivo em `clientes/<cliente>/projetos/<projeto>/docs/pauta-<pessoa>-<tema>-<AAAA-MM-DD>.md`:

1. **Cabeçalho** — cliente, projeto, data da sessão, **quem decide o quê**, quem leva.
2. **O que muda em relação ao que está construído** — em duas frases, o que o sistema faz hoje e o
   que a demanda acrescenta. É isso que impede a reunião de redesenhar o que já funciona.
3. **O conflito, se houver** (ver seção abaixo).
4. **Desenho do fluxo** em bloco de texto, com cada etapa marcada `[pronto]`, `[parcial]` ou
   `◀── NOVO`. O ponto de ramificação novo fica visualmente óbvio — é o único assunto da reunião.
5. **As perguntas, numeradas e agrupadas em blocos temáticos.** Bloco solto vira conversa solta.
   Blocos que costumam existir: os produtos/opções em jogo · os sinais que separam um do outro ·
   quanto a IA decide sozinha · o que muda depois da decisão · descarte e follow-up · processo
   comercial em volta (CRM, pipeline, dono do roteiro, critério de acerto).
6. **Tabela "o que eu preciso sair da reunião com"** — saída × o que ela destrava. É o critério de
   pronto da sessão.
7. **Fontes** — caminhos dos arquivos que sustentam cada afirmação da pauta.

## Cruze com as decisões já fechadas — e ponha o conflito como pergunta nº 1

Antes de montar os blocos, releia as decisões anteriores registradas em `docs/` (as fechadas com
outro stakeholder, em outra reunião). **Demanda nova que contradiz decisão fechada não é detalhe:
é a primeira pergunta da pauta**, porque metade das outras muda de resposta conforme ela. Enuncie a
decisão antiga literal, a nova demanda, e as saídas possíveis (a antiga cai · a nova fica restrita ·
as duas convivem com escopo separado).

## As perguntas precisam respeitar a arquitetura

Pergunta que promete comportamento que o fluxo não consegue entregar produz decisão inútil. Antes
de escrever o bloco de perguntas, confira as restrições já provadas do fluxo e enuncie-as na pauta:

- **Modelo pequeno (`gpt-4o-mini`) não chama tool silenciosa** — sem efeito visível na resposta, ela
  sempre perde para a tool que o modelo precisa para responder. Registro, bookkeeping e
  classificação **saem das tools do agente e viram passo determinístico depois dele**. Não adianta
  reforçar no prompt; a solução é arquitetura. Portanto a pauta pergunta *o que a IA apura*, nunca
  *o que a IA grava*.
- **Identificador do lead nunca vem por `$fromAI`** — telefone e afins são plumbados do webhook, ou
  o modelo inventa.

## Quando a pauta vira artefato visual

O padrão é `.md`. Mas quando o usuário vai **apresentar numa reunião** ou **circular para um
decisor**, o entregável muda de formato — e são dois formatos diferentes, não um só:

| Formato | Quando | Forma |
|---|---|---|
| **Deck** | vai ser projetado/conduzido na reunião | **HTML em slides de tela cheia**, um assunto por slide: `<section class="slide">` com só um visível por vez, navegação por setas/clique, tecla `f` para tela cheia, contador e barra de progresso. Fundo escuro na capa e em cada virada de tema. Nada de página com rolagem. Ponto de partida: `templates/deck-slides.html` |
| **Registro de decisão** | vai ser marcado durante a reunião e virar ata depois | **uma página A4**, grade de cards, cada ponto com opções e caixa de marcar |
| **Mapa de status** | "o que temos e o que falta", projeto que saiu do escopo, prestação de contas | **página standalone para o navegador** (fundo e fontes próprios, não widget com as variáveis do tema do chat): placar de 3 números → trilho do caminho ponta a ponta com estado por passo → inventário por sistema → tabela de referências clicáveis. Receita: `references/artefato-visual-reuniao.md` |

**"Cria um artefato" depois de um deck pede formato novo, não o deck encolhido.** Registro de
decisão que é só o deck espremido perde a função: o que o torna útil é a caixa de marcar ao lado de
cada opção, que faz a mesma folha servir de pauta na mesa e de ata no grupo depois.

Regras que valem para qualquer peça que sai do repositório:

- **Marca só se a peça é da <empresa>.** Peça da <empresa>: leia os tokens em
  `<workspace>/<projeto-de-marca>/identidade-visual.md` antes de escolher cor ou fonte (nunca
  invente cor: um acento por peça, fundo creme, não branco puro). Projeto de parceiro (ex.: <cliente>) é
  neutro: sem marca nem nome <empresa>.
- **Linguagem de negócio, não jargão.** Nome de nó, nome de credencial e ID cru ficam na spec técnica.
  Na peça: "campos de controle", "rotina", "o CRM". Exceção: quando o pedido é justamente o
  inventário (quais fluxos, quais tabelas), o nome fica, com uma frase em linguagem leiga ao lado, e
  o ID vai escondido no link, não no texto.
- **Antes de montar, reconcilie os documentos do projeto.** Se uma decisão mais nova contradiz uma
  spec, um passo a passo ou um ADR, a peça segue a mais nova, e o documento velho aparece marcado como
  desatualizado nas referências e na resposta do chat. Senão, o leitor sai da reunião com o artefato
  errado na mão.
- **Nenhum dado de produção numa peça que circula** — telefone de cliente, JID de grupo, ID de
  instância. A peça vai para grupo de WhatsApp e sobrevive à reunião.
- **Quantifique a lacuna no cabeçalho.** Três números que enquadram a decisão (quantas rotinas
  olham o problema hoje, quantos estágios já existem, quantas execuções reais) valem mais que um
  parágrafo de contexto.
- **Marque o que foi deduzido.** Item cuja resposta você inferiu de arquivo ou de nó — sem ter
  observado — entra na peça com essa palavra. É o que impede a reunião de terminar com todos
  achando que já foi verificado.

**Gate antes de entregar: renderize e olhe.** HTML não conferido não é entregável — quebra de
linha em rótulo, card desalinhado e corte de página só aparecem renderizados. Receita de render,
verificação por visão e o ajuste de uma página A4: **`references/artefato-visual-reuniao.md`**.

## Fechamento da sessão

- Crie/atualize `tarefas/<AAAA-MM-DD>-<slug>.md` com `estado: fazendo`, o escopo já confirmado, o
  caminho da pauta, o estado técnico (IDs, instância, ativo/inativo, como editar) e o "depois da
  sessão" numerado.
- No chat, entregue **os caminhos dos dois arquivos e no máximo três pontos**: o conflito, a
  restrição de arquitetura que limita o desenho, e a pergunta de maior alavancagem da pauta (a que,
  respondida, faz o resto encaixar). O conteúdo está no arquivo — não o repita na resposta.
- Prompt novo é **arquivo novo** (`prompt-<agente>-v<N+1>.md`), nunca sobrescrita da versão em vigor.

## Verification

- Toda pergunta da pauta tem resposta que **muda** o que vai ser construído. Se a resposta não muda
  nada, corte a pergunta.
- Nenhuma pergunta tem resposta já escrita no `docs/` ou no `README.md` do projeto.
- O arquivo de tarefa aponta para o arquivo de pauta e vice-versa.
- Peça visual: renderizada e conferida em fatias legíveis antes de entregar; registro de decisão
  fecha em **uma** página, confirmado pela contagem do PDF e não por estimativa de altura.
- Peça visual: nenhum telefone, JID, ID de instância ou nome de nó no corpo.
- Peça com links: todo caminho relativo testado com `[ -e ]`, e a peça diz quais links pedem login e
  quais só abrem na máquina local.

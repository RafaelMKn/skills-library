# Contrato de Entregáveis — Motion Editorial

Utilize esta referência para padronizar os artefatos de cada peça produzida pelo pipeline.

## Estrutura de Pastas da Peça

Após a aprovação de uma ideia no Board, organize os arquivos na seguinte estrutura:

```text
projetos/motion/exemplos/<slug>/
├── README.md              # Status do pipeline e registro de decisões
├── pesquisa.md            # Referências e benchmarks
├── roteiro-e-voz.md       # Roteiro, texto de tela e direção de locução
├── storyboard.md          # Storyboard estruturado
├── takes.html             # Artboards dos takes em HTML/CSS
├── takes/                 # Snapshots PNG dos takes
│   ├── 01-<slug-take>.png
│   └── ...
├── locucao.mp3            # Áudio final
├── timings-locucao.json   # Marcadores de tempo por beat
├── motion-spec.md         # Especificação de animação
└── motion/                # Projeto Remotion (quando rota de código)
```

## Registro de Estado no README

O `README.md` de cada peça deve registrar o progresso de cada etapa:

| Etapa | Estados | Evidência |
|---|---|---|
| Pesquisa & Nicho | pendente, concluída | `pesquisa.md` |
| Ideia | aguardando-aprovacao, aprovada | Nome da ideia e decisão registrada |
| Roteiro e Voz | aguardando-aprovacao, aprovado | `roteiro-e-voz.md` |
| Áudio / Locução | aguardando-asset, recebido, dispensado | `locucao.mp3` e duração |
| Takes Visuais | em-producao, aprovados | `storyboard.md`, `takes.html` |
| Rota Final | prompt-spec, remotion | Rota escolhida |
| Motion Final | especificado, renderizado | `motion-spec.md` ou arquivo MP4 |

## Padrões de Roteiro e Locução (`roteiro-e-voz.md`)
1. **Objetivo & Público:** Resumo em 2 linhas.
2. **Roteiro Falado:** Texto contínuo com contagem de palavras e estimativa de tempo (~2.5 palavras/segundo).
3. **Tabela de Beats:** Beat # | Tempo estimado | Fala | Texto na tela | Intenção visual.
4. **Direção de Voz:** Emoção, ritmo, pausas (`...`), entonação.
5. **Bloco de Locução Puro:** Somente o texto da locução, limpo de anotações.

## Padrões de Takes Visuais
* Dimensões: 1080 x 1920 (9:16 vertical).
* Margens de segurança: 120px no topo e 240px na base (para não conflitar com UI do Instagram/TikTok).
* Foco: Uma única ideia/hierarquia focal por take.

## Especificação de Motion (`motion-spec.md`)
* Inventário de assets e fontes utilizadas;
* Timeline com início e fim em milissegundos derivados da locução;
* Curvas de easing recomendadas (ex.: `cubic-bezier(0.16, 1, 0.3, 1)`);
* Instruções de transição entre takes;
* Checklist de conferência técnica (resolução, fps, taxa de bits, sincronia).

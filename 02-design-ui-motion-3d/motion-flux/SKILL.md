---
name: motion-flux
description: Conduz o pipeline editorial de vídeos em motion (Reels, Shorts, TikTok e anúncios verticais) — da pesquisa de referências, alinhamento de nicho e aprovação da ideia até roteiro, voz, takes e produção com Remotion ou prompt de motion. Na primeira execução, coleta o nicho e empresas de referência para gerar ideias altamente contextualizadas.
---

# Motion Editorial & Pipeline de Vídeos

Skill para conduzir a produção editorial de vídeos em motion e peças verticais de alta conversão, passo a passo, através de portões de aprovação (*gates*).

---

## 🎯 1. Primeira Execução: Onboarding de Nicho & Referências

Quando esta skill for iniciada pela primeira vez em um projeto ou quando não houver referências prévias configuradas:

1. **Pergunte ao Usuário:**
   * **Nicho / Segmento:** Qual é o nicho do negócio/projeto? (ex.: SaaS, automação de processos, marketing digital, e-commerce, finanças, etc.).
   * **Empresas / Criadores de Referência:** Quais marcas, perfis ou empresas servem de referência visual e de conteúdo? (ex.: Linear, Stripe, Vercel, criadores específicos).
   * **Público-Alvo e Dores Centrais:** Quem é o público que assistirá ao vídeo e qual problema central estamos resolvendo?
   * **Tom de Voz e Estilo Visual:** Formal, dinâmico, minimalista, dark mode, cores principais.
2. **Auto-Complementação:**
   * Salve essas diretrizes em `.motion-context.md` ou na documentação do projeto (`projetos/motion/README.md`) para que todas as ideações e roteiros seguintes utilizem esse direcionamento automaticamente.

---

## 🎬 2. Pipeline Editorial em 4 Gates

Conduza uma peça por vez. Cada gate exige aprovação explícita do usuário antes de avançar para a próxima etapa.

### Gate 1: Pesquisa & Board de Ideias
1. Se disponível, consulte referências de mercado e tendências dos últimos 30 dias com `last30days`.
2. Cruze as tendências com o nicho e as referências do usuário.
3. Apresente um **Board com 4 a 6 ideias** contendo:
   * **Título & Hook** (os primeiros 3 segundos);
   * **Tese** em uma frase;
   * **Público & Dor** abordada;
   * **Sequência de Beats** (5 a 6 batidas);
   * **Mecânica Visual Central** (ex: interface animada, kinetic typography, split screen, 3D spotlight);
   * **Esforço Estimado** (Baixo, Médio, Alto).
4. Indique uma ideia recomendada com justificativa. **Pare e aguarde a aprovação do usuário.**

### Gate 2: Roteiro & Pacote de Locução
Para a ideia aprovada, produza o arquivo `roteiro-e-voz.md`:
* Roteiro falado exato (duração estimada de 20 a 30s, ~50-70 palavras);
* Tabela por beat: fala exata, texto de tela (síntese) e intenção visual;
* Direção de voz para IA (ex.: ElevenLabs): tom, energia, ritmo, pausas e pronúncias;
* Bloco isolado de locução pronto para geração de áudio.
* **Pare e aguarde o arquivo de áudio ou a aprovação para prosseguir.**

### Gate 3: Takes & Storyboard Visual
Alinhe os beats à duração exata do áudio:
* Crie o storyboard dos takes (formato 1080 x 1920 para Reels/Shorts);
* Defina hierarquia visual única por take, área de respiro e paleta de cores da marca;
* Forneça os takes em HTML (`takes.html`) ou mockups visuais;
* Pergunte ao usuário a rota de entrega desejada:
  * **Rota A:** Especificação técnica detalhada (`motion-spec.md`) para montagem no After Effects/CapCut/Figma;
  * **Rota B:** Implementação e render programático com **Remotion** (`remotion-video`).
* **Pare e aguarde a escolha da rota.**

### Gate 4: Entrega Final
* **Se Rota A (Prompt/Spec):** Entregue o arquivo `motion-spec.md` completo com timeline por take, textos, transições, instruções de easing e checklist de QA.
* **Se Rota B (Remotion):** Crie a composição React em Remotion, renderize o trecho de teste e em seguida o MP4 final em 1080x1920 a 30fps.

---

## 📁 3. Estrutura de Arquivos por Peça

```text
projetos/motion/<slug-da-ideia>/
├── README.md              # Estado atual da peça e registro de gates
├── pesquisa.md            # Referências e sinais de pesquisa
├── roteiro-e-voz.md       # Roteiro, tabela de beats e prompt de locução
├── storyboard.md          # Descrição visual dos takes
├── takes.html             # Artboard dos takes editáveis
├── locucao.mp3            # Áudio da locução (quando gerado)
├── motion-spec.md         # Especificação detalhada de animação
└── motion/                # Código da composição Remotion (quando aplicável)
```

Consulte [references/contrato-de-entregaveis.md](references/contrato-de-entregaveis.md) para detalhes de cada artefato.

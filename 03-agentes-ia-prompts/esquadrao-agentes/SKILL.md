---
name: esquadrao-agentes
description: "Briefings e contratos de subagentes para equipes multiagente autônomas."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagents, archetypes, briefings, multiagent]
    related_skills: [doit, auditoria-trabalho-de-agente, create-subagent]
---

# Esquadrão de Agentes — Briefings e Contratos de Delegação

Catálogo de arquétipos especializados de subagentes, contratos operacionais de execução e matriz de roteamento para orquestração de equipes multiagente autônomas via `delegate_task`.

## When to Use

- O agente principal precisa delegar tarefas em paralelo ou isoladas para subagentes.
- Necessidade de estruturar briefings claros, reprodutíveis e protegidos contra auto-relato enganoso.
- Definição de papéis em fluxos orquestrados (ex.: `/doit`, pipelines de refatoração, triagem de bugs).

## Regras Universais para Todo Subagente

1. **Auto-relato não é fato:** Relatos de "funcionou", "arquivo criado" ou "testes passaram" são alegações não verificadas até que o orquestrador comprove diretamente no disco, no log de execução ou no diff Git.
2. **Alça verificável obrigatória:** Todo subagente deve devolver no resultado alças concretas de auditoria (caminho absoluto do arquivo, `arquivo:linha`, SHA do commit ou saída de terminal).
3. **Isolamento estrito:** Subagentes trabalham exclusivamente no diretório atribuído (worktree ou diretório específico). NUNCA devem alterar arquivos fora do seu escopo.
4. **Sem ações externas não autorizadas:** Subagentes não executam `git push`, não abrem Pull Requests, não chamam endpoints destrutivos de APIs e não fazem deploy por iniciativa própria.
5. **`output_schema` conciso:** Exija no JSON schema apenas os campos essenciais para o orquestrador tomar a próxima decisão (status, commit, caminhos, problemas).

## Matriz de Roteamento de Modelos

| Tipo de Tarefa | Complexidade | Perfil de Modelo Recomendado | Exemplos |
|---|---|---|---|
| **Criação / Arquitetura** | Alta | Raciocínio profundo, alta precisão de código | Claude Sonnet, Claude Opus, GPT-4o |
| **Correção cirúrgica** | Média | Modelo balanceado com contexto de código | Claude Sonnet, GPT-4o-mini |
| **Recon / Auditoria** | Média-Baixa | Rápido, econômico, bom leitor de contexto | Claude Haiku, Gemini Flash |
| **Pesquisa documental** | Baixa | Rápido, busca em lote | Claude Haiku, Gemini Flash |

## Arquétipos de Subagentes

### 1. `recon-auditor` (Auditoria e Inspeção Read-Only)
- **Objetivo:** Analisar a base de código, dependências, fluxos ou configurações sem alterar nada.
- **Comportamento:** Somente leitura. Toda afirmação deve vir acompanhada de `arquivo:linha` e citação textual exata.
- **Briefing Context:**
  ```
  Você é um auditor read-only. NÃO modifique nenhum arquivo.
  Sua missão: inspecionar <alvo> e responder com evidências auditáveis.
  Para cada problema ou ponto relevante, informe: arquivo, linha exata, trecho de código e impacto técnico.
  ```
- **Output Schema:**
  ```json
  {
    "type": "object",
    "properties": {
      "itens_auditados": {"type": "integer"},
      "achados": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "arquivo": {"type": "string"},
            "linha": {"type": "integer"},
            "gravidade": {"type": "string", "enum": ["critica", "aviso", "informativa"]},
            "descricao": {"type": "string"}
          },
          "required": ["arquivo", "linha", "descricao"]
        }
      }
    }
  }
  ```

### 2. `investigador` (Diagnóstico de Causa Raiz de Bugs)
- **Objetivo:** Reproduzir falhas, identificar o mecanismo exato do defeito e isolar a causa raiz antes de qualquer alteração de código.
- **Comportamento:** Cria primeiro uma sonda mínima ou teste de reprodução no scratch. Não propõe correção antes de confirmar a reprodução do erro.
- **Briefing Context:**
  ```
  Você é o investigador de defeitos. NÃO altere o código de produção ainda.
  Sua missão: isolar a causa raiz do bug reportado: <descrição do bug>.
  1. Crie um script de teste/sonda mínima em scratch para reproduzir o sintoma.
  2. Confirme a falha com exit code e log real.
  3. Isole o ponto de falha exato (arquivo:linha) e o mecanismo técnico da quebra.
  ```

### 3. `implementador` (Implementação Cirúrgica em Worktree)
- **Objetivo:** Escrever código, criar testes e gerar commit semântico em branch isolada.
- **Comportamento:** Respeita rigorosamente a lista de arquivos permitidos. Roda suíte de testes antes de considerar o trabalho feito.
- **Briefing Context:** Ver template completo em `05-dev-harness-cli/doit/templates/briefing.md`.

### 4. `revisor` (Peer Review Independente)
- **Objetivo:** Avaliar criticamente uma entrega contra a especificação original sem viés de autoria.
- **Comportamento:** Desconfiado. Testa caminhos de falha, verifica se edge cases foram cobertos e se há regressões.
- **Briefing Context:** Ver template completo em `05-dev-harness-cli/doit/templates/reviewer.md`.

### 5. `pesquisador` (Levantamento Técnico e APIs)
- **Objetivo:** Mapear documentação técnica, especificações de APIs REST/GraphQL, bibliotecas ou pacotes.
- **Comportamento:** Sintetiza endpoints, schemas de autenticação e payloads sem inventar parâmetros não documentados.
- **Briefing Context:**
  ```
  Você é um pesquisador técnico. Investigue a documentação oficial de <tecnologia/API>.
  Extraia: métodos suportados, formato de autenticação, payloads de exemplo e limitações/rate limits.
  Toda informação deve citar a URL oficial da documentação de onde foi extraída.
  ```

## Verification

- O briefing fornecido ao subagente contém escopo delimitado, restrições claras e alças verificáveis exigidas.
- O modelo escolhido corresponde à complexidade da tarefa na matriz de roteamento.
- O orquestrador confirma no disco os artefatos declarados pelo subagente.

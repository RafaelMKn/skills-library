# Matriz de Homologação em Runtime Real

Guia de validação para integrações complexas (APIs, bancos de dados, serviços externos e filas).

## Princípios de Verificação

1. **Auto-relato não é fato:** Um teste só é considerado válido quando acompanhado do comando executado, código de retorno (exit code) e saída real observada.
2. **Isolamento de ambiente:** NUNCA execute testes destrutivos contra bancos ou APIs de produção. Utilize mocks explícitos, containers efêmeros locais ou ambientes dedicados de sandbox/homologação.
3. **Sanitização de dados de teste:** Certifique-se de que nenhum dado confidencial, credencial real ou PII (dados pessoais identificáveis) seja utilizado em fixtures ou gravado em logs.

## Níveis de Evidência Exigidos

| Nível | Tipo | Como Obter | Requisito para Aprovação |
|---|---|---|---|
| L1 | Estático | Linters, typecheck, verificação de sintaxe | Exit code 0, 0 erros ou avisos bloqueantes |
| L2 | Unitário | Test runner com suites de mocks | 100% de testes passando nas funções alteradas |
| L3 | Integração | Subida de serviços em container / banco local | Fluxo de ponta a ponta exercitado e verificado |
| L4 | E2E / Contrato | Chamadas autenticadas contra APIs de teste | Payload de resposta validado com schema esperado |

## Checklist de Verificação Antes da Integração

- [ ] Diff limpo contendo apenas alterações pertinentes ao escopo.
- [ ] Nenhum arquivo temporário, `.env`, `.log` ou credencial commitada.
- [ ] Testes unitários cobrindo caminhos felizes e caminhos de erro adicionados/atualizados.
- [ ] Build e testes locais executados e passando com sucesso.
- [ ] Mensagens de commit semânticas e claras.

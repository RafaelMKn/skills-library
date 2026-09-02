---
name: make-manager
description: Use esta skill para consultar, criar, editar, ativar, desativar, executar, exportar blueprint ou investigar logs de cenários no Make pela API v2. Use quando o usuário mencionar Make, Integromat, cenário, blueprint, organização, equipe ou execução no Make.
---

# Make Manager

Use a API v2 oficial do Make pelo script `skills/make-manager/scripts/make_api.py`. A conta é selecionada explicitamente por `--account` (ex.: `--account PROD` ou `--account MINHA_CONTA`).

## Configuração e segurança

- As credenciais locais ficam exclusivamente em `.env`: `MAKE_<CONTA>_API_TOKEN` e `MAKE_<CONTA>_API_URL`. Nunca imprima, versione ou inclua o token em payloads, prompts ou cenários.
- A URL precisa incluir `/api/v2`, por exemplo `https://us1.make.com/api/v2`. A zona é parte da conta: descubra-a uma vez com `detect-zone` e grave o resultado no `.env`.
- O token precisa ter os escopos mínimos da ação. Para inventário: `organizations:read`, `teams:read` e `scenarios:read`; para alterar cenários: `scenarios:write`; e, para execução manual, `scenarios:run` também.
- O cenário vivo no Make é a fonte de verdade. Antes de editar, consulte o cenário e o blueprint atuais. Só grave exportações datadas de histórico dentro da pasta do projeto, nunca em `scratch/`. Não exporte nem versione segredos ou conexões.

## Primeira conexão

Com um token já configurado e sem URL de zona:

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> detect-zone
```

Se devolver uma URL, registre-a em `MAKE_<CONTA>_API_URL` no `.env`. Depois confirme apenas a autenticação, sem expor os dados do usuário:

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> probe
```

## Inventário

Comece pela hierarquia `organização → equipe → cenário`:

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> list-organizations
python skills/make-manager/scripts/make_api.py --account <CONTA> list-teams <ORGANIZATION_ID>
python skills/make-manager/scripts/make_api.py --account <CONTA> list-scenarios <TEAM_ID>
python skills/make-manager/scripts/make_api.py --account <CONTA> get-scenario <SCENARIO_ID>
python skills/make-manager/scripts/make_api.py --account <CONTA> get-blueprint <SCENARIO_ID>
python skills/make-manager/scripts/make_api.py --account <CONTA> audit-lead-error-handlers <TEAM_ID>
python skills/make-manager/scripts/make_api.py --account <CONTA> list-connections <TEAM_ID>
python skills/make-manager/scripts/make_api.py --account <CONTA> get-connection <CONNECTION_ID>
```

`list-connections` e `get-connection` projetam só campos não sensíveis (id, nome, rótulo, `uid`,
`expire`, escopos) — o segredo da conexão nunca é impresso. O `uid` é **app-scoped**: dentro de um
mesmo app, ids diferentes significam perfis diferentes; entre apps distintos, o mesmo perfil tem
ids diferentes. Serve para agrupar conexões por pessoa, nunca para identificá-la fora do Make.

**Pagine sempre.** Os endpoints de coleção (`/hooks`, `/scenarios`, `/connections`) devolvem só a
primeira página quando `pg[limit]` é omitido — 50 itens no `/hooks`. Uma leitura não paginada de
217 hooks devolveu 50 e inverteu a conclusão sobre qual conexão sustenta a produção.

Para depurar, use logs e o detalhe de uma execução:

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> list-logs <SCENARIO_ID> --limit 20
python skills/make-manager/scripts/make_api.py --account <CONTA> get-execution <SCENARIO_ID> <EXECUTION_ID>
```

## Alterações

1. Busque o cenário e seu blueprint ao vivo; confira equipe, agendamento e conexões afetadas.
2. Monte o payload JSON em `scratch/` e valide-o contra a documentação oficial ou um cenário equivalente. O Make exige uma estrutura de blueprint específica; não a invente de memória.
3. Peça confirmação explícita do usuário antes de criar, atualizar, iniciar, parar, executar ou apagar. Só então inclua `--confirm`.
4. Depois da mudança, busque o cenário novamente e confira `isActive`, `teamId`, nome e blueprint. Registre um snapshot datado seguro no projeto, se aplicável, e apague o payload temporário.

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> create-scenario scratch/cenario.json --confirm
python skills/make-manager/scripts/make_api.py --account <CONTA> update-scenario <SCENARIO_ID> scratch/alteracao.json --confirm
python skills/make-manager/scripts/make_api.py --account <CONTA> start-scenario <SCENARIO_ID> --confirm
python skills/make-manager/scripts/make_api.py --account <CONTA> stop-scenario <SCENARIO_ID> --confirm
python skills/make-manager/scripts/make_api.py --account <CONTA> run-scenario <SCENARIO_ID> scratch/entrada.json --confirm
python skills/make-manager/scripts/make_api.py --account <CONTA> delete-scenario <SCENARIO_ID> --confirm
```

Para cenários de captação Meta, `add-lead-error-handler` aplica somente no módulo HTTP escolhido a
rota de erro `e-mail → Ignore`: o lead que falhar é descartado e o próximo segue normalmente.
Faça primeiro a auditoria e use uma conexão SMTP já existente na equipe:

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> add-lead-error-handler <SCENARIO_ID> <HTTP_MODULE_ID> --recipient "seu-email" --email-connection <CONNECTION_ID> --confirm
```

Após aprovar o piloto, replique somente os casos pendentes encontrados pela auditoria. Sem
`--active-only`, a operação mantém também os cenários inativos prontos para uma ativação futura,
mas não os ativa:

```bash
python skills/make-manager/scripts/make_api.py --account <CONTA> add-lead-error-handlers <TEAM_ID> --recipient "seu-email" --email-connection <CONNECTION_ID> --confirm
```

`run-scenario` executa automações reais. Não o use para testar sem confirmação específica sobre os efeitos externos.

## Referências oficiais

- [Estrutura e zona da API](https://developers.make.com/api-documentation/getting-started/api-structure)
- [Autenticação por token](https://developers.make.com/api-documentation/authentication)
- [Cenários](https://developers.make.com/api-documentation/api-reference/scenarios)
- [Blueprints](https://developers.make.com/api-documentation/api-reference/scenarios-greater-than-blueprints)
- [Logs](https://developers.make.com/api-documentation/api-reference/scenarios-greater-than-logs)

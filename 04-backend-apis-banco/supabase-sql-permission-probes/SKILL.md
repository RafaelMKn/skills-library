---
name: supabase-sql-permission-probes
description: "Use when checking Supabase SQL permissions and ACLs."
---

# Supabase — comprovar permissões e compatibilidade de ACL

## Procedimento

- Diferencie a identidade da conexão da identidade selecionada pelo modo de execução. Em `SUPABASE_BETA_RUN_SQL_QUERY`, `read_only=true` pode executar como `supabase_read_only_user`, enquanto a mesma conexão com `read_only=false` pode executar como `postgres`. Não conclua que a conexão inteira é read-only pelo primeiro resultado.
- Comprove capacidade sem escrever: execute somente `SELECT current_user, session_user, has_schema_privilege(current_user, 'public', 'CREATE'), current_setting('transaction_read_only')` no modo correspondente. SELECT com `read_only=false` não autoriza DDL; autorização de produção continua necessária.
- Verifique a versão real do Postgres e compare com a dos testes. Container vanilla não comprova particularidades do Supabase.
- Trate `PUBLIC` como grantee especial de ACL, não como role literal garantida. Inspecione ACLs usando `aclexplode`, onde `grantee=0` representa PUBLIC. Não dependa de `has_function_privilege('public', ...)` sem comprovar que a role literal existe; não crie essa role artificialmente nos testes para fazer a verificação passar.
- Inspecione default ACL, RLS, EXECUTE das funções e exposição do schema no PostgREST antes de criar objetos. RLS não restringe roles com BYPASSRLS da mesma maneira que usuários comuns.
- Antes e depois de migração aditiva, registre contagens e fingerprints das tabelas legadas sem expor registros. Releia o alvo após aplicar; sucesso do endpoint não comprova preservação ou permissões.

## Testes de integração

- Exercite o retorno real das funções Postgres com a normalização e o mapeamento do adapter. Suítes independentes podem passar mesmo quando uma parte retorna `applied` e outra exige `committed`.
- Não confunda harness de Node com runtime n8n: credenciais, parâmetros, Code node, Respond to Webhook e HTTP precisam de homologação própria.
- Não declare cadastro disponível para a IA quando existe somente num schema privado. Verifique a ponte para as tabelas e a chave de sessão efetivamente lidas pelo agente.

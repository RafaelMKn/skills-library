# APIs, Backend & Banco de Dados

> Skills para desenvolvimento de APIs com Fastify, ORM com Prisma, segurança OAuth 2.0/2.1 e integrações com ClickUp.

Total de skills nesta categoria: **5**

| Skill | Descrição |
|---|---|
| **[`clickup-api`](clickup-api/SKILL.md)** | Chame a API REST v2 do ClickUp diretamente (fora do n8n) para consultar, criar ou atualizar workspaces, spaces, folders, lists, tasks, comentários e webhooks. Use quando o pedido envolver "buscar/criar/atualizar tarefa no ClickUp", "listar tasks/lists/spaces do ClickUp", "comentar em uma tarefa do ClickUp", "configurar webhook do ClickUp", ou mencionar CLICKUP_API_TOKEN, personal token `pk_...`, ou a API do ClickUp em geral fora do contexto de um fluxo n8n. Não é para configurar os nós nativos do ClickUp dentro de um workflow n8n — para isso use `n8n-workflow-patterns` / os nós ClickUp diretamente. |
| **[`fastify-best-practices`](fastify-best-practices/SKILL.md)** | Guides development of Fastify Node.js backend servers and REST APIs using TypeScript or JavaScript. Use when building, configuring, or debugging a Fastify application — including defining routes, implementing plugins, setting up JSON Schema validation, handling errors, optimising performance, managing authentication, configuring CORS and security headers, integrating databases, working with WebSockets, and deploying to production. Covers the full Fastify request lifecycle (hooks, serialization, logging with Pino) and TypeScript integration via strip types. Trigger terms: Fastify, Node.js server, REST API, API routes, backend framework, fastify.config, server.ts, app.ts. |
| **[`oauth`](oauth/SKILL.md)** | Implements OAuth 2.0/2.1 authorization flows in Fastify applications — configures authorization code with PKCE, client credentials, device flow, refresh token rotation, JWT validation, and token introspection/revocation endpoints. Use when setting up authentication, authorization, login flows, access tokens, API security, or securing Fastify routes with OAuth; also applies when troubleshooting token validation errors, mismatched redirect URIs, CSRF issues, scope problems, or RFC 6749/6750/7636/8252/8628 compliance questions. |
| **[`prisma-cli`](prisma-cli/SKILL.md)** | Prisma ORM CLI commands reference covering init, generate, migrate, db, dev, complete, studio, validate, format, debug, and mcp. Use for ORM/database CLI workflows, not the Prisma Platform CLI. Triggers on "prisma init", "prisma generate", "prisma migrate", "prisma db", "prisma complete", "prisma studio", "prisma mcp". |
| **[`prisma-client-api`](prisma-client-api/SKILL.md)** | Prisma Client API reference covering model queries, filters, operators, and client methods. Use when writing database queries, using CRUD operations, filtering data, or configuring Prisma Client. Triggers on "prisma query", "findMany", "create", "update", "delete", "$transaction". |

---
*Skills Library*

---
name: postgres-least-privilege-api-tests
description: "Use when testing Postgres privilege and lock boundaries."
version: 0.1.0
author: "<autor>"
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [postgres, security, concurrency, testing]
    related_skills: [test-driven-development, requesting-code-review]
---

# Postgres least-privilege API verification

## When to Use

Use for SQL migrations separating webhook ingestion from trusted services, atomic send gates, evidence promotion, or cancellation leases. Requires disposable Postgres, dedicated test logins and Podman. Never run the destructive harness against production.

## Procedure

- Test with real LOGIN connections that inherit only the dedicated NOLOGIN execution role; SET ROLE from a superuser connection can hide privilege leaks.
- Cast literal arguments explicitly in privilege probes (`'{}'::jsonb`): an unknown literal passed to a function named like a composite array type (e.g. `_ai_sent`) can resolve as a type cast instead of invoking the function. Assert `has_function_privilege` and exercise the exact typed signature before interpreting a missing permission error as an ACL leak.
- Keep existing migrations immutable. Extend through a separate restricted-owner API schema, explicit SECURITY DEFINER entrypoints, fully qualified references, fixed search_path ending in pg_temp, static SQL, and separate ingress/service allowlists.
- Compare the global service-role ACL entries themselves, not entire acl arrays: adding a restricted owner grant changes the array without changing global service-role permissions.
- Acquire canonical-identity advisory and lead locks before evaluating a gate or mutating a send reservation in the same transaction. Assert another connection actually waits through pg_stat_activity before committing the competing signal or unknown event.
- Begin a cancellation lease TTL after waiting for serialization locks; time captured at function entry can produce an already-expired grant and concurrent holders. Test with lock wait exceeding the requested TTL.
- Reject promotion of missing ledger content rather than filling it from caller text; verify exact provider ID, identity, current cycle, content, and trusted evidence.
- Guard any custom unittest evidence runner with `if __name__ == '__main__'`: multiprocessing spawn imports the runner, and unguarded discovery recursively starts the full suite and disposable databases.
- Journal exact container names, labels and ports before tests. After cleanup, check existence for each exact name. On timeout, remove only journaled containers whose labels match; never remove all containers sharing a generic test label.
- Verify migration reruns and fail-closed rollback on disposable Postgres. Report inherited migration-order limitations explicitly rather than changing applied migrations to bypass them.
- Exercise installation as a non-superuser migration login matching the target PostgreSQL major version and observed role attributes before declaring cloud readiness. CREATEROLE alone does not prove permission to transfer ownership or SET ROLE; test the required owner changes inside BEGIN/ROLLBACK and read back role memberships and catalog after failure. Do not present an untested membership workaround as a validated installer.
- Run security verifiers against the complete final migration chain, not only the migration that introduced them. A later migration can add DEFINER entrypoints, grants or tables and invalidate the earlier checksum, allowlists and RLS expectations while behavioral tests remain green. Add version-aware verification through a new file/migration; preserve prior migration checksums and require negative tests for unlisted entrypoints, extra grants, disabled RLS and definition drift.
- Inventory every table and function introduced by evidence/audit migrations as part of the same trust boundary. Restrict ACLs, verify the declared RLS invariant and register the new API version/checksum; audit storage is not exempt from security checks merely because message execution still passes.

## Pitfalls

Use `terminal` for execution and `read_file`/`patch` for source inspection and edits. Keep production credentials out of harnesses. A successful grant or migration call is not evidence of denied bypasses; negative tests must run as the real restricted login.

## Verification

Require successful complete-suite execution with no skipped security cases, expected permission-denied results for legacy dispatch/DML/proofs, observed lock waits, preserved immutable checksums and global ACL entries, and removal of every exact container created by the run.

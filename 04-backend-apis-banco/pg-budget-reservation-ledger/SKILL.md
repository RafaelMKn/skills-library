---
name: pg-budget-reservation-ledger
description: Use when implementing PostgreSQL daily API budget gates.
---

# PostgreSQL budget reservation gates

- Reserve maximum verified token costs atomically before every external attempt, including retries. Never keep a database transaction open during network IO.
- Count all unresolved reservations regardless of creation date, plus resolved spend on the current accounting day. A previous-day unresolved request can still incur next-day spend; midnight must not release its liability.
- Never auto-release timeout or unknown-usage reservations. Settle only explicitly validated integer usage within the saved input/output caps; reject conflicting repeat settlements and make identical repeats idempotent.
- Save an immutable operator-verified tariff snapshot, source URLs, currency conversion and validity dates. Block absent, expired or mismatched-model tariffs; use exact decimal strings and bigint arithmetic with conservative integer cost ceiling.
- When serializing reads through a PostgreSQL advisory transaction lock, explicitly use READ COMMITTED before the first lock query. Repeatable-read or serializable defaults can pin a pre-lock snapshot and invalidate read-then-insert admission logic.
- Sample the database clock after acquiring the lock. Derive named-zone accounting dates in PostgreSQL, and conservatively charge late resolution on its resolution day.
- Protect snapshots/caps and settled rows with constraints and immutability triggers. RLS and grants must deny untrusted API roles; privileged application code must still use the gate.
- Prove concurrency, old-day carryover, missing usage, immutable snapshots, decimal boundaries and non-default session isolation against an explicitly isolated loopback database.
- If a shared transaction helper is owned by another agent and unavailable, report the dependency. A clearly labeled scratch transaction-contract harness can exercise real PostgreSQL service SQL, but it does not verify the missing helper or make the repository typecheck pass; rerun against the real helper before declaring integration complete.

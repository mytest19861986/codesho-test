# Current Task: SPRINT1-SYNTHETIC-ACCOUNT-BOOTSTRAP-ARCHITECTURE-71A

- Owner: Codex
- Status: ARCHITECTURE_AND_PRIVACY_GATE / IN_PROGRESS / SYNTHETIC_ONLY.
- BASE_SHA: `bdc2839bb03e829064066496739d47c7cbb05c07`.
- Target repository: `mytest19861986/codesho-test`.
- Branch: `agent/task71a-synthetic-account-bootstrap-architecture`.
- Worktree: new clean isolated worktree; old dirty checkout and prior branches preserved.
- Employer standing authorization date: `2026-07-26`.

## Goal

Define the future Synthetic Account Bootstrap boundary from an adult attestation
to an opaque synthetic account, membership, and dormant credential state. This
Task changes no code, migration, API, configuration, product capability, or
user behavior.

## Exact allow-list

```text
docs/decisions/2026-07-26-synthetic-account-bootstrap-boundary.md
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
docs/reviews/s1-071a-synthetic-account-bootstrap-architecture-review-summary.md
```

## Task71A authority and gates

Commit and push of this documentation-only branch and creation of a Draft PR
are authorized. Ready-for-review marking, merge to `codesho-test/main`, and
any implementation or production action are not authorized by this assignment.
Independent provider-neutral security, privacy, database, and RLS review,
internal consistency review, exact-file review, and the three required CI
checks remain gates before requesting further authority.

## Historical Task70A closeout evidence

```text
PR #9: CLOSED / MERGED
MERGE_COMMIT: 5be173afb03197cbc2e293e2ff28e1f9156a47ad
MERGE_PARENTS: 27a8626d29bfa7e21c5e770455db6b20a4521ccc,
               0aea2e0a1dbba925343a854de35683b84d83a748
SOURCE_BRANCH: PRESERVED
PR #5: OPEN / DRAFT / UNCHANGED / HEAD ee708a59fda89f08b824b079ebece2eed3b5515b
NEXT_STATE: WAITING_FOR_NEXT_SEPARATE_AUTHORIZATION
```

No Production, deployment, release, real-user, public API, backfill, provider,
or protected `codesho` promotion is authorized. Legal retention/deletion/hold
decisions remain `LEGAL_PENDING`.

## Historical Task69B contract

The independent append-only provenance table contains only a server UUIDv4,
opaque tenant UUID, unique opaque attestation reference, constants
`internal_synthetic_harness` and `self_attestation`, and a server UTC
timestamp. It contains no subject, PII, raw signal, operator identity,
document, digest, cookie, payload, free text, or metadata map.

It is created only for a newly created attestation in the same
`tenant_atomic` transaction. Replay creates no new provenance; failures of
provenance or audit roll back the full acceptance. PostgreSQL RLS, same-tenant
trigger validation, append-only trigger, and runtime INSERT-only grants are
mandatory. No legacy backfill is allowed.

## Historical Task69B implementation gates

```text
MIGRATION DRIFT: NONE
EMPTY POSTGRESQL MIGRATION: REQUIRED
MODEL/MIGRATION CONSISTENCY: REQUIRED
ATTESTATION + PROVENANCE + AUDIT ATOMICITY: REQUIRED
IDEMPOTENT REPLAY: REQUIRED
CONCURRENT DUPLICATE SAFETY: REQUIRED
CROSS-TENANT LINKAGE: REJECTED
RLS FAIL-CLOSED: REQUIRED
RUNTIME SELECT/UPDATE/DELETE/TRUNCATE: REJECTED
DATABASE UPDATE/DELETE: REJECTED
PROVENANCE IN API/AUDIT/LOG: NONE
PROHIBITED OR FREE-TEXT FIELDS: NONE
LEGACY BACKFILL: NONE
PRODUCTION INTERNAL MODE: REJECTED
```

The block above records completed Task69B implementation evidence only; it is
not an active Task71A acceptance block and creates no Task71A implementation
requirement. Task71A gates are: self-review, independent provider-neutral
security/privacy/database/RLS review, internal consistency, exact five-file
allow-list, `git diff --check`, and backend/frontend/smoke_restore CI on the
Task71A head. PR #11 is OPEN / DRAFT; its creation is complete, while review,
CI, and any Ready or merge transition remain pending and separately gated.

## Authority and exclusions

Commit, push, Draft PR, and in-scope documentation remediation are authorized.
`READY TRANSITION: NOT YET AUTHORIZED`; `MERGE: NOT AUTHORIZED`. Direct push to `main`, force-push,
rebase, source-branch deletion, PR #5 mutation/merge, backfill, public API,
frontend, account/user/membership/session creation, external providers, real
data, deployment, release, Alpha/Production, and protected `codesho`
promotion are forbidden. Legal retention/deletion/hold policies remain
`LEGAL_PENDING` and unchanged.

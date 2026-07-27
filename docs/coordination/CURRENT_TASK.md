# Current Task: SPRINT1-SYNTHETIC-ACCOUNT-BOOTSTRAP-IMPLEMENT-71B

- Owner: Codex
- Status: IMPLEMENTATION / IN_PROGRESS / INTERNAL_SYNTHETIC_ONLY.
- BASE_SHA: `5149bb1c7bf1ca6cf590bfafc3833876de11ec0a`.
- Target repository: `mytest19861986/codesho-test`.
- Branch: `agent/task71b-synthetic-account-bootstrap`.
- Worktree: `H:\codesho\codesho\worktrees\codesho-task71b`.
- Employer standing authorization date: `2026-07-26`.

## Goal

Implement the approved internal synthetic-only foundation from an adult
attestation to an opaque User, inactive roleless membership, and dormant
no-credential state. No public endpoint, signup flow, authentication, role
activation, real-user or Production capability is authorized.

## Exact allow-list

```text
backend/modules/identity/models.py
backend/modules/identity/migrations/0010_synthetic_account_bootstrap.py
backend/modules/identity/synthetic_bootstrap.py
backend/modules/platform_tenant/models.py
backend/modules/platform_tenant/migrations/0003_synthetic_membership_activation.py
backend/modules/platform_event/models.py
backend/modules/platform_event/security_audit.py
backend/modules/platform_event/migrations/0011_synthetic_bootstrap_events.py
backend/tests/test_synthetic_account_bootstrap.py
docs/data-dictionary.md
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
docs/reviews/s1-071b-synthetic-account-bootstrap-review-summary.md
```

## Task71B authority and gates

Small scoped commits, push of the authorized branch, Draft PR creation, and
in-allow-list review remediation are authorized. Ready, merge, direct main
push, source deletion, public API/OpenAPI, frontend, credentials, login,
membership activation, real users, Production, deployment, release, and
protected `codesho` promotion are not authorized. The final Draft PR must pass
the exact 14-file check, all local acceptance checks, sequential reviews, and
backend/frontend/Compose/smoke_restore CI.

## Task71B acceptance checkpoint

```text
EXACT_BASE_SHA: REQUIRED
ISOLATED_CLEAN_WORKTREE: REQUIRED
EXACT_14_FILE_ALLOW_LIST: REQUIRED
OPENAPI_NON_CHANGE: REQUIRED
FRONTEND_TREE_NON_CHANGE: REQUIRED
READY/MERGE: NOT_AUTHORIZED
REAL_USERS/PRODUCTION: NOT_AUTHORIZED
LEGAL_RETENTION/DELETION/ERASURE/HOLD: LEGAL_PENDING
```

The architecture review and Task71A merge are historical inputs to this
implementation. No Task71B user activation, credential enrollment, public API,
or Production claim is implied.

---

## Historical Task71A authority and gates

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
Task71A head. PR #11 is OPEN / DRAFT; creation, independent review, and CI
closeout are complete. Ready and merge remain separately gated and are not
authorized.

## Authority and exclusions

Commit, push, Draft PR, and in-scope documentation remediation are authorized.
`READY TRANSITION: NOT YET AUTHORIZED`; `MERGE: NOT AUTHORIZED`. Direct push to `main`, force-push,
rebase, source-branch deletion, PR #5 mutation/merge, backfill, public API,
frontend, account/user/membership/session creation, external providers, real
data, deployment, release, Alpha/Production, and protected `codesho`
promotion are forbidden. Legal retention/deletion/hold policies remain
`LEGAL_PENDING` and unchanged.

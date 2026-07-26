# Current Task: SPRINT1-TASK69B-POST-MERGE-CLOSEOUT-70A

- Owner: Codex
- Status: COMPLETE / MERGED / VERIFIED; waiting for next separate authorization.
- BASE_SHA: `5be173afb03197cbc2e293e2ff28e1f9156a47ad`.
- Target repository: `mytest19861986/codesho-test`.
- Branch: `agent/task70a-task69b-post-merge-closeout`.
- Worktree: new clean isolated worktree; old dirty checkout and source branch preserved.
- Employer standing authorization date: `2026-07-26`.

## Goal

Record and verify the successful Task69B merge. This closeout changes no code,
migration, API, configuration, product capability, or user behavior.

## Exact allow-list

```text
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
docs/reviews/s1-069b-provenance-implementation-review-summary.md
```

## Task70A closeout evidence

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

## Acceptance criteria and gates

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

Required reviews are sequential: self-review, security, privacy, database/RLS,
and provider-neutral review. All findings require disposition; raw prompts and
responses stay outside the repository. Task70A changed exactly four
allow-listed documentation files; CI passed backend, frontend, and
smoke_restore on the merged Task69B head. The project is waiting for the next
separate authorization; no Ready or merge transition remains for Task70A.

## Authority and exclusions

Commit, push, Draft PR, and in-scope documentation remediation are authorized.
`READY TRANSITION: NOT YET AUTHORIZED`; `MERGE: NOT AUTHORIZED`. Direct push to `main`, force-push,
rebase, source-branch deletion, PR #5 mutation/merge, backfill, public API,
frontend, account/user/membership/session creation, external providers, real
data, deployment, release, Alpha/Production, and protected `codesho`
promotion are forbidden. Legal retention/deletion/hold policies remain
`LEGAL_PENDING` and unchanged.

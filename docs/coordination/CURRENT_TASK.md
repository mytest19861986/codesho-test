# Current Task: SPRINT1-TASK71B-POST-MERGE-CLOSEOUT-71C

- Owner: Codex
- Status: AUTHORIZED / DOCS-ONLY / POST-MERGE-CLOSEOUT.
- BASE_BRANCH: `origin/main`.
- BASE_SHA: `f08ddd9e56ea2c7f503fbe4e5287f4665840ec2b`.
- Branch: `codex/task71c-post-merge-closeout`.
- Scope: only the four Task71C coordination/review documents.

## Task71B final disposition

PR #12 is `CLOSED / MERGED` by Squash into `codesho-test/main` at
`f08ddd9e56ea2c7f503fbe4e5287f4665840ec2b`. The former candidate
`297a4daaa50fd34d05c7de29eac2608a64b162f8` is superseded. Post-merge CI run
`31042633399` and Compose smoke/restore run `31042633952` are `SUCCESS`.
Independent review is `PASS` with zero open blockers.

No Production, Alpha, real-user activation, deployment, or promotion to the
protected `codesho` repository occurred or is authorized.

## Current next state

`AWAITING_COMMANDER_NEXT_TASK`. No implementation, migration, API, frontend,
infrastructure, dependency, merge, direct-main push, or prior-branch deletion
is authorized by this closeout task. Legal retention/deletion/erasure/hold
decisions remain `LEGAL_PENDING`.

## Historical Task71B record

The Task71B implementation and remediation details below are preserved as
historical evidence. References to Draft, Ready, unmerged, or merge-blocked
states describe pre-merge checkpoints only and are not the current status.

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

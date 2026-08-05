# Task71B Synthetic Account Bootstrap Review Summary

Status: `COMPLETE / MERGED / VERIFIED`

Task: `SPRINT1-SYNTHETIC-ACCOUNT-BOOTSTRAP-IMPLEMENT-71B`
Repository: `mytest19861986/codesho-test`
Base: `5149bb1c7bf1ca6cf590bfafc3833876de11ec0a`
Branch: `agent/task71b-synthetic-account-bootstrap`

## Final disposition

PR #12 was Squash-merged into `codesho-test/main` at
`f08ddd9e56ea2c7f503fbe4e5287f4665840ec2b`. Post-merge CI run
`31042633399` and Compose smoke/restore run `31042633952` completed with
`SUCCESS`. The independent review final verdict is `PASS` with
`OPEN_BLOCKING_FINDINGS: 0`.

The pre-merge Draft, Ready, unmerged, and merge-blocked references below are
preserved as historical review/remediation evidence only. This merge did not
authorize or enable Production, Alpha, real-user activation, deployment,
public API expansion, or promotion to protected `codesho`.

## Exact scope

Only these 14 paths may change:

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

No public API, OpenAPI, frontend, configuration, credential, login, session,
role activation, real-user, backfill, Production, deployment, release, or
protected-repository behavior is authorized.

## Implementation self-review

- [x] Explicit human/synthetic identity mode and opaque synthetic handle.
- [x] Synthetic User has no username, email, phone, name, or contact value,
      is inactive, and receives an unusable password only.
- [x] Request uses opaque UUID references, tenant/idempotency uniqueness, and
      one lifetime attestation linkage.
- [x] Membership is inactive, roleless, and marked synthetic-bootstrap.
- [x] Service is explicit, internal-mode gated, tenant-atomic, lock-based,
      idempotent, replay-safe, and audit all-or-nothing.
- [x] RLS/FORCE RLS and database linkage/dormancy contracts are defined in
      migrations; runtime mutation and activation are rejected.
- [x] Audit event is bounded and metadata-free.

## Required verification gates

```text
EXACT BASE / CLEAN ISOLATED WORKTREE: REQUIRED
EXACT 14-FILE ALLOW-LIST / GIT DIFF --CHECK: REQUIRED
RUFF / MYPY / DJANGO CHECK: REQUIRED
MAKEMIGRATIONS --CHECK --DRY-RUN: REQUIRED
EMPTY SQLITE / EMPTY POSTGRESQL MIGRATION: REQUIRED
FOCUSED + FULL BACKEND TESTS / COVERAGE: REQUIRED
OPENAPI BYTE-FOR-BYTE / FRONTEND TREE NON-CHANGE: REQUIRED
SECURITY / PRIVACY / DATABASE-RLS / INTERNAL REVIEWS: REQUIRED
BACKEND / FRONTEND / COMPOSE / smoke_restore CI: REQUIRED
READY / MERGE: NOT AUTHORIZED
LEGAL RETENTION / DELETION / ERASURE / HOLD: LEGAL_PENDING
```

Raw review prompts, attachments, and responses remain outside the repository;
only bounded findings, dispositions, and evidence belong here.

## Independent review V1 disposition

Review V1 returned `FAIL` with four blockers. Remediation is restricted to the
same 14 paths and a new head/re-review is required:

| Finding | Disposition |
|---|---|
| `71B-CI-01` module boundary imports | `REMEDIATED`: service now uses Django app registry, transaction-local tenant context, and the approved audit DB function without cross-module imports. |
| `71B-SEC-01` unusable password and mutation | `REMEDIATED`: PostgreSQL accepts Django's `!%` unusable marker and a database trigger rejects synthetic password/identity/activation mutation. |
| `71B-PRIV-01` synthetic names | `REMEDIATED`: model/migration constraints and trigger require empty `first_name`/`last_name`; focused test covers invented names. |
| `71B-TEST-01` missing evidence | `REMEDIATED IN SCOPE`: focused tests now include PostgreSQL runtime grants, dormancy guards, real audit integration, and concurrent first requests; the required CI remains the authoritative evidence. |

No finding authorizes Ready, merge, public API, real users, Production, or
protected `codesho` promotion.

## Independent review V2 disposition

Review V2 found three blockers, all addressed within the exact allow-list:

| Finding | Disposition |
|---|---|
| `71B-V2-DB-01` psycopg percent escaping | `REMEDIATED`: PostgreSQL SQL uses `!%%`, which schema-editor execution renders as `!%`. |
| `71B-V2-CONC-01` identical concurrent replay | `REMEDIATED`: the idempotency lookup is repeated after the attestation serialization lock and returns the terminal result. |
| `71B-V2-TEST-01` PostgreSQL/RLS evidence | `REMEDIATED IN SCOPE`: focused tests now cover missing/cross-tenant RLS visibility, runtime grants, direct membership/user guards, cross-link rejection, real audit, concurrency, late rollback, and migration contract evidence. Final CI remains authoritative. |

V3 independent review, final CI, and exact-file review remain pending. Ready,
merge, direct `main` push, real users, Production, and protected `codesho`
promotion remain unauthorized.

## Independent review V3 disposition

V3 returned three blockers on `fc338caa1b3590a20363f61a208ea04009f51a38`.
Remediation is restricted to this same 14-file allow-list and requires a new
non-amended commit, full CI/Compose gates, and V4 review:

| Finding | Disposition |
|---|---|
| `71B-V3-SEC-01` synthetic origin and credential immutability | `REMEDIATED`: model and PostgreSQL trigger boundaries reject human/synthetic mode transitions and synthetic credential creation; negative tests cover both paths. |
| `71B-V3-TEST-02` real audit rollback evidence | `REMEDIATED`: PostgreSQL integration now uses the real audit append, forces a late request failure, and proves the audit row is absent after rollback. |
| `71B-V3-DOC-03` coordination inconsistency | `REMEDIATED`: current-head, CI, review, and historical Task71A markers are aligned. |

Remediation commit: `4da41b7c05c12ccbd1c8b8d94360fe0b7d79f8b5`.
CI `30255137479` and Compose `30255137504` both SUCCESS. Local full suite:
`199 passed, 39 skipped`, coverage `86.60%`. At this pre-merge checkpoint,
Independent V4 review remained required and PR #12 was Draft; no Ready/merge
action was then authorized.

## Independent review V4 disposition

V4 returned two blockers on `2b3d9ebfb3ad7ec8d29f98d178ab541fb678f9d3`:

| Finding | Disposition |
|---|---|
| `71B-V4-TEST-01` direct PostgreSQL guard evidence | `IN_REMEDIATION`: add migrator/direct-SQL negative assertions for both identity-mode transition directions and synthetic credential insertion. |
| `71B-V4-DOC-02` stale current-head checkpoint | `IN_REMEDIATION`: update coordination current-head and CI fields to the exact reviewed head before requesting V5. |

## Independent review V5 disposition

V5 found one documentation self-reference issue: a hardcoded SHA in a
coordination commit becomes stale as soon as that commit is created. The
coordination checkpoint now uses the authoritative PR head (`git rev-parse
HEAD`) and explicitly treats PR checks attached to that head as authoritative.
This is `REMEDIATED`; final CI on this checkpoint and an independent final
review remain required. The exact commit SHA is recorded in the handoff and
Git history rather than duplicated as a self-referential field.

## Independent review V6 final verdict

Review V6 on `b2129c4539a520a3265e4ebf89033c7cbafd3761` returned
`FINAL VERDICT: PASS` with `OPEN_BLOCKING_FINDINGS: 0`. It confirmed the
direct PostgreSQL guard evidence, real audit rollback, RLS and tenant
isolation, idempotency/concurrency/immutability, exact 14-file scope, and
the Draft-only boundary. CI `30256726798` and Compose
`30256726683` were SUCCESS. The PR remains OPEN / DRAFT; Ready, merge,
deployment, release, real users, and protected-repository promotion remain
unauthorized. Legal retention/deletion/erasure/hold remains `LEGAL_PENDING`.

## Commander re-review remediation

The historical V6 verdict was superseded by a Commander `FAIL / MERGE_BLOCKED`
decision. Remediation is limited to the existing 14-file allow-list and remains
unpushed and unmerged.

| Finding | Disposition |
|---|---|
| Request/audit binding was incomplete | `REMEDIATED`: the PostgreSQL request trigger now requires the exact event ID, event type, outcome, reason, tenant, subject User, null actor/credential, and derived idempotency key. Seven direct-SQL mismatch cases are covered. |
| Membership guard blocked human lifecycle | `REMEDIATED`: DELETE is handled before NEW access; synthetic update/delete remains forbidden, while human activation/deactivation/delete follows baseline UPDATE/DELETE privileges. Runtime TRUNCATE remains revoked. |
| Synthetic administrative flags were not constrained | `REMEDIATED`: model constraint, migration state, service defaults, PostgreSQL insert/update/delete trigger, ORM negatives, and direct-SQL negatives require `is_staff=false` and `is_superuser=false`. |
| Provenance rollback evidence was incomplete | `REMEDIATED IN TEST SCOPE`: PostgreSQL tests use valid attestations and cover missing, cross-tenant, and wrong-attestation provenance, proving User/membership/request/audit rollback. |
| Reverse contract was unconditionally irreversible | `REMEDIATED`: identity, membership, and audit allow-list reverse paths are allowed only when no protected synthetic data/evidence or incompatible nullable-role membership exists; otherwise they raise `IrreversibleError` fail-closed. Empty and populated PostgreSQL paths have dedicated tests. |
| Generated OpenAPI baseline drift | `OUT_OF_SCOPE`: Task71B changes no OpenAPI, URL, auth-view, or frontend path. |

Local remediation evidence: Ruff PASS; MyPy 47 files PASS; module boundaries
PASS; Django check PASS; migration drift NONE; empty SQLite migration PASS;
focused `9 passed / 15 PostgreSQL-only skipped`; full backend `199 passed / 49
skipped`; coverage `85.55%` against the 80% gate. PostgreSQL/Compose CI remains
mandatory before any Ready or merge action.

## Commander remediation re-review verdict

Commander re-review returned `PASS` with `OPEN_BLOCKERS: 0`. The exact scoped
remediation may be committed once without amend and pushed only to
`codesho-test` branch `codex/task71b-review-remediation`. Branch CI remains a
gate. Ready, merge, direct main push, protected `codesho` promotion, deployment,
release, real users, and Production remain unauthorized.

## PostgreSQL CI remediation after run 31014336650

Backend CI on remote head `9c5d6ee79268424099c1f5ff16df6d029b94f27d`
reported 12 failures. Three valid-path tests mocked a successful append without
creating the audit row required by PostgreSQL; PostgreSQL now uses the real
audit function while SQLite retains the bounded mock. Seven negative ORM tests
expected raw psycopg `RaiseException`; they now assert Django's `DatabaseError`
wrapper and exact trigger reason.

The original empty reverse probe incorrectly assumed the shared test audit
table had no prior immutable evidence. The second Commander re-review rejected
the intermediate recording-schema-editor replacement: the probe now runs first
in this module, executes all three real PostgreSQL reverse paths inside one
atomic transaction, asserts the empty precondition with FORCE RLS temporarily
removed, verifies trigger/policy/function/constraint and RLS state after the
reverse, and raises a marker exception to prove the complete catalog baseline
is restored by rollback.

Populated reverse tests assert each exact `IrreversibleError`, the wrapped
database guard reason where applicable, and identical catalog state before and
after rejection. FORCE RLS is removed only for the owner-visible compatibility
guard. It is restored to the contract owned by the still-applied dependency
`platform_tenant.0002_membership_rls` before Task71B objects are removed; both
migrations document that ownership explicitly.

Corrective local evidence after the second re-review patch: focused `9 passed /
15 PostgreSQL-only skipped`; full backend `199 passed / 49 skipped`; coverage
`85.55%`; Ruff, MyPy, module boundaries, Django check, migration drift, and
empty SQLite migration all PASS. Real PostgreSQL CI remains mandatory. No
corrective commit, push, or merge is authorized by this checkpoint.

# Task71B Synthetic Account Bootstrap Review Summary

Status: `IN_PROGRESS / REMEDIATION_REQUIRED / DRAFT_ONLY`

Task: `SPRINT1-SYNTHETIC-ACCOUNT-BOOTSTRAP-IMPLEMENT-71B`
Repository: `mytest19861986/codesho-test`
Base: `5149bb1c7bf1ca6cf590bfafc3833876de11ec0a`
Branch: `agent/task71b-synthetic-account-bootstrap`

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

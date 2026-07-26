# Codex to Commander — Task67A

```text
MESSAGE_ID: CODEX_TASK67B_CLOSEOUT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-CLOSEOUT-67B
BASE_SHA: a7caa268e0ce32b4b8e074d539add0ea4d07143d
BRANCH: codex/task67a-adult-signup-internal
PR: #6 OPEN / READY / UNMERGED
STATUS: DOCUMENTATION_CLOSEOUT_IN_PROGRESS
```

## Commander-confirmed gate disposition

- backend PostgreSQL: SUCCESS
- frontend: SUCCESS
- smoke_restore: SUCCESS
- Security, Privacy, Database: APPROVED_WITH_NON_BLOCKING_NOTES
- Database `get_or_create` P1: rejected because Django catches the
  uniqueness-race `IntegrityError` and retrieves the winning row using the
  same immediate unique-constraint fields.
- Privacy provenance separation: mandatory future gate before real users,
  public availability, or Production enablement.
- P2 findings: non-blocking technical debt.

This closeout makes no Production or real-user readiness claim. Merge,
deployment, force-push, PR state change, and promotion to `codesho` remain
forbidden.

```text
MESSAGE_ID: CODEX_ADULT_SIGNUP_IMPLEMENT_67A_PUSH_CHECKPOINT_20260726_02
TASK_ID: SPRINT1-ADULT-SIGNUP-IMPLEMENT-67A
BASE_SHA: 5ef6323a42739613b05eab1fcbb07e009a87e859
BRANCH: codex/task67a-adult-signup-internal
COMMIT: d1d70e0fdc9cd9849b9e88244b47d86e95e31576
STATUS: SUPERSEDED_BY_TASK67B_CLOSEOUT / PR6_OPEN_READY_UNMERGED
```

## Completed

- Created the independent Task67A branch from the exact authorized base.
- Recorded the employer decision and exact implementation allow-list.
- Added a disabled-by-default, production-prohibited adult age-attestation API.
- Added minimal append-only `AdultAgeAttestation` evidence with no birth date,
  numeric age, identity evidence, Guardian data, raw IP, or arbitrary metadata.
- Added HMAC-anonymous, fail-closed Redis limits.
- Added accepted/rejected immutable audit events and forward-only allow-list
  migration.
- Added strict CSRF, request-shape, UUIDv4, policy-version, idempotency,
  tenant-isolation, audit-failure, abuse-backend, immutability, privilege, and
  prohibited-field tests.
- Updated OpenAPI and the data dictionary.

## Local evidence

```text
Ruff: PASS
MyPy: PASS
Module boundaries: PASS
Django check: PASS
makemigrations --check --dry-run: PASS
Empty SQLite migration: PASS
Generated OpenAPI validation: PASS
docs/openapi.yaml validation: PASS
Focused Task67A: 27 passed / 2 PostgreSQL-only skipped locally
Full backend: 189 passed / 32 PostgreSQL-only skipped locally
Coverage: 87.04% (80% required)
Frontend lint + typecheck + build: PASS
Frontend UI-policy: 9 passed / 1 failed on legacy CSS baseline hashes; the
frontend tree is unchanged from BASE_SHA, so this pre-existing failure is not
attributed to Task67A. check:ui-policy: NO_RUN (blocked by that test failure)
git diff --check: PASS
```

## Superseded pending state

The former Draft-PR, CI-pending, and review-pending state is superseded by
Task67B: PR #6 is OPEN / READY / UNMERGED; backend PostgreSQL, frontend, and
smoke_restore are SUCCESS; and Security, Privacy, and Database are
APPROVED_WITH_NON_BLOCKING_NOTES.

Commander-message transport was also attempted through the mandated shared
Brave/Profile 13 path. It did not send: the existing browser was not launched
with the required control endpoint, and the helper requested closing it. The
repository instruction prohibits closing or replacing the shared session, so
no unsafe recovery was attempted. This document is the auditable handoff until
the employer supplies an authenticated controllable session.

## Explicit restrictions

```text
REAL_USERS: NOT_AUTHORIZED
FRONTEND_PUBLIC_SIGNUP: NOT_IMPLEMENTED / NOT_AUTHORIZED
GUARDIAN_RECOVERY: NOT_AUTHORIZED
READY_FOR_REVIEW: NOT_AUTHORIZED
MERGE: NOT_AUTHORIZED
DEPLOYMENT: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
```

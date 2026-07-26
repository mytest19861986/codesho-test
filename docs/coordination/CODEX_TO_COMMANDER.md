# Codex to Commander — Task67A

```text
MESSAGE_ID: CODEX_ADULT_SIGNUP_IMPLEMENT_67A_LOCAL_CHECKPOINT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-IMPLEMENT-67A
BASE_SHA: 5ef6323a42739613b05eab1fcbb07e009a87e859
BRANCH: codex/task67a-adult-signup-internal
STATUS: LOCAL_IMPLEMENTATION_COMPLETE / PUBLICATION_BLOCKED_MISSING_GH
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
Frontend: 10 UI-policy tests + policy + lint + typecheck + build PASS
git diff --check: PASS
```

## Pending

- Install and authenticate the required GitHub CLI in the Codex environment,
  then push the scoped commit and open a Draft PR to obtain real PostgreSQL CI.
- Complete the required external security/privacy/database review before any
  future Ready-for-Review or Merge authority.

The GitHub publication workflow explicitly requires `gh`; it is not installed
in this environment. No local commit, push, Draft PR, or CI run was created,
and the connector was not used to bypass that prerequisite.

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

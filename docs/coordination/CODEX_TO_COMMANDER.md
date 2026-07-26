# Codex to Commander — Task69A

```text
MESSAGE_ID: CODEX_TASK69A_PROVENANCE_ARCHITECTURE_CHECKPOINT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-PROVENANCE-ARCHITECTURE-69A
BASE_SHA: fc2aa2f4d7261dc7bb597886dbe782163313eceb
BRANCH: agent/task69a-provenance-architecture
PR_7: CLOSED / MERGED
MERGE_COMMIT: fc2aa2f4d7261dc7bb597886dbe782163313eceb
STATUS: ARCHITECTURE_ONLY / PRIVACY_GATE / REVIEW_REQUIRED
REAL_USERS: NOT_AUTHORIZED
PRODUCTION/DEPLOYMENT/RELEASE: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
PR_5: PRESERVED_AS_DRAFT / UNCHANGED
```

## Task69A checkpoint

Added the provider-neutral architecture decision
`docs/decisions/2026-07-26-adult-signup-provenance-separation.md`. It defines
the separation of the minimal `adult_attested` claim from restricted opaque
provenance, distinguishes subject/attestation/provenance/security-audit
boundaries, specifies tenant/RLS fail-closed, immutability, idempotency and
data-minimization invariants, compares Options A/B/C, and records legal
retention/deletion/hold questions as `LEGAL_PENDING`.

No model, migration, endpoint, OpenAPI, configuration, test, frontend,
account, credential, provider, deployment, release, or real-user behavior was
changed. No sensitive or raw review content is included.

Task68E was accepted and verified: PR #7 is CLOSED / MERGED with parents
`e11557f378231469d22348f4959caa554dbbd406` and
`3c61ae6b4b2408a8f2dd759eb266089ac3a3ccff`. PR #5 remains a draft and was
not mutated.

## Required gates before closeout

- self-review and internal consistency: required;
- provider-neutral independent documentation review: required;
- privacy architecture verdict: PASS required;
- exact four-file allow-list and `git diff --check`: required;
- new backend, frontend, and smoke_restore CI: required;
- commit, push, draft PR, ready transition, and merge only under Task69A
  authorization and after all gates pass.

The next implementation step is a separate authorized Task69B. This checkpoint
does not create a Production claim or authorize real users.

```text
MESSAGE_ID: CODEX_TASK68A_POST_MERGE_CLOSEOUT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-POST-MERGE-CLOSEOUT-68A
BASE_SHA: e11557f378231469d22348f4959caa554dbbd406
BRANCH: agent/task68a-post-merge-closeout
PR_6: CLOSED / MERGED
MERGED_AT: 2026-07-26T12:48:10Z
MERGE_COMMIT: e11557f378231469d22348f4959caa554dbbd406
STATUS: IMPLEMENTATION_COMPLETE / CI_REQUIRED / MERGE_NOT_AUTHORIZED
```

## Verified merge checkpoint

- Authorized PR head:
  `9247bec6e22e8415344d78ee90018ea8eaaeac90`.
- Merge parents: `5ef6323a42739613b05eab1fcbb07e009a87e859` and
  `9247bec6e22e8415344d78ee90018ea8eaaeac90`.
- Merge method: merge commit.
- backend PostgreSQL: SUCCESS.
- frontend: SUCCESS.
- smoke_restore: SUCCESS.
- No deployment, release, Production activation, real-user activation,
  protected `codesho` promotion, direct push, rebase, force-push, or branch
  deletion occurred as part of Task67C.

Task68A only reconciles the four allow-listed documents with this verified
state. Its merge requires separate employer authorization.

```text
MESSAGE_ID: CODEX_TASK67B_CLOSEOUT_20260726_01
TASK_ID: SPRINT1-ADULT-SIGNUP-CLOSEOUT-67B
BASE_SHA: a7caa268e0ce32b4b8e074d539add0ea4d07143d
BRANCH: codex/task67a-adult-signup-internal
HISTORICAL_PR_STATE: #6 OPEN / READY / UNMERGED
STATUS: COMPLETED / MERGED_BY_PR_6
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

This closeout made no Production or real-user readiness claim. Its merge was
later separately authorized and completed by Task67C. Deployment, release,
Production enablement, real-user activation, and promotion to `codesho` remain
forbidden.

```text
MESSAGE_ID: CODEX_ADULT_SIGNUP_IMPLEMENT_67A_PUSH_CHECKPOINT_20260726_02
TASK_ID: SPRINT1-ADULT-SIGNUP-IMPLEMENT-67A
BASE_SHA: 5ef6323a42739613b05eab1fcbb07e009a87e859
BRANCH: codex/task67a-adult-signup-internal
COMMIT: d1d70e0fdc9cd9849b9e88244b47d86e95e31576
STATUS: HISTORICAL / SUPERSEDED_BY_TASK67B_CLOSEOUT / PR6_OPEN_READY_UNMERGED
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

## Historical pending state

The former Draft-PR, CI-pending, review-pending, and OPEN / READY / UNMERGED
states are historical. PR #6 is CLOSED / MERGED; backend PostgreSQL, frontend,
and smoke_restore are SUCCESS; and Security, Privacy, and Database are
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
PR_6_READY_TRANSITION: COMPLETED UNDER SEPARATE AUTHORIZATION
PR_6_MERGE: COMPLETED UNDER SEPARATE TASK67C AUTHORIZATION
TASK68A_MERGE: NOT_AUTHORIZED
DEPLOYMENT: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PROTECTED_CODESHO_PROMOTION: NOT_AUTHORIZED
```

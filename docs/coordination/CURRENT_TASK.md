# Current Task: SPRINT1-ADULT-SIGNUP-IMPLEMENT-67A

- Owner: Codex
- Status: local implementation complete; publication is blocked because the
  required GitHub CLI is unavailable. PostgreSQL CI and required external
  review remain pending. Development/internal synthetic-data authority only.
- BASE_SHA: `5ef6323a42739613b05eab1fcbb07e009a87e859`.
- Target repository: `mytest19861986/codesho-test`.
- Branch: `codex/task67a-adult-signup-internal`.
- Employer authorization date: `2026-07-26`.

## Goal

Implement a fail-closed adult age-attestation foundation for a future signup
flow. The endpoint may record only a self-attested `18+` status and minimal
immutable evidence for a synthetic opaque subject. It does not create a user,
credential, membership, session, Guardian relationship, or public signup flow.

## Exact allow-list

```text
.env.example
backend/config/adult_signup.py
backend/config/settings/base.py
backend/config/settings/local.py
backend/config/settings/production.py
backend/config/urls.py
backend/modules/identity/models.py
backend/modules/identity/migrations/0008_adult_age_attestation.py
backend/modules/platform_event/models.py
backend/modules/platform_event/security_audit.py
backend/modules/platform_event/migrations/0010_adult_signup_events.py
backend/tests/test_adult_signup.py
docs/coordination/CODEX_TO_COMMANDER.md
docs/coordination/CURRENT_TASK.md
docs/coordination/PROJECT_STATE.md
docs/data-dictionary.md
docs/decisions/2026-07-26-adult-signup-internal.md
docs/openapi.yaml
docs/reviews/s1-067a-adult-signup-review-summary.md
```

No frontend, workflow, Docker/Compose, Nginx, deployment, protected-repository,
Guardian/Recovery, birth-date, identity-document, or real-user file is in scope.

## Acceptance criteria

1. The feature defaults to disabled and production settings reject activation.
2. Only `internal_test` mode with the exact server policy version can persist
   an attestation.
3. The request requires explicit boolean `true`; false or missing values fail
   closed and never create an attestation.
4. Only synthetic opaque UUIDs are accepted as subjects. No date of birth,
   numeric age, identity document, national identifier, raw IP, or free text is
   accepted or stored.
5. Valid requests are subject to fail-closed HMAC-anonymous Redis limits by
   synthetic subject and client IP; raw signals are never Redis keys.
6. Accepted attestations and the supported rejection are recorded in the
   immutable security audit ledger with allow-listed metadata.
7. Attestation persistence and accepted audit append are atomic and
   idempotent for tenant, subject, and policy version.
8. Attestation rows are append-only in application code and PostgreSQL; the
   runtime role has no update, delete, or truncate privilege on the table.
9. The API and OpenAPI contract expose no account-creation claim.
10. Focused tests cover disabled mode, exact request shape, missing/false
   attestation, policy mismatch, tampering fields, idempotency, audit failure,
   rate limiting/backend failure, tenant separation, immutability, and
   prohibited data-field absence.
11. Repository-defined backend CI checks and `git diff --check` pass.

## Review and release gates

```text
Security/privacy/database review: REQUIRED BEFORE MERGE
Repository CI: REQUIRED BEFORE MERGE
Real-user Legal approval: REQUIRED / BLOCKING
Ready for Review: NOT AUTHORIZED BY THIS TASK
Merge: NOT AUTHORIZED
Deployment: NOT AUTHORIZED
Protected codesho promotion: NOT AUTHORIZED
```

## Stop conditions

Stop for new authority if implementation requires real user data, birth date,
identity evidence, Guardian/Minor/Recovery, account creation, frontend/public
activation, external provider access, a file outside the allow-list, Merge, or
Deployment.

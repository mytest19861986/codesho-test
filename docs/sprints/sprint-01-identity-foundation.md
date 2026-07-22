# Sprint 1 — Identity Foundation (Planning Only)

Status: backlog/evidence reconciled at `7f23ec882d30f76cba1f4b0b504849c1fd48b184`.
Existing foundations are evidenced below; no new feature is authorized by this
document. Recovery, Guardian, Signup, Onboarding and Notification remain out of
scope or deferred unless a separate approved Task says otherwise.

## Sprint goal

Deliver a tenant-safe identity foundation for a teen learner, guardian and
platform operator without external notification providers or commercial
workflow integration.

## User stories and planned work

| Priority | Story / task | Estimate | Dependencies | Acceptance criteria |
|---|---|---:|---|---|
| P0 | As a learner, I can create and use an approved passcode credential. | M | Employer decision 3 | Passcode is hashed, never logged, validation is server-side and an initial-change flow is enforced. |
| P0 | As the system, I resist passcode spraying and lockout abuse. | M | Decision 3, cache/Redis availability | Account/IP/device/global controls, five-attempt behavior, timed lockout and negative tests pass. |
| P0 | As a guardian, I have an approved relationship and recovery boundary. | M | Decision 3 and legal policy | Tenant-safe guardian-link model, authorization service and audit events are covered by isolation tests. |
| P0 | As an operator, I access only the approved administrative scope. | S | Decision 2 | Admin allow-list/policy is implemented, cross-tenant negative tests pass and actions are audited. |
| P0 | As deployment, migrations use the approved role separation. | M | Decision 1, deployment credentials | Runtime cannot alter schema or bypass RLS; migrator runbook and PostgreSQL integration test pass. |
| P1 | As a guardian, I receive an anomalous-login notice. | M | Decision 4, provider and consent approval | Not started unless provider, consent, template and delivery/audit controls are approved. |

## Security tests

- Tenant-absence and cross-tenant access must fail closed.
- Session/CSRF same-origin, session fixation, logout and credential-change
  tests must pass.
- S1-005 login uses a tenant-host-only username/passcode endpoint, explicit
  CSRF protection, 12-hour browser sessions, session-auth epoch invalidation,
  fail-closed Redis/Audit gates, and typed immutable audit producers.
- Lockout/rate-limit tests cover account, IP, device and global limits without
  recording sensitive credential material.
- PostgreSQL RLS and connection-reuse negative tests run in CI.
- Outbox duplicate-delivery tests cover any approved notification event.
- OpenAPI is generated and compatibility-checked for every public API change.

## Migration and rollback considerations

- Apply migrations from an empty PostgreSQL database and verify reverse/forward
  compatibility before release.
- Credential state changes are additive and rollback must not expose or erase
  immutable audit/consent evidence.
- Do not call notification providers inside a database transaction; any later
  delivery uses an idempotent outbox consumer inheriting `BaseTenantTask`.
- Roll back application code only after checking the migration compatibility
  window; use an approved forward migration for irreversible security state.

## Exit criteria

All P0 acceptance criteria, required backend/frontend checks, OpenAPI check,
PostgreSQL migration-from-empty-database proof, tenant isolation negatives,
session/CSRF tests and outbox duplicate-delivery tests are green. Employer
decisions and any legal/provider approvals are attached to the release record.

## Task54 evidence reconciliation

This table distinguishes implementation/test evidence in `codesho-test` from
Production, Alpha and protected-repository eligibility. Statuses are limited to
`COMPLETE_WITH_EVIDENCE`, `PARTIAL/TEST_ONLY`, `BLOCKED`, `DEFERRED`, and
`NOT_STARTED`.

| Backlog item | Status | Existing evidence and boundary |
|---|---|---|
| PostgreSQL migrator/runtime separation | COMPLETE_WITH_EVIDENCE | Implementation checkpoint `972c54b`; CI/Compose role, DDL/RLS denial and ownership/grant checks recorded in `PROJECT_STATE.md`. This is not Production deployment proof. |
| Passcode credential foundation | COMPLETE_WITH_EVIDENCE | S1-002 implementation/review summaries; Argon2id, versioned Pepper HMAC, validation, model/migration and tests. |
| Abuse-control/lockout foundation | COMPLETE_WITH_EVIDENCE | S1-003 implementation and sequential reviews; Redis Lua controls, fail-closed behavior, delays, lockout and negative tests. |
| Immutable security audit foundation | COMPLETE_WITH_EVIDENCE | S1-004 migration/review summary plus Task45/48 audit-mock lifecycle fix and Task50/51 Claude documentation checkpoint. |
| Secure login/session and forced passcode-change flow | COMPLETE_WITH_EVIDENCE | S1-005 review summary, E2E/HTTP evidence, CI/Compose green runs `29919602405`/`29919602325`; implementation is not Production/Alpha activation proof. |
| Dev-only login UI | PARTIAL/TEST_ONLY | `/login` and auth contract/test evidence exist; it remains development-only and does not authorize Production, Alpha or protected promotion. |
| Guardian relationship/recovery | DEFERRED | No guardian relationship/recovery implementation or approved legal recovery policy is evidenced in this checkpoint. |
| Platform operator/admin scope | PARTIAL/TEST_ONLY | Django Admin registrations exist, but approved operator allow-list/policy, tenant boundary, audited actions and negative tests are not implemented as the 2-A scope. |
| Guardian notification | DEFERRED | Decision 4-A-revised defers provider, consent, template, delivery and audit workflow. |

## Production and environment eligibility distinction

Existing implementation/test evidence does not establish Production readiness,
real Alpha readiness, or eligibility to promote to protected `codesho`. Open
gates remain Production TLS and `__Host-` proof, legal retention/privacy review,
Production cleanup scheduling, real Alpha activation, and deferred
Signup/Recovery/Guardian/OAuth/Onboarding work. Promotion to protected
`codesho` remains unauthorized.

## Single candidate for the next implementation Task

Candidate: platform-operator/admin scope under employer decision 2-A.

Goal and boundary: create a narrowly allow-listed Django Admin capability for
approved platform operators, with explicit tenant-record boundaries and
immutable audit events for permitted administrative actions. This candidate
does not add public APIs, guardian recovery, notifications, UI, Alpha users or
Production activation.

Security invariants: fail closed for non-staff and non-operator users; never
use Django superuser status as a substitute for the approved policy; prevent
cross-tenant access except for explicitly approved platform-level records;
preserve tenant context and RLS boundaries; audit every permitted mutation with
typed non-sensitive metadata; do not expose passcodes, cookies, tokens or raw
provider data; keep published/audit evidence immutable.

Required test matrix: unauthenticated/non-staff denial; operator allow-list;
tenant-scoped read and mutation; cross-tenant negative access; platform-record
boundary; audit success/failure and idempotency; session/CSRF/admin login
behavior; PostgreSQL RLS and connection-reuse isolation; migration-from-empty
database; OpenAPI unchanged/no public contract drift; secret/sensitive-field
non-disclosure.

Potential migration/API/OpenAPI impact: likely additive authorization metadata
or policy tables and possibly audit reason/event allow-list entries; no API
change is assumed. Any migration, audit contract or API impact must be confirmed
by a future approved Task and forward-only migration review.

Proposed future allowed files (subject to a new Task):
`backend/modules/identity/admin.py`,
`backend/modules/platform_tenant/admin.py`,
`backend/modules/identity/admin_policy.py`,
`backend/modules/identity/models.py`,
`backend/modules/platform_event/security_audit.py`,
`backend/tests/test_admin_scope.py`,
`backend/tests/test_security_audit.py`.
No migration or security-document file is authorized in this candidate because
the required exact migration/document names are not yet determined; any such
file requires a separate design review and independent Task. OpenAPI files are
not authorized because no public API change is proposed.

Out of scope: guardian/recovery, notification providers, public admin APIs,
login UI, signup/onboarding/OAuth, payment, Production/Alpha activation,
protected promotion, and unrelated refactors.

The candidate is proposed, not approved for implementation. It requires a new
Task and independent BASE_SHA.

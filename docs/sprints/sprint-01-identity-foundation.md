# Sprint 1 — Identity Foundation (Planning Only)

Status: draft; no implementation is authorized until all decisions in
`docs/decisions/sprint-01-employer-gate.md` are approved.

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

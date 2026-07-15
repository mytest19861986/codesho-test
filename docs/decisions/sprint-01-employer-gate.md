# Sprint 1 Employer Gate — Identity Foundation

Status: approved 2026-07-15. The recorded employer decisions authorize Sprint
1, beginning with S1-001 role separation; identity/passcode implementation
remains a separate approved backlog item.

## Recorded employer decisions

- 1-B approved: a deployment/CI-only PostgreSQL migrator role and a
  least-privilege runtime role.
- 2-A approved: platform-operator Django Admin scope, with tenant records
  hidden until a tenant-scoped policy is approved.
- 3-A revised approved: six-digit passcode policy; detailed revised controls
  must be captured before passcode implementation.
- 4-A revised approved: guardian anomalous-login notification is deferred;
  minimal immutable security audit evidence remains in scope.

## 1. PostgreSQL migrator and runtime roles

- Problem: the application runtime role must not retain schema-change power.
- Analysis: migrations need DDL privileges; web, worker and beat processes do
  not. Sharing one role enlarges compromise impact.
- Options: (A) one shared role; (B) a CI/deployment-only migrator and a
  least-privilege runtime role; (C) managed-provider migration service.
- Recommendation: B.
- Reason: preserves deployability while making the runtime role unable to
  alter schema or bypass RLS.
- Security impact: B materially limits database compromise blast radius.
- Cost impact: low operational scripting/secret-management cost; no required
  paid service.
- Implementation dependency: production deployment credentials, migration
  runbook and role-grant migration must be approved before production setup.

## 2. Django Admin global versus tenant-scoped policy

- Problem: `/admin/` intentionally bypasses tenant-selection middleware, so
  staff access needs an explicit data-scope rule.
- Analysis: global admin is efficient for foundation operations but risks
  accidental cross-tenant access; tenant-scoped admin adds implementation and
  review complexity.
- Options: (A) global admin restricted to platform operators with audited
  break-glass access; (B) tenant-scoped admin for all staff; (C) no Django
  Admin for tenant records and custom staff workflows only.
- Recommendation: A for foundation operations, with tenant records hidden
  until a tenant-scoped policy is approved.
- Reason: delivers safe operational capability without pretending generic
  ModelAdmin filters are a complete tenant authorization system.
- Security impact: requires least privilege, immutable audit events and an
  explicit cross-tenant access procedure.
- Cost impact: A is lowest; B/C require more custom development and testing.
- Implementation dependency: staff role matrix and ModelAdmin allow-list must
  be approved before staff-facing identity administration.

## 3. Teen passcode policy

- Problem: the approved minimum of six digits needs a final UX and abuse
  policy before credentials are implemented.
- Analysis: short numeric passcodes are memorable but have low entropy and
  need rate limits, lockout and forced rotation.
- Options: (A) six digits, five attempts, timed lockout and mandatory first
  login change; (B) eight digits with the same controls; (C) guardian-set
  password plus an optional local passcode.
- Recommendation: A for Alpha, retaining the ability to move to B after
  telemetry and usability review.
- Reason: it matches the approved Alpha default while keeping abuse controls
  enforceable and understandable for teen users.
- Security impact: rate limits must cover account, IP, device and global
  signals; never log the passcode; secure hashing and reset/audit flows are
  mandatory.
- Cost impact: low; B has negligible technical cost but potentially greater
  support/abandonment cost.
- Implementation dependency: approved reset ownership, lockout duration and
  guardian recovery rules are required before identity endpoints.

## 4. Guardian anomalous-login notification in MVP

- Problem: notification can help guardians respond to suspicious access but
  requires a provider, consent/retention policy and false-positive handling.
- Analysis: no SMS/email provider is selected; emitting notices without a
  delivery and privacy policy would create an incomplete security promise.
- Options: (A) defer guardian notification and retain only minimal immutable
  security audit evidence; (B) email notification after provider and consent
  approval; (C) SMS notification after provider, cost and consent approval.
- Recommendation: A for MVP/Identity Foundation, with B evaluated before paid
  production.
- Reason: avoids provider coupling and sensitive-data processing before the
  legal and operational controls exist.
- Security impact: detection/audit remains; guardian alerting is unavailable
  until the later approved integration.
- Cost impact: A has no provider cost; B/C add recurring delivery, support and
  consent-management costs.
- Implementation dependency: provider selection, consent wording, retention,
  notification templates and incident-response ownership are required for B/C.

## Employer response required

Reply with one option for each: `1-B`, `2-A`, `3-A`, `4-A`, or explicitly
replace an option with an approved alternative and owner.

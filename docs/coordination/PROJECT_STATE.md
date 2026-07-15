# Codesho Project State

Updated: 2026-07-15 (SZ-021 complete; employer decision gate pending)

## Current Status

Sprint Zero is technically closed at `013bccc834b31c91a1424c14a304eb6acc01ff0a`
on `codesho-test/main`. Its two required GitHub Actions workflows completed
successfully:

- CI `29427888761`: backend and frontend checks passed.
- Compose smoke and restore `29427888874`: isolated full-stack startup,
  PostgreSQL RLS/connection-reuse tests, and backup/restore drill passed.

SZ-021 is complete at `dc13cc8e72b2f67eaf6bf97c018f1fc7c2d076bf`: it records
review traceability and prepares, but does not implement, the employer
decisions that gate Sprint 1 Identity Foundation. Its CI `29430842483` and
Compose smoke/restore `29430842466` are both successful.

## Completed

- Employer architecture and Sprint Zero defaults recorded.
- Django 5.2 modular-monolith skeleton and Next.js TypeScript/RTL build.
- Tenant context, PostgreSQL RLS migration and negative tests.
- Outbox foundation, duplicate-delivery tests and `BaseTenantTask`.
- Docker Compose, Nginx same-origin proxy, Redis/Celery, OpenAPI and CI.
- Sprint Zero threat, load and backup/restore documentation.
- SZ-020 Claude review completed and findings dispositioned; no unresolved
  Claude P0 remains. The auditable summary is at
  `docs/reviews/sz-020-review-resolution-summary.md`.
- SZ-021 employer decision gate and Sprint 1 plan prepared and verified
  without new production or identity workflow code.

## Historical Evidence

- Earlier CI `29406301878` for `0e65d23` and CI `29427689716` / Compose
  `29427689672` for `49c25c1` remain historical checkpoints. They are not the
  current closure evidence.
- The current closure evidence is the successful pair for `013bccc` above.

## In Progress

- No implementation work is active. Await employer decisions before Identity
  Foundation code begins.

## Blockers

- Employer decisions are required for production migrator/runtime role
  separation, tenant-scoped Django Admin policy, teen passcode policy, and
  guardian anomalous-login notification.
- Local Docker daemon remains unavailable:
  `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
  The required Compose gate passed in isolated GitHub Actions.

## Next Steps

1. Employer answers the four questions in
   `docs/decisions/sprint-01-employer-gate.md`.
2. Commander converts the answers into the approved Sprint 1 backlog.
3. Implement Identity Foundation only after that approval; do not promote to
   the protected `codesho` repository without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain
  deferred.
- Legal retention/privacy/aging-out rules require counsel before paid
  production.
- Local Compose verification remains unavailable, though the CI/staging gate
  is green.

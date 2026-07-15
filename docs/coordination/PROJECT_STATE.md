# Codesho Project State

Updated: 2026-07-15 (S1-001 migrator/runtime separation awaiting CI)

## Current Status

Sprint Zero is technically closed at `013bccc834b31c91a1424c14a304eb6acc01ff0a`
on `codesho-test/main`. Its two required GitHub Actions workflows completed
successfully. The employer approved all four Sprint 1 gate decisions on
2026-07-15, authorizing S1-001 PostgreSQL migrator/runtime separation.

- CI `29427888761`: backend and frontend checks passed.
- Compose smoke and restore `29427888874`: isolated full-stack startup,
  PostgreSQL RLS/connection-reuse tests, and backup/restore drill passed.

SZ-021 is complete at `dc13cc891dfff2e4df9a70ce61da7d8e73f3a4f2`: it records
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
- SZ-021 employer decision gate and Sprint 1 plan prepared and verified.
- Employer decisions recorded: 1-B, 2-A, 3-A-revised and 4-A-revised.

## Historical Evidence

- Earlier CI `29406301878` for `0e65d23` and CI `29427689716` / Compose
  `29427689672` for `49c25c1` remain historical checkpoints. They are not the
  current closure evidence.
- The current closure evidence is the successful pair for `013bccc` above.

## In Progress

- S1-001 separates `codesho_migrator` from `codesho_runtime`: migrations run
  in a one-shot Compose service; backend, worker and beat use runtime-only
  database URLs; CI and Compose smoke/restore now verify DDL/RLS denial and
  restored ownership/grants. Local lint, targeted backend tests, migration
  check, mypy, Compose configuration and diff check pass. Commit/push and
  GitHub workflow verification are pending.

## Blockers

- Local Docker daemon remains unavailable:
  `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
  The required S1-001 Compose gate must run in isolated GitHub Actions.

## Next Steps

1. Commit and push S1-001 to `codesho-test/main`.
2. Monitor CI and Compose smoke/restore until both are green; repair any
   failure before handoff.
3. Send the S1-001 evidence to Commander. Do not begin passcode work until a
   new Commander task is assigned; do not promote to protected `codesho`
   without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain
  deferred.
- Legal retention/privacy/aging-out rules require counsel before paid
  production.
- Local Compose verification remains unavailable, though the CI/staging gate
  is green.

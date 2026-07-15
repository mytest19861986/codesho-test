# Codesho Project State

Updated: 2026-07-15 (SZ-020 Claude review completed)

## Current Status

Sprint Zero is `CI_GREEN` at `49c25c1`; SZ-020 Claude-dispositioned tenant and
outbox hardening passed CI, including the isolated Compose PostgreSQL
backup/restore gate.

## Completed

- Employer architecture and initial product defaults recorded.
- Django 5.2 LTS modular-monolith skeleton.
- Next.js 16.2.10 TypeScript/RTL production build.
- Tenant candidate/transaction middleware, PostgreSQL RLS migration and negative tests.
- Outbox foundation and `BaseTenantTask`.
- Docker Compose, Nginx same-origin proxy, PostgreSQL schemas, Redis and Celery.
- OpenAPI generation, module-boundary gate, backup/restore scripts.
- GitHub Actions workflow and Sprint Zero threat/load/DR documents.
- Reusable Codex master prompt, persistent execution protocol and AI handoff file templates.
- Local validation: 10 passed, 2 PostgreSQL-only tests skipped, 94% coverage,
  Ruff/MyPy/ESLint/TypeScript/Next production build passed.
- GitHub Actions CI run `29406301878` completed successfully for commit
  `0e65d23`: backend and frontend jobs both passed. The backend CI job ran
  against PostgreSQL and Redis and includes the PostgreSQL-specific RLS and
  physical-connection-reuse tests.

## In Progress

- No implementation work is active. Employer decisions remain before the
  associated production/Identity work can start.

## Blocker

The local Docker daemon remains unavailable:
`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
SZ-016 passed through the isolated GitHub Actions fallback.
The local Docker daemon remains unavailable; the required PostgreSQL/Compose
integration gate passed in GitHub Actions.

## Next Steps

1. Obtain employer decisions for production migrator/runtime role separation,
   tenant-scoped admin policy, and guardian anomalous-login notification.
3. Do not promote to the primary `codesho` repository without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain deferred.
- Teen passcode entropy/UX must be closed before the Identity Sprint.
- Legal retention/privacy/aging-out rules require counsel before paid production.
- Docker was unavailable locally; container integration remains a CI/staging gate.
- Production role separation and tenant-admin policy require employer approval.
- Guardian anomalous-login notification requires employer approval before the
  Identity Sprint.

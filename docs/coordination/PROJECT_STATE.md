# Codesho Project State

Updated: 2026-07-15 (CI checkpoint reconciled)

## Current Status

Sprint Zero foundation and AI coordination protocol are published to the
`codesho-test` checkout on `main` at
`0e65d232c4ae4a16dd458d130e63e76630594e0c`.

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

- Claude security/architecture review of the prepared 16-file Sprint Zero
  package.

## Blocker

No current implementation or CI blocker. The GitHub CLI is not installed in
this environment, so CI was verified through the public GitHub Actions API.

## Next Steps

1. Submit the prepared Claude package and classify each finding before changes.
2. Keep the next Sprint gated on accepted security-review resolutions.
5. Do not promote to the primary `codesho` repository without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain deferred.
- Teen passcode entropy/UX must be closed before the Identity Sprint.
- Legal retention/privacy/aging-out rules require counsel before paid production.
- Docker was unavailable locally; container integration remains a CI/staging gate.
- The Claude review package is prepared in the coordination root and awaits
  review; no findings have been received or applied.

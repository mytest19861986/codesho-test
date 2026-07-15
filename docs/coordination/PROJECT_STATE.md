# Codesho Project State

Updated: 2026-07-15 (SZ-020 local resolution checkpoint)

## Current Status

Sprint Zero is `CI_GREEN` at `168332c`; P0 task SZ-016 passed the isolated
Compose smoke and PostgreSQL backup/restore gate.

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

- SZ-020 Claude review: Batch 01 received; Batch 02 rate-limited and not
  Claude-verified. Local preliminary review is authorized; gate remains open.

## Blocker

The local Docker daemon remains unavailable:
`failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
SZ-016 passed through the isolated GitHub Actions fallback.
Claude provider reported: `out of free messages until 6:50 PM` (Asia/Tehran).
No quota or authentication bypass was attempted. Batch 02-A/B/C is prepared
but must not be sent until the quota window opens.

## Next Steps

1. Resolve Batch 01 findings and run local checks; label local Batch 02 review
   `LOCAL_PRELIMINARY_REVIEW / NOT_CLAUDE_VERIFIED`.
2. After 18:50 Asia/Tehran, send Batch 02-A once, then B and C sequentially.
3. Do not promote to the primary `codesho` repository without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain deferred.
- Teen passcode entropy/UX must be closed before the Identity Sprint.
- Legal retention/privacy/aging-out rules require counsel before paid production.
- Docker was unavailable locally; container integration remains a CI/staging gate.
- Claude Batch 01 is received and pending resolution; Batch 02 is blocked by
  provider usage limit.

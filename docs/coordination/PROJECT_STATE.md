# Codesho Project State

Updated: 2026-07-15

## Current Status

Sprint Zero foundation is implemented in the local `codesho-test` checkout.
Local commit: `965db24 chore: establish Sprint Zero foundation`.

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

## In Progress

- Publish the local commit to `codesho-test` and execute GitHub CI.
- Run PostgreSQL-specific RLS and physical-connection-reuse tests in CI.

## Blocker

The current execution environment has no GitHub credential and no `gh` binary.
`git push -u origin main` failed with:

`fatal: could not read Username for 'https://github.com': No such device or address`

## Next Steps

1. Authenticate GitHub for Codex (`gh auth login` or workspace GitHub connection).
2. Push commit `965db24` to `codesho-test`.
3. Monitor CI, fix all failures and record the final green run.
4. Request Commander/Claude review for the security-sensitive Sprint Zero files.
5. Do not promote to the primary `codesho` repository without employer approval.

## Open Decisions / Risks

- Payment, SMS, video, object-storage and online-session providers remain deferred.
- Teen passcode entropy/UX must be closed before the Identity Sprint.
- Legal retention/privacy/aging-out rules require counsel before paid production.
- Docker was unavailable locally; container integration remains a CI/staging gate.

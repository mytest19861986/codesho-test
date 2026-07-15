# Codesho Engineering Instructions

## Authority

- Employer approval is required for scope, architecture, paid infrastructure and production release.
- Commander AI owns technical coordination and review.
- Codex implements code, tests and refactors from approved architecture.
- Gemini produces UI proposals and lightweight frontend review.
- Claude reviews high-risk architecture/security packages of no more than 19 files.

## Architecture

- Backend: Django 5.2 LTS + Django REST Framework.
- Frontend: Next.js App Router + TypeScript.
- Architecture: Modular Monolith.
- Database: PostgreSQL with `codesho` as the main application schema.
- `audit`, `analytics` and `platform` are optional dedicated schemas.
- Background jobs: Celery + Redis.
- Business logic lives in Django, never in Next.js.
- All API changes must remain represented in OpenAPI.

## Hard Rules

- Do not access PostgreSQL from Next.js.
- Do not place business workflows in Django signals or serializers.
- Do not call external providers inside a database transaction.
- Tenant-specific Celery tasks must inherit from `BaseTenantTask`.
- Tenant context must fail closed when absent.
- Never log OTP, passcode, tokens, secrets or sensitive child data.
- Use IRR minor units in persistence; toman is presentation only.
- Store operational timestamps as UTC `TIMESTAMPTZ`; Jalali is presentation only.
- Published content, consent decisions, receipts, evidence and audit events are immutable.

## Repository Workflow

- This repository is the test/integration workspace.
- Do not push directly to the production repository without employer approval.
- Keep commits small and scoped.
- Run relevant tests before handing work back.
- Never rewrite or discard user changes.
- At the start of every new chat, read `docs/coordination/CODEX_MASTER_PROMPT_FA.md`
  and `docs/coordination/PROJECT_STATE.md` before changing files.
- Update `docs/coordination/PROJECT_STATE.md` before every handoff or session end.
- When running under the employer's Windows workspace, use
  `H:\codesho\codesho\codesho` as the project root and
  `H:\codesho\codesho` as the AI coordination root.
- Never assume which repository is open: inspect `git remote -v`. The
  `codesho-test` remote permits Sprint implementation; the `codesho` remote is
  protected until the employer approves promotion.

## Persistence Protocol

- Continue autonomously through safe, in-scope work; do not stop after analysis,
  scaffolding, the first failing test, or a partial implementation.
- A task ends only when its acceptance criteria and relevant checks pass, or a
  genuine blocker requires employer authority, credentials, a provider choice,
  paid infrastructure, or external coordination.
- Before reporting a blocker, exhaust safe diagnostics and alternatives, record
  the exact failed command/error, and leave a resumable checkpoint.
- Never wait indefinitely. Poll long-running work, fix failures and continue.
- Do not ask the employer to repeat project history that exists in repository
  documents.

## Required Verification

- Backend lint, type-check and tests.
- Frontend lint, type-check and tests.
- Migration apply from an empty database.
- Tenant isolation negative tests.
- Session/CSRF same-origin tests.
- Outbox duplicate-delivery tests.
- OpenAPI generation and compatibility check.

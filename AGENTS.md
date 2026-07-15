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

## Required Verification

- Backend lint, type-check and tests.
- Frontend lint, type-check and tests.
- Migration apply from an empty database.
- Tenant isolation negative tests.
- Session/CSRF same-origin tests.
- Outbox duplicate-delivery tests.
- OpenAPI generation and compatibility check.

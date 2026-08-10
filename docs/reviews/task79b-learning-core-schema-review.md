# Task79B Learning Core Schema / RLS Review

Task: `SPRINT1-DOMAIN-LEARNING-CORE-SCHEMA-RLS-79B`

Base: `30dfe7e94e39edb20d65a3e2d5b382162cdd5e56`

Status: `IMPLEMENTATION / PROVIDER REVIEWS PENDING`

## Scope review

Implemented scope is limited to:

- `Course`
- `Lesson`
- learning app registration
- schema migrations
- PostgreSQL same-tenant integrity
- FORCE RLS
- immutable stable-key guards
- focused model/PostgreSQL tests
- module-boundary declaration
- coordination/review documentation

No learner/user relation, cohort, progress, assignment, session, API, OpenAPI, frontend, fixture, dependency, deployment, release, Production, or protected-repository action is introduced.

## Security invariants to review

1. No tenant context returns no learning rows.
2. Tenant A cannot read tenant B rows.
3. `WITH CHECK` rejects cross-tenant writes.
4. `Lesson(tenant_id, course_id)` must reference the same tenant's Course at database level.
5. Runtime role must not bypass FORCE RLS.
6. Transaction-local tenant context must not leak across connection reuse.
7. Course code, lesson code and lesson position remain immutable on PostgreSQL.
8. No API/client-provided tenant authority exists.

## Qwen gate

Prompt: `QWEN_TASK79B_LEARNING_CORE_SCHEMA_RLS_REVIEW_01_V1`

Result: pending.

## Claude hard gate

Prompt: `CLAUDE_TASK79B_LEARNING_CORE_SCHEMA_RLS_HARD_GATE_01_V1`

Result: pending.

PASS requires `P0=0`, `P1=0`, `OPEN_BLOCKERS=0` after exact-content provenance binding.

# Task80A — Course/Lesson Read-Contract Architecture

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

Branch: `codex/task80a-learning-course-lesson-read-contract-architecture`

Status: `ARCHITECTURE_ONLY / VALIDATION IN PROGRESS`

## Objective

Define a bounded, tenant-safe, read-only Course/Lesson contract for a later separately authorized implementation task.

## Authorized files

1. `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md`
2. `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`
3. `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`

No other repository file is authorized for Task80A unless a test/CI defect demonstrates a documentation-only correction is necessary.

## Explicit exclusions

No runtime Python/TypeScript, API route, serializer, URL, canonical OpenAPI schema, migration, SQL, RLS, grant, model, frontend, fixture, cohort, progress, learner-specific state, PII activation, Release, Deployment, Production, or protected `codesho` change.

## Contract decisions

- Future read surface is limited to two GET proposals: Course list and lessons-by-course list.
- Learner-visible rows are published only.
- Tenant authority comes only from the validated existing request/session boundary.
- Existing active tenant membership remains the admission boundary.
- Cross-tenant and hidden parent identifiers must not disclose existence.
- Course response fields: id, code, title, state.
- Lesson response fields: id, code, title, position, state.
- Default page size: 20.
- Maximum page size: 100.
- Empty states are truthful empty collections; no fabricated academic values.
- Current canonical six-operation OpenAPI file remains unchanged in Task80A.

## Required gates

- exact docs-only diff review;
- no out-of-scope file changes;
- exact-head CI;
- exact-head Compose smoke/restore;
- Qwen architecture review;
- Claude architecture hard gate before any implementation successor.

## Next checkpoint

After exact-head CI/Compose are green, provide the exact three-file content packet to Qwen and then Claude. Task80A remains architecture-only regardless of provider verdict; runtime implementation requires a new Task.

No Release, Deployment, Production, or protected `codesho` action is authorized.

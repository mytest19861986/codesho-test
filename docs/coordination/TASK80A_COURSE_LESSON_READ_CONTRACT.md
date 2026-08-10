# Task80A — Course/Lesson Read-Contract Architecture

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

Implementation branch: `codex/task80a-learning-course-lesson-read-contract-architecture`

Closeout branch: `codex/task80a-closeout`

Status: `ARCHITECTURE MERGED / POST-MERGE GREEN / PROVIDER HARD-GATES PENDING`

## Objective

Define a bounded, tenant-safe, read-only Course/Lesson contract for a later separately authorized implementation task.

## Authorized architecture files

1. `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md`
2. `docs/reviews/task80a-learning-course-lesson-read-contract-review.md`
3. `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md`

No runtime Python/TypeScript, API route, serializer, URL, canonical OpenAPI schema, migration, SQL, RLS, grant, model, frontend, fixture, cohort, progress, learner-specific state, PII activation, Release, Deployment, Production, or protected `codesho` change was introduced.

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
- Current canonical six-operation OpenAPI file remained unchanged in Task80A.

## Exact-head pre-merge evidence

Reviewed architecture HEAD: `0eeb107e064bb99669c7ea0e94d52654df4687fe`

Exact changed-file count: 3.

Exact blob bindings:

- ADR: `5ad991af630f107a72edcd9d6e30af26eb78d4db`
- Review plan: `78f8f83cecd881651466b9c092f1454060968a9a`
- Coordination: `03b1143e698eeff778bbb1aef84cdbe9f99c0415`

Pre-merge CI:
- Run `31402531075`
- Result: `SUCCESS`

Pre-merge Compose smoke/restore:
- Run `31402530817`
- Result: `SUCCESS`

## Merge evidence

PR: `#35`

Merge method: race-safe squash with expected head SHA.

Expected/reviewed head: `0eeb107e064bb99669c7ea0e94d52654df4687fe`

Merged commit on `main`: `813db363411f857d35bc5774b7856cdc71b49e41`

PR state after merge: `CLOSED / MERGED`.

## Post-merge evidence

Post-merge CI on `main@813db363411f857d35bc5774b7856cdc71b49e41`:
- Run `31402907652`
- Result: `SUCCESS`
- Backend full tests: SUCCESS
- Frontend checks/build: SUCCESS
- Migration/OpenAPI/runtime-image checks: SUCCESS

Post-merge Compose smoke/restore:
- Run `31402907634`
- Result: `SUCCESS`
- PostgreSQL RLS and connection-reuse tests: SUCCESS
- Backup/restore verification: SUCCESS

## Provider gate status

Qwen architecture review: `PENDING`.

Claude architecture hard gate: `PENDING`.

Task80A must not authorize or start the runtime/API/OpenAPI implementation successor until both provider gates return zero P0/P1/open blockers and Claude recommends `READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.

## Final disposition at this checkpoint

Architecture documentation is merged and post-merge green.

Runtime implementation remains blocked by provider hard gates.

No Release, Deployment, Production, or protected `codesho` action occurred.

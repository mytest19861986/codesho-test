# Task80A Learning Course/Lesson Read-Contract Review

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

Status: `ARCHITECTURE MERGED / POST-MERGE GREEN / PROVIDER REVIEWS PENDING`

## Scope under review

Documentation-only architecture for a future read-only Course/Lesson API slice.

No runtime/API/OpenAPI canonical schema, migration, model, frontend, cohort, progress, learner-specific state, real-user activation, Release, Deployment, Production, or protected `codesho` change is permitted by Task80A.

## Review focus

1. The contract exposes only Course and Lesson data already authoritative in PostgreSQL.
2. Proposed future operations are exactly two GET collection operations.
3. Tenant authority is inherited from the existing validated request/session boundary.
4. Active tenant membership remains the admission boundary.
5. Cross-tenant identifiers do not disclose object existence.
6. Only published courses and published lessons are learner-visible.
7. Resource fields are minimized and exclude tenant ids, timestamps, audit/internal fields and learner-specific state.
8. Ordering is deterministic.
9. Pagination is always bounded with default 20 and maximum 100.
10. Empty/unavailable states remain truthful and never synthesize academic values.
11. Current canonical OpenAPI remains unchanged in this architecture task.
12. Cohort/progress remain explicitly blocked pending separate authority.

## Exact architecture provenance

Reviewed architecture HEAD: `0eeb107e064bb99669c7ea0e94d52654df4687fe`

Exact architecture file/blob bindings:

- `docs/decisions/2026-08-10-learning-course-lesson-read-contract-architecture-80a.md` — `5ad991af630f107a72edcd9d6e30af26eb78d4db`
- `docs/reviews/task80a-learning-course-lesson-read-contract-review.md` — `78f8f83cecd881651466b9c092f1454060968a9a`
- `docs/coordination/TASK80A_COURSE_LESSON_READ_CONTRACT.md` — `03b1143e698eeff778bbb1aef84cdbe9f99c0415`

Exact architecture diff: three documentation files only.

## Validation evidence

Pre-merge exact-head CI `31402531075`: `SUCCESS`.

Pre-merge exact-head Compose smoke/restore `31402530817`: `SUCCESS`.

PR `#35` was squash-merged race-safely with expected head SHA `0eeb107e064bb99669c7ea0e94d52654df4687fe`.

Merged main commit: `813db363411f857d35bc5774b7856cdc71b49e41`.

Post-merge CI `31402907652`: `SUCCESS`.

Post-merge Compose smoke/restore `31402907634`: `SUCCESS`.

Post-merge evidence includes backend full tests, frontend checks/build, canonical OpenAPI parity, PostgreSQL RLS/connection-reuse, and backup/restore success.

## Required Qwen architecture gate

Prompt ID: `QWEN_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_REVIEW_01_V1`

Qwen must review the exact three-file packet bound above and return:

- `CONTENT_RECEIVED_COMPLETE`;
- `HEAD_LABEL_REVIEWED`;
- verdict;
- P0/P1/P2 counts;
- open blockers;
- findings on tenant authority, active membership authorization, enumeration resistance, publication visibility, field minimization, pagination bounds, deterministic ordering, empty states, OpenAPI proposal boundary, and scope;
- `IMPLEMENTATION_RECOMMENDATION=READY_FOR_CLAUDE` only when P0=0, P1=0 and open blockers=0.

Status: `PENDING`.

## Required Claude architecture hard gate

Prompt ID: `CLAUDE_TASK80A_COURSE_LESSON_READ_CONTRACT_ARCH_HARD_GATE_01_V1`

Claude runs only after Qwen passes and receives the same exact three-file packet plus Qwen's complete response.

Claude must independently assess tenant isolation, membership authorization, privacy/data minimization, enumeration behavior, pagination bounds, publication visibility, OpenAPI expansion proposal safety, preservation of existing auth/session/CSRF/cookie behavior, and absence of cohort/progress/runtime scope creep.

PASS requires:

- `CONTENT_RECEIVED_COMPLETE=YES`;
- `P0_COUNT=0`;
- `P1_COUNT=0`;
- `OPEN_BLOCKERS=0`;
- `IMPLEMENTATION_RECOMMENDATION=READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.

Status: `PENDING`.

## Runtime successor gate

No runtime/API/OpenAPI implementation successor may start until both provider reviews are complete and the Claude PASS condition above is satisfied.

No Release, Deployment, Production, or protected `codesho` action is authorized.

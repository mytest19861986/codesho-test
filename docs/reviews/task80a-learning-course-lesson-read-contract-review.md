# Task80A Learning Course/Lesson Read-Contract Review

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

Status: `ARCHITECTURE REVIEW PENDING`

## Scope under review

Documentation-only architecture for a future read-only Course/Lesson API slice.

No runtime/API/OpenAPI canonical schema, migration, model, frontend, cohort, progress, learner-specific state, real-user activation, Release, Deployment, Production, or protected `codesho` change is permitted in Task80A.

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

## Required independent review

Qwen architecture challenge should return:

- P0/P1/P2 counts;
- open blockers;
- findings on authorization, enumeration, pagination, publication and scope;
- `READY_FOR_CLAUDE` only when P0=0, P1=0 and open blockers=0.

Claude architecture hard gate should then independently assess tenant isolation, authorization, privacy/minimization, OpenAPI proposal safety and scope.

PASS requires:

- P0=0;
- P1=0;
- OPEN_BLOCKERS=0;
- recommendation `READY_FOR_SEPARATE_IMPLEMENTATION_TASK`.

## Acceptance evidence before provider review

- exact docs-only diff;
- no runtime/API/OpenAPI canonical schema changes;
- repository CI successful at exact HEAD;
- Compose smoke/restore successful at exact HEAD.

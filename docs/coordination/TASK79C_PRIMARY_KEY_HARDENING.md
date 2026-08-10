# Task79C — Learning Primary-Key Immutability Hardening

Task: `SPRINT1-DOMAIN-LEARNING-PRIMARY-KEY-IMMUTABILITY-HARDENING-79C`

Base: `ab30d93128183cd26691224b6ea0efe85ef0d6a7`

Implementation branch: `codex/task79c-learning-pk-immutability-hardening`

Closeout branch: `codex/task79c-closeout`

Status: `COMPLETE / MERGED / POST-MERGE GREEN`

## Objective

Close Claude Task79B's single non-blocking P2 by explicitly preventing mutation of persisted `Course.id` and `Lesson.id` values.

## Implemented scope

- Django model-level immutable-id guards for persisted Course and Lesson rows.
- PostgreSQL migration `0003_primary_key_immutability` strengthening the existing immutable-update trigger function.
- Direct QuerySet/database mutation tests for Course.id and Lesson.id.
- Preservation of Course.code, Lesson.code and Lesson.position immutability.
- Preservation of FORCE RLS, tenant isolation, same-tenant Course/Lesson composite FK, runtime role restrictions, and DELETE/TRUNCATE denial.
- Reverse migration restores the exact Task79B immutable-trigger behavior.

No model field expansion, API/OpenAPI, frontend, learner/cohort/progress relationships, real-user PII, deployment, Release, Production, or protected `codesho` action was introduced.

## Provider gates

Qwen:
- Prompt: `QWEN_TASK79C_LEARNING_PRIMARY_KEY_IMMUTABILITY_REVIEW_01_V1`
- HEAD reviewed: `6490599073d39043cf962569e497a716b5e3fbc0`
- Verdict: `PASS`
- P0: 0
- P1: 0
- P2: 4
- Open blockers: 0
- Recommendation: `READY_FOR_CLAUDE`

Claude:
- Prompt: `CLAUDE_TASK79C_LEARNING_PRIMARY_KEY_IMMUTABILITY_HARD_GATE_01_V1`
- HEAD reviewed: `6490599073d39043cf962569e497a716b5e3fbc0`
- Content received complete: YES
- Content verdict: `PASS`
- Verdict: `PASS`
- P0: 0
- P1: 0
- P2: 4
- Open blockers: 0
- Merge recommendation: `READY`
- Final marker: `TASK79C_REVIEW_COMPLETE`

## Exact-head pre-merge evidence

Reviewed implementation HEAD: `6490599073d39043cf962569e497a716b5e3fbc0`

Exact changed-file count: 6.

Pre-merge CI:
- Run `31383517391`
- Result: `SUCCESS`

Pre-merge Compose smoke/restore:
- Run `31383517753`
- Result: `SUCCESS`

## Merge evidence

PR: `#33`

Merge method: squash with expected head SHA.

Expected/reviewed head: `6490599073d39043cf962569e497a716b5e3fbc0`

Merged commit on `main`: `5fb1bb0011bdcfced9308bc638851751283a7bde`

PR state after merge: `CLOSED / MERGED`.

## Post-merge evidence

Post-merge CI on `main@5fb1bb0011bdcfced9308bc638851751283a7bde`:
- Run `31401335940`
- Result: `SUCCESS`
- Backend full tests: SUCCESS
- Frontend checks/build: SUCCESS
- Migrations/OpenAPI/runtime image checks: SUCCESS

Post-merge Compose smoke/restore:
- Run `31401335885`
- Result: `SUCCESS`
- PostgreSQL RLS and connection-reuse tests: SUCCESS
- Backup/restore verification: SUCCESS

## Final disposition

Task79C Acceptance Criteria are satisfied.

No unresolved P0/P1/provider blocker remains.

Four Qwen and four Claude P2 findings remain non-blocking technical notes only.

No Release, Deployment, Production, or protected `codesho` action occurred.

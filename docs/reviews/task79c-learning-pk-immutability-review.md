# Task79C Learning Primary-Key Immutability Review

Task: `SPRINT1-DOMAIN-LEARNING-PRIMARY-KEY-IMMUTABILITY-HARDENING-79C`

Base: `ab30d93128183cd26691224b6ea0efe85ef0d6a7`

Status: `COMPLETE / QWEN PASS / CLAUDE PASS / MERGED / POST-MERGE GREEN`

## Review focus

- model-level persisted Course.id immutability;
- model-level persisted Lesson.id immutability;
- PostgreSQL direct UPDATE / QuerySet.update protection;
- migration ordering and reverse behavior;
- preservation of pre-existing immutable code/position trigger semantics;
- preservation of FORCE RLS, tenant policies, same-tenant Course/Lesson integrity, runtime role restrictions and DELETE/TRUNCATE denial;
- no schema-field expansion, API/OpenAPI/frontend expansion, learner linkage or PII activation.

## Qwen gate

Prompt: `QWEN_TASK79C_LEARNING_PRIMARY_KEY_IMMUTABILITY_REVIEW_01_V1`

HEAD reviewed: `6490599073d39043cf962569e497a716b5e3fbc0`

Result: `PASS`

- Content received complete: YES
- P0: 0
- P1: 0
- P2: 4
- Open blockers: 0
- Implementation recommendation: `READY_FOR_CLAUDE`

Non-blocking Qwen notes covered inherited composite-FK confirmation, an out-of-objective pk=None/_state.adding edge case, intentional reverse-migration weakening back to Task79B behavior, and exact-head CI/Compose revalidation.

## Claude hard gate

Prompt: `CLAUDE_TASK79C_LEARNING_PRIMARY_KEY_IMMUTABILITY_HARD_GATE_01_V1`

HEAD reviewed: `6490599073d39043cf962569e497a716b5e3fbc0`

Result: `PASS`

- Content received complete: YES
- Content verdict: PASS
- P0: 0
- P1: 0
- P2: 4
- Open blockers: 0
- Merge recommendation: `READY`
- Final marker: `TASK79C_REVIEW_COMPLETE`

Claude independently reviewed all seven exact files. It confirmed that migration 0002 binds the immutable triggers by function name, migration 0003 uses `CREATE OR REPLACE FUNCTION` without detaching those triggers, reverse restores the Task79B body, the Django model guard and PostgreSQL trigger close the intended primary-key mutation paths, QuerySet.update bypass is tested, and inherited RLS/FK/role/DELETE-TRUNCATE/search_path/scope invariants remain valid.

## Provenance

Reviewed implementation HEAD: `6490599073d39043cf962569e497a716b5e3fbc0`

Exact reviewed file/blob bindings:

- `backend/modules/learning/models.py` — `2ca14af4a83f9eb4518b6c73e3002fff22a0b07b`
- `backend/modules/learning/migrations/0003_primary_key_immutability.py` — `bc5b056f0ed94db6a6aa777c9992e01b60fe7ded`
- `backend/tests/test_learning_models.py` — `10743f3e2e3f827607a337ba29e5b832c05e0a55`
- `backend/tests/test_learning_rls_postgres.py` — `161fca97b3c27b3aab64a0fe1a116edd82210a4f`
- `docs/coordination/TASK79C_PRIMARY_KEY_HARDENING.md` — `89c53fcea5264ad902e0bc49a9cadf1b0ac1da3a`
- `docs/reviews/task79c-learning-pk-immutability-review.md` — `438068f160ff36822623e683e214561966c2aa99`
- inherited `backend/modules/learning/migrations/0002_tenant_rls.py` — `78aa08716b5aa180f160aafb83abde42dd17ebb2`

## Validation and merge

Pre-merge exact-head CI `31383517391`: `SUCCESS`.

Pre-merge exact-head Compose `31383517753`: `SUCCESS`.

PR `#33` was marked Ready only after both provider hard gates passed, then squash-merged race-safely with expected head SHA `6490599073d39043cf962569e497a716b5e3fbc0`.

Merged `main` commit: `5fb1bb0011bdcfced9308bc638851751283a7bde`.

Post-merge CI `31401335940`: `SUCCESS`.

Post-merge Compose smoke/restore `31401335885`: `SUCCESS`.

Post-merge evidence includes full backend success, frontend success, PostgreSQL RLS/connection-reuse success, and backup/restore success.

## Final verdict

`PASS / P0=0 / P1=0 / OPEN_BLOCKERS=0 / MERGED / POST-MERGE GREEN`

All remaining provider findings are P2 and non-blocking.

No Release, Deployment, Production, or protected `codesho` action occurred.

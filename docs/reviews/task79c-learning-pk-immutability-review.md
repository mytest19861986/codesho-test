# Task79C Learning Primary-Key Immutability Review

Task: `SPRINT1-DOMAIN-LEARNING-PRIMARY-KEY-IMMUTABILITY-HARDENING-79C`

Base: `ab30d93128183cd26691224b6ea0efe85ef0d6a7`

Status: `PROVIDER REVIEWS PENDING`

## Review focus

- model-level persisted Course.id immutability;
- model-level persisted Lesson.id immutability;
- PostgreSQL direct UPDATE / QuerySet.update protection;
- migration ordering and reverse behavior;
- preservation of the pre-existing immutable code/position trigger semantics;
- preservation of FORCE RLS, tenant policies, same-tenant Course/Lesson integrity, runtime role restrictions and DELETE/TRUNCATE denial;
- no schema-field expansion, API/OpenAPI/frontend expansion, learner linkage or PII activation.

## Qwen gate

Prompt: `QWEN_TASK79C_LEARNING_PRIMARY_KEY_IMMUTABILITY_REVIEW_01_V1`

Result: pending.

## Claude hard gate

Prompt: `CLAUDE_TASK79C_LEARNING_PRIMARY_KEY_IMMUTABILITY_HARD_GATE_01_V1`

Result: pending.

PASS requires `P0=0`, `P1=0`, `OPEN_BLOCKERS=0` and Claude merge recommendation `READY`.

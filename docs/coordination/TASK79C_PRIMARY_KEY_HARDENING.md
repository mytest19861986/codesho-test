# Task79C — Learning Primary-Key Immutability Hardening

Task: `SPRINT1-DOMAIN-LEARNING-PRIMARY-KEY-IMMUTABILITY-HARDENING-79C`

Base: `ab30d93128183cd26691224b6ea0efe85ef0d6a7`

Branch: `codex/task79c-learning-pk-immutability-hardening`

Status: `IMPLEMENTATION / VALIDATION PENDING`

## Objective

Close Claude Task79B's single non-blocking P2 by explicitly preventing mutation of persisted `Course.id` and `Lesson.id` values.

## Scope

Authorized changes are limited to:

- learning model-level immutable-id guards;
- a new forward migration that strengthens the existing PostgreSQL immutable-update trigger function;
- focused model and PostgreSQL tests;
- bounded Task79C coordination/review documentation.

No model fields, API/OpenAPI, frontend, learner/cohort/progress relationships, real-user PII, deployment, Release, Production, or protected `codesho` action is introduced.

## Invariants

1. A persisted Course primary key cannot be changed through model `save()`.
2. A persisted Lesson primary key cannot be changed through model `save()`.
3. PostgreSQL rejects direct/QuerySet UPDATE attempts that change Course.id.
4. PostgreSQL rejects direct/QuerySet UPDATE attempts that change Lesson.id.
5. Existing Course.code, Lesson.code and Lesson.position immutability remains unchanged.
6. Existing FORCE RLS, tenant isolation, same-tenant FK, runtime privileges and destructive-operation denial remain unchanged.
7. Migration reversal restores the exact Task79B trigger behavior without dropping existing triggers.

## Required gates

- focused model tests;
- PostgreSQL-focused tests;
- Ruff;
- MyPy;
- Django check;
- migration drift check;
- full backend suite;
- exact Diff audit;
- exact-head CI;
- exact-head Compose smoke/restore;
- Qwen adversarial review;
- mandatory Claude migration/security hard gate before merge.

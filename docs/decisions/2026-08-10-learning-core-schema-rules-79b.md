# Learning Core Schema + RLS — Task79B

Status: `IMPLEMENTATION / SYNTHETIC-ONLY / NO-API`

Base: `30dfe7e94e39edb20d65a3e2d5b382162cdd5e56`

## Authorized scope

Task79B implements only tenant-owned `Course` and `Lesson` catalog structure. It does not introduce cohorts, memberships, learner linkage, progress, assignments, sessions, submissions, analytics, AI fields, API endpoints, OpenAPI operations, or frontend behavior.

Real-user PII activation and legally pending cohort/progress/retention decisions remain out of scope. Validation uses synthetic/internal data only.

## Schema bounds

`Course` fields: UUID id, tenant FK, immutable code (`max_length=64`), title (`max_length=160`), state (`draft|published|archived`), created/updated UTC timestamps.

`Lesson` fields: UUID id, tenant FK, protected course FK, immutable code (`max_length=64`), title (`max_length=160`), immutable positive position, state (`draft|published|archived`), created/updated UTC timestamps.

Required uniqueness:

- Course: `(tenant, code)` and `(tenant, id)`.
- Lesson: `(tenant, course, code)` and `(tenant, course, position)`.

The `(tenant, id)` course uniqueness exists specifically to support the PostgreSQL same-tenant composite foreign key from lesson.

## Tenant isolation

The learning tables reuse the existing transaction-local `app.tenant_id` context. PostgreSQL enables and forces RLS on both tables. Policies use the existing fail-closed `current_setting('app.tenant_id', true)` comparison for both `USING` and `WITH CHECK`.

No second tenant context or client-supplied tenant authority is introduced.

`Lesson(tenant_id, course_id)` additionally references `Course(tenant_id, id)` at database level, so cross-tenant lesson/course linkage is invalid even if application validation is bypassed.

## Immutable identifiers

Course code, lesson code, and lesson position are guarded in the Django model and additionally by PostgreSQL update triggers. This prevents direct queryset updates from mutating stable identifiers on PostgreSQL.

Full content versioning is intentionally deferred. Task79B adds no body/content field and therefore does not create an unsupported publication mutation workflow.

## Module boundary amendment

The repository module-boundary gate previously knew only identity/platform modules. Task79B adds exactly one dependency edge:

`learning -> platform_tenant`

No dependency on identity, platform_event, config services, API code, or frontend is opened.

## Migration strategy

`0001_initial` creates portable Django schema/constraints/indexes.

`0002_tenant_rls` applies PostgreSQL-only guards:

- ENABLE/FORCE RLS for Course and Lesson;
- tenant isolation policies;
- same-tenant composite FK;
- immutable-key triggers.

The reverse function exists for migration-framework reversibility, but operational rollback remains forward-only and non-destructive.

No data migration or backfill exists.

## Future API bounds

Task79B creates no API. For the later learning read API task:

- proposed default page size: 20;
- mandatory maximum page size: 50.

These values are architecture acceptance inputs only and do not alter global pagination settings here.

## Deferred decisions

The following remain explicitly deferred:

- ClassCohort / ClassMembership;
- LessonProgress and its append-only/write authority contract;
- assignment/session/submission models;
- XP/rank/streak/recommendation/attention/analytics;
- seventh canonical OpenAPI operation;
- real-user cohort/progress retention and erasure semantics.

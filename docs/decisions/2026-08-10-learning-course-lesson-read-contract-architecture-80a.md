# Learning Course/Lesson Read Contract Architecture — Task80A

Status: `ARCHITECTURE_ONLY / IMPLEMENTATION_NOT_AUTHORIZED`

Date: 2026-08-10

Task: `SPRINT1-DOMAIN-LEARNING-COURSE-LESSON-READ-CONTRACT-ARCHITECTURE-80A`

Base: `f96733da69e42df3fe8ea8710ec1e9a0f81d91a2`

## Purpose

Define the smallest truthful read-only contract for exposing the already-implemented tenant-scoped `Course` and `Lesson` catalog in a later, separately authorized implementation task.

This architecture task changes documentation only. It does not add endpoints, serializers, URLs, OpenAPI operations, migrations, models, fixtures, frontend behavior, learner/cohort/progress relations, real-user capability, Release, Deployment, Production, or protected `codesho` actions.

## Existing authoritative source

The database source of truth is the existing Task79B/79C learning schema:

- `Course`: opaque UUID, tenant, immutable stable code, bounded title, publication state, timestamps.
- `Lesson`: opaque UUID, tenant, course, immutable stable code, immutable positive position, bounded title, publication state, timestamps.
- PostgreSQL enforces same-tenant Lesson→Course integrity.
- Both tables use `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`.
- Runtime role must not be superuser or `BYPASSRLS`.
- Missing tenant context fails closed.

No learner-specific progress, cohort membership, assignment, session, ranking, analytics, or AI source exists in this scope.

## Authorized future read surface

A later implementation task may propose exactly these two read-only operations:

1. `GET /api/v1/learning/courses/`
2. `GET /api/v1/learning/courses/{course_id}/lessons/`

These paths are architecture proposals only. Task80A does **not** modify the canonical `docs/openapi.yaml` or runtime URL configuration.

No POST, PUT, PATCH, DELETE, bulk, export, search, progress, enrollment, cohort, or aggregate-dashboard operation is authorized by this ADR.

## Authorization boundary

A future implementation must reuse existing authority rather than inventing a new one:

1. Tenant comes from the validated request/session tenant boundary, never from a learner-supplied tenant identifier.
2. Tenant context is established transaction-locally before tenant-owned queries.
3. Existing active tenant membership remains the admission boundary.
4. The learner may read only data visible under the current tenant's RLS policy.
5. Missing tenant context, inactive tenant, inactive/invalid tenant membership, unauthorized role, or tenant mismatch fails closed.
6. No platform-wide or cross-tenant catalog read is implied.

Task80A does not authorize new membership state, role state, learner identity, or real-user activation.

## Course list contract

Future route proposal:

`GET /api/v1/learning/courses/`

### Visibility

Return only `Course` rows where:

- the row is visible through the current tenant RLS context; and
- `state = published`.

Draft and archived courses are not learner-visible through this contract.

### Resource shape

Each course item contains only:

- `id`: opaque UUID string;
- `code`: immutable stable course code;
- `title`: bounded display title;
- `state`: literal `published`.

Do not expose:

- `tenant_id` or tenant metadata;
- created/updated timestamps;
- audit metadata;
- author/staff identity;
- internal publication history;
- learner progress;
- cohort/enrollment information;
- counts inferred from unavailable relations.

### Ordering

Deterministic ascending ordering:

1. `code` ascending;
2. `id` ascending as a stable tie-breaker.

Although tenant+code is unique, the explicit UUID tie-breaker keeps the ordering contract deterministic if future projection logic changes.

## Lesson list contract

Future route proposal:

`GET /api/v1/learning/courses/{course_id}/lessons/`

### Parent authorization

The parent `Course` must itself be visible under the Course contract:

- same current tenant/RLS context;
- `state = published`.

A hidden, draft, archived, missing, or cross-tenant course must not leak existence through distinguishable response content.

### Visibility

Return only lessons where:

- `lesson.course_id = {course_id}`;
- row is visible through current tenant RLS context;
- `lesson.state = published`.

Draft and archived lessons are excluded.

### Resource shape

Each lesson item contains only:

- `id`: opaque UUID string;
- `code`: immutable stable lesson code;
- `title`: bounded display title;
- `position`: positive immutable ordering integer;
- `state`: literal `published`.

Do not expose tenant identifiers, timestamps, internal audit data, progress, assignments, submissions, instructor notes, provider output, or analytics.

### Ordering

Deterministic ascending ordering:

1. `position` ascending;
2. `code` ascending;
3. `id` ascending.

The schema already guarantees unique `(tenant, course, position)`; secondary keys remain an explicit defensive ordering contract.

## Pagination contract

Both collection operations must be bounded.

Architecture default:

- default page size: `20`;
- maximum page size: `100`;
- client may request a smaller positive page size only;
- values above `100`, zero, negative, non-integer, or otherwise invalid values must be rejected or normalized according to one explicitly documented implementation choice before coding.

The implementation task must choose one pagination mechanism already compatible with repository conventions and pin it in OpenAPI/tests. Task80A does not authorize a new dependency.

A response must never become unbounded if the client omits pagination input.

## Empty, unavailable, and not-found semantics

- A tenant with no published courses receives an empty collection, not fabricated placeholder data.
- A visible course with no published lessons receives an empty lesson collection.
- A parent course that is missing or not learner-visible must use a non-enumerating not-found response in the future implementation contract.
- Cross-tenant identifiers must not reveal whether an object exists in another tenant.
- There is no `progress`, `completion`, `next lesson`, XP, rank, streak, recommendation, or at-risk field in these responses.

## Caching and consistency

Task80A authorizes no cache.

A future implementation must read from the authoritative PostgreSQL source under the current tenant transaction context unless a separately reviewed cache design preserves tenant isolation and publication semantics.

ETag, conditional requests, CDN caching, shared cache keys, and stale-while-revalidate behavior are deferred.

## Error/security contract for future implementation

The implementation task must pin exact status/body semantics, but architecture invariants are:

- unauthenticated request: fail closed using existing auth/session contract;
- invalid/inactive membership or unauthorized role: fail closed without data;
- absent tenant context: no tenant rows;
- cross-tenant object id: no existence disclosure;
- malformed UUID: bounded validation failure, no database error leakage;
- invalid pagination: bounded client error or explicitly normalized safe default;
- no traceback, SQL detail, tenant identifier, cookie, secret, audit metadata, or raw exception in responses/logs.

## OpenAPI proposal boundary

A later implementation task must update the canonical OpenAPI projection only after a separate hard gate.

That task must define:

- exactly the two GET paths above;
- bounded pagination parameters;
- exact course/lesson resource schemas;
- empty collection behavior;
- authentication/authorization error schemas;
- non-enumerating parent-not-found semantics;
- no write operation;
- no cohort/progress/learner endpoint.

The current canonical six approved operations remain unchanged by Task80A.

## Required tests for the implementation successor

### Tenant isolation

- missing tenant context returns no learning rows;
- current tenant cannot read another tenant's courses;
- current tenant cannot read another tenant's lessons;
- cross-tenant parent `course_id` does not disclose existence;
- connection reuse does not leak prior tenant context.

### Authorization

- unauthenticated request fails closed;
- inactive/invalid tenant membership fails closed;
- authorized active membership can read published catalog data only;
- no request-supplied tenant id can override tenant authority.

### Publication visibility

- published course is visible;
- draft course is not visible;
- archived course is not visible;
- published lesson under published course is visible;
- draft/archived lesson is not visible;
- published lesson under non-visible course is not reachable.

### Response bounds

- resource fields are exact and do not leak tenant/timestamp/internal fields;
- ordering is deterministic;
- default pagination is bounded;
- maximum page size is `100`;
- empty database/empty tenant returns a truthful empty result;
- malformed UUID and invalid pagination are bounded and deterministic.

### Contract integrity

- future generated OpenAPI is deterministic and byte-equal to the committed canonical schema;
- only explicitly approved new operations appear;
- existing runtime auth/session/CSRF/cookie behavior remains unchanged;
- frontend remains unchanged unless separately authorized.

## Mandatory hard gate before runtime implementation

Because the successor would change authorization-visible API behavior, implementation requires a separate Task and mandatory Claude review covering:

- tenant authority and RLS use;
- active membership authorization;
- object enumeration risk;
- pagination bounds;
- serializer field minimization;
- OpenAPI expansion;
- preservation of existing auth/session/CSRF behavior.

Qwen may independently challenge the proposal before Claude.

## Explicit exclusions

Task80A does not authorize:

- runtime Python/TypeScript changes;
- migrations or SQL;
- RLS or grants changes;
- `docs/openapi.yaml` changes;
- frontend changes;
- `ClassCohort` / `ClassMembership` implementation;
- `LessonProgress` implementation;
- learner-specific academic state;
- assignment/session/submission work;
- real-user activation or PII expansion;
- Release, Deployment, Production, Alpha activation, or protected `codesho` promotion.

## Successor recommendation

If Task80A passes review, the next separately authorized implementation slice should implement only the two Course/Lesson GET contracts with exact OpenAPI schemas and negative authorization/RLS tests.

Cohort membership and progress remain blocked pending their explicit product/legal/source-of-truth dispositions.

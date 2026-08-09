# Learning Domain Read Model Architecture — Task79A

Status: `ARCHITECTURE_ONLY / CONTRACT_PENDING / IMPLEMENTATION_NOT_AUTHORIZED`

Date: 2026-08-10  
Base: `cb0a09df5e566dd14be329d22333fd16c82d6378`  
Task: `SPRINT1-DOMAIN-LEARNING-READ-MODEL-ARCHITECTURE-79A`

## Decision summary

Define a small, tenant-scoped learning read model for a later implementation
task. The first implementation should establish only the authoritative
entities needed to render a truthful learner dashboard: `Course`, `Lesson`,
`ClassCohort`, `ClassMembership`, and an append-only or otherwise
contract-defined `LessonProgress` projection. `Assignment`, `ClassSession`,
and submission summaries remain optional follow-up slices unless a concrete
source of truth and product owner approve them.

The model is a read contract, not a license to synthesize academic data. A
field with no authoritative source remains unavailable/null. XP, rank, streak,
recommendations, at-risk indicators, AI attention, and analytics aggregates
are explicitly deferred.

## Current evidence and boundary

The current authenticated session contract provides only an opaque user id,
username, tenant id, tenant slug, and role. The existing dashboard has no
backend learning endpoint or academic source of truth; its academic values
are intentionally unavailable. Existing tenant middleware resolves the tenant
from the host and establishes database context inside `tenant_atomic` before
tenant queries. Existing tenant membership is the authoritative admission
boundary, not a course/class mapping.

This decision creates no model, migration, endpoint, serializer, OpenAPI
operation, RLS policy, fixture, backfill, or frontend behavior.

## Minimum V1 domain

### Course

An author-controlled learning product within one tenant. Required future
fields: opaque UUID, tenant foreign key, immutable stable code, bounded title,
publication state, and UTC timestamps. A course is not a class, cohort, user
profile, or progress record. Publication and title mutation rules require a
separate content decision; published content must remain immutable under the
repository rules.

### Lesson

An ordered unit belonging to exactly one course. Required future fields:
opaque UUID, tenant foreign key, course foreign key, immutable ordering key,
bounded title, publication state, and UTC timestamps. Cross-tenant course or
lesson references must be rejected by database constraints or a transaction-
local invariant, not by a UI check.

### ClassCohort

A tenant-scoped teaching grouping that may be associated with courses through
an explicitly approved relationship. It is not an academic result and does
not imply that every member has completed a lesson. Names, dates, and status
need bounded contracts and privacy review before implementation.

### ClassMembership

A tenant-scoped relation between an existing user and a cohort. It must use
the existing user and tenant membership boundaries; it must not create an
alternate identity or infer a learner from a dashboard username. Active
membership, role eligibility, tenant equality, uniqueness, and revocation
semantics require explicit database and authorization tests.

### LessonProgress

A learner-to-lesson read projection only after a source-of-truth write
contract is approved. Minimum safe identity is tenant, existing user, lesson,
bounded state, and UTC transition timestamps. Completion must not be inferred
from page views or fabricated from fixture data. If progress provenance or
write semantics are not approved, the dashboard returns unavailable rather
than creating this projection.

## Deferred or conditional entities

`Assignment`, `AssignmentSubmission`, and `ClassSession` are not part of the
minimum V1 read model. They may be added only with an approved source of truth,
privacy classification, lifecycle/immutability rules, tenant invariants, and
an explicit API contract. A submission summary must not expose child data,
free text, evidence, or provider responses.

## Authority and tenant invariants

1. Resolve tenant from the existing validated request/session boundary; never
   accept a tenant id supplied by a learner as authority.
2. Establish tenant context inside `transaction.atomic()` before any
   tenant-owned query, preserving `FORCE ROW LEVEL SECURITY` and runtime role
   restrictions.
3. Every tenant-owned row has exactly one tenant. Cross-tenant foreign-key
   pairs are rejected; application-side filtering is not sufficient.
4. A learner may read only rows reachable through the current tenant and an
   active existing `TenantMembership`; class membership is an additional
   relationship, not a replacement for tenant membership.
5. Missing tenant context, inactive tenant, inactive membership, mismatched
   tenant references, and unauthorized role fail closed.
6. No aggregate, cache, export, or endpoint may combine tenants without a
   separately approved platform scope and explicit privacy contract.

## Read-model shape

Prefer bounded resource projections over one broad aggregate endpoint:

- `GET /api/v1/learning/courses/` — published courses visible to the current
  learner, with bounded pagination.
- `GET /api/v1/learning/courses/{course_id}/lessons/` — published lessons for
  one visible course.
- `GET /api/v1/learning/lessons/{lesson_id}/progress/` — the current learner's
  progress only, if a write/source contract exists.

These paths are a proposal, not an authorized API change. An aggregate
dashboard endpoint is not justified yet: it would couple publication,
membership, progress, assignments, sessions, and privacy decisions and would
make partial/unavailable data harder to represent safely.

## Fields that must not exist in V1

Do not add XP, rank, streak, recommendations, at-risk indicators, AI-derived
attention, behavioral analytics, engagement scores, or synthetic progress
numbers merely to fill existing dashboard cards. No field may be a numeric
placeholder for an absent contract. `null`/unavailable is the correct state.

## RLS, migration, and rollback proposal

The successor implementation must use forward-only migrations owned by the
approved migrator role. Each tenant-owned table must receive explicit enable
and force-RLS policy coverage, same-tenant foreign-key protection, runtime
grant checks, and negative connection-reuse tests. Migration order should be:

1. immutable/reference content tables and constraints;
2. cohort and membership relation;
3. progress projection only after its source-of-truth decision;
4. read serializers/views and OpenAPI projection;
5. empty-database and restore verification.

Rollback is forward-only operational rollback: stop exposing the new read
contract, deploy a compatible application version, and retain immutable
published/audit data. No destructive down migration, backfill, or delete
policy is implied. Retention, erasure, aging-out, and legal hold remain
`LEGAL_PENDING`.

## API, privacy, and security contract proposal

The successor task must define schemas in OpenAPI before implementation,
including unavailable/empty states, pagination, authorization failures, and
tenant mismatch behavior. It must not expose tenant names, private class
notes, child data, raw submissions, audit metadata, cookies, secrets, or raw
provider responses. IDs are opaque and non-semantic. Published content,
consent, evidence, receipts, and audit records remain immutable.

The legal review must decide whether learner-to-cohort linkage, progress
retention, deletion/erasure, and class-session history are permitted. No
retention period or real-user readiness is inferred here.

## Test strategy for the successor implementation task

Required evidence includes:

- migration-from-empty-database and restore checks;
- tenant context absence, inactive tenant, cross-tenant row, and connection
  reuse negatives;
- active/inactive membership and role authorization negatives;
- same-tenant relationship and uniqueness constraints;
- published versus unpublished content visibility;
- progress unavailable/null behavior when no source exists;
- pagination, object authorization, and bounded response-field checks;
- deterministic OpenAPI parity and no unapproved endpoint exposure;
- no sensitive values in logs, audit metadata, fixtures, or raw responses.

## Implementation sequencing

1. Obtain product/legal disposition for cohort membership and progress
   authority.
2. Produce an exact schema/constraint/RLS ADR and OpenAPI proposal.
3. Run mandatory Claude hard gate for schema, tenant isolation, privacy, and
   authorization risk.
4. Implement migrations and backend read contracts in a new authorized task.
5. Add focused negatives, full gates, Compose restore evidence, and a second
   exact-head review before any Ready/Merge decision.

## Explicit exclusions

No runtime product code, migration, SQL, RLS change, endpoint, OpenAPI file,
frontend change, fixture, dependency, workflow, Compose change, deployment,
release, Alpha activation, Production action, real-user capability, or
protected `codesho` promotion is authorized by Task79A.

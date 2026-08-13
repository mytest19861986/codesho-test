# Task81A authoritative contract context

## Data flow and ownership

The authoritative source is tenant-scoped PostgreSQL Course and Lesson catalog data. Tenant comes from the validated request/session tenant boundary, never from a learner-supplied tenant identifier. Tenant context is established before tenant-owned queries; active tenant membership is the admission boundary. Next.js reads the REST API and never accesses PostgreSQL directly. No learner progress, cohort, ranking, analytics, or AI metric is part of this contract.

## Contract types and validation boundary

```text
CourseItem = { id: opaque UUID string, code: string, title: string, state: "published" }
LessonItem = { id: opaque UUID string, code: string, title: string, position: positive integer, state: "published" }
CourseResults = { results: CourseItem[] }
LessonResults = { results: LessonItem[] }
```

The boundary accepts only bounded pagination (`page` positive, `page_size` positive and at most 100), validates course identifiers as UUID-like values, and returns only the fields above. No tenant identifier, timestamp, audit field, progress, cohort, completion, ranking, or provider output is serialized.

## State machine

The UI states are: `session-loading`, `unauthenticated`, `courses-loading`, `courses-empty`, `courses-ready`, `lessons-loading`, `lessons-empty`, `lessons-ready`, `parent-not-found`, `forbidden-or-boundary`, `invalid-request`, `recoverable-error`, and `stale-session`. A late response after session generation or course selection changes is ignored. Course selection clears the previous lesson view before loading the new parent.

## Authentication, session, and caching

Unauthenticated and inactive/invalid membership requests fail closed. Same-origin credentials are used for the REST request. Session generation and AbortController guards prevent an old response from repopulating a newer session or selection. No shared cache or tenant-agnostic cache key is authorized.

## Error matrix and security invariants

Malformed, missing, draft, archived, or cross-tenant parent identifiers use the same non-enumerating `404 {"code":"not_found"}` contract. Invalid pagination is a bounded `400 {"code":"invalid_pagination"}`. Empty visible collections are truthful `{ "results": [] }`. Responses expose no tenant identity, hidden-row status, learner metrics, secrets, cookies, or raw exceptions. Course and lesson ordering is deterministic and result cardinality is bounded.

# Student Dashboard Learning Read Integration Architecture — Task81A

Status: `ARCHITECTURE_ONLY / IMPLEMENTATION_NOT_AUTHORIZED`

Date: 2026-08-11

Task: `SPRINT1-UI-LEARNING-DASHBOARD-READ-INTEGRATION-ARCHITECTURE-81A`

Base: `29b1b4d03f2043f9a45bd791b4af26260fa71c55`

## Context

The repository contains a merged Student Dashboard foundation and a merged,
tenant-safe Course/Lesson read API. This task defines how a later Task81B may
connect them. It does not implement the connection, change runtime behavior,
or authorize a new API, dependency, cache, service, or learner data source.

## Current repository facts

- `frontend/src/app/dashboard/page.tsx` renders
  `DashboardDataBoundary`.
- `DashboardDataBoundary.tsx` is a client component. It calls the existing
  `getSession()` boundary, renders loading until the session resolves, renders
  the existing error state for a failed session, and currently creates a
  typed placeholder `DashboardModel` for a valid session.
- `authClient.ts` parses the authenticated session fail-closed and uses
  `credentials: "same-origin"`. The session contract contains user and tenant
  identity for display/admission context; the frontend must never use tenant
  identity as an authorization parameter.
- `DashboardScreen.tsx` owns the visual shell and currently receives a model
  prop. Its fixture is the default for presentational/test use, while the
  data boundary does not import or render the fixture.
- `loading.tsx` and `error.tsx` reuse the same DashboardScreen states.
- Existing UI tests cover the session boundary, fail-closed parsing,
  same-origin credentials, fixture isolation, semantic landmarks, and state
  announcements. No implementation test in this task is authorized.
- `frontend/package.json` has no approved data-fetching or runtime validation
  dependency beyond the existing Next/React/TypeScript platform.
- The authoritative backend contract is:
  `GET /api/v1/learning/courses/` and
  `GET /api/v1/learning/courses/{course_id}/lessons/`.
- Both responses are `{ "results": [...] }`. They expose only the fields in
  the committed OpenAPI schemas. Pagination accepts `page` and `page_size`,
  with defaults 1 and 20 and maximum page size 100; there is no count, total,
  next, previous, or page-count metadata.
- Courses and lessons are published-only, tenant-scoped, and ordered by the
  backend contract. A hidden/missing/cross-tenant course parent returns the
  same not-found semantics for the lesson route.
- Task80B's implementation and OpenAPI contract are authoritative at this
  exact base. Task80B P2 items remain
  `NON_BLOCKING_FUTURE_HARDENING`; Task81A must not resolve them.

## Goals

1. Define a minimal, typed, same-origin read path from Dashboard to the two
   existing APIs.
2. Preserve server-side authentication, tenant admission, RLS, and
   non-enumerating parent semantics.
3. Define honest loading, empty, recoverable-error, auth-failure, and
   parent-not-found behavior without fabricating learner state.
4. Propose the smallest exact Task81B implementation allow-list and test
   strategy.

## Non-goals and prohibitions

This task does not implement frontend fetching, change backend/API/OpenAPI,
modify models/migrations/RLS, add dependencies, add progress/XP/rank/streak,
infer enrollment/cohort/attendance/assignments, add analytics or caching, or
change styling. Release, Deployment, Production, Alpha, and protected
`codesho` actions are forbidden.

## Data flow and ownership

The later implementation should keep the existing client-side Dashboard
boundary as the owner of interactive course selection and lesson loading:

```text
DashboardDataBoundary
  -> existing getSession() same-origin admission check
  -> bounded learning data-access module
  -> GET /api/v1/learning/courses/?page=1&page_size=20
  -> selected course.id (UI state only)
  -> GET /api/v1/learning/courses/{course.id}/lessons/?page=1&page_size=20
  -> typed DashboardScreen view model
```

The data-access module owns URL construction, `credentials: "same-origin"`,
response status classification, minimal response validation, and bounded
pagination. The component owns selection and presentation state. No browser
request may include a tenant ID, tenant slug, role, or alternate authority.

Do not introduce a server-side BFF, Redux, React Query, SWR, websocket,
GraphQL layer, Redis cache, or a new service. A small module using the existing
platform `fetch` is the approved default.

## Contract types and validation boundary

Task81B should define narrow types equivalent to:

```ts
type CourseItem = { id: string; code: string; title: string; state: "published" };
type LessonItem = {
  id: string; code: string; title: string; position: number; state: "published";
};
type CourseResults = { results: CourseItem[] };
type LessonResults = { results: LessonItem[] };
```

The implementation must validate object shape, required strings, UUID-like
IDs according to the repository's lightweight convention, `state ===
"published"`, and positive lesson positions before rendering. It must reject
malformed or unexpected payloads as recoverable data errors. It must not use
`any`, deserialize extra fields into the view model, or trust `code` as
identity when `id` is present.

## State machine

The later implementation must distinguish these states:

| State | Meaning | UI rule |
| --- | --- | --- |
| `session-loading` | Existing session request pending | Reuse the existing loading state. |
| `unauthenticated` | Session is absent/invalid or API returns 401 | Show auth/session recovery, never “no courses”. |
| `courses-loading` | Course request pending | Announce loading and preserve no stale tenant data. |
| `courses-empty` | Valid response with `results: []` | Show truthful empty learning state. |
| `courses-ready` | At least one validated course | Select by opaque `id`; show only contract fields. |
| `lessons-loading` | Selected course lesson request pending | Announce loading and keep course identity UI-only. |
| `lessons-empty` | Valid lesson response with no results | Show truthful empty lesson state. |
| `lessons-ready` | Valid lessons exist | Render code/title/position/state only. |
| `parent-not-found` | Lesson request returns 404 | Clear selected parent/lessons and explain it may no longer be visible. |
| `forbidden-or-boundary` | 403 or admission boundary failure | Show unavailable/permission-safe recovery, no backend body dependency. |
| `invalid-request` | 400 from locally invalid pagination/request | Treat as bounded client-contract error and recover safely. |
| `recoverable-error` | Network, 5xx, malformed payload | Show retryable generic error, no traceback or raw response. |
| `stale-session` | Session changes or request becomes unauthorized | Clear course/lesson data before re-admission. |

The component must ignore late responses after selection/session changes and
must not display data from a previous user or tenant. Back/forward navigation,
reload, and tab restoration must re-enter through the same session boundary.

## Pagination UX

V1 should request page 1 with page size 20 and expose only bounded incremental
navigation or “load more” when the product needs more rows. It must never show
total pages or pretend that an absent `next` field exists. Page numbers must
be locally bounded and never be generated from untrusted user input without a
small positive upper bound. The client must not request arbitrarily huge page
values or page sizes. A future pagination hardening change belongs to the
backend backlog, not Task81A.

## Course selection and URL semantics

Selection identity is `course.id`. `code` and title are display fields only.
Task81B should keep selection in component state unless inspection proves an
existing dashboard navigation convention requires a query parameter. If a
query parameter is used, it is UI state only, must be validated as an opaque
course ID, must not be tenant authority, and must be cleared when the course
is not returned or the lesson parent is 404.

## Authentication, session, and caching

Reuse `getSession()` and the existing same-origin cookie behavior. Do not add
tokens, localStorage/sessionStorage credentials, Authorization-header
invention, or a second auth protocol. Do not cache responses in a shared
client or server cache. If browser navigation restores the page, the data
boundary must revalidate session and learning data so one user's/tenant's
response cannot be reused for another. Auth errors must be classified by
status, not by undocumented middleware body fields; the actual 401/403 body
may differ from the generic OpenAPI Error schema.

## Error matrix

| Response | Required frontend disposition |
| --- | --- |
| 200 | Validate exact envelope and render truthful data. |
| 400 | Bounded request/pagination error; do not silently invent totals. |
| 401 | Session/auth recovery; never empty-state substitution. |
| 403 | Generic unavailable/permission-safe state; do not parse undocumented fields. |
| 404 lesson parent | Clear selection and show parent-not-found recovery. |
| 5xx/network | Generic retryable error; do not expose internal details. |
| malformed 2xx payload | Recoverable contract error; do not render partial data. |

## Security and privacy invariants

- Tenant authority comes only from the existing validated server/session and
  backend tenant transaction/RLS boundary.
- No request-supplied tenant field, frontend tenant state, or URL query value
  can authorize a read.
- No cross-tenant existence or hidden-parent information is displayed.
- No progress, completion, XP, rank, streak, cohort, enrollment, attendance,
  due assignment, recommendation, AI insight, or lock state is inferred.
- No PII beyond the existing authenticated display name is added.
- No raw cookies, secrets, backend error bodies, SQL details, or provider data
  are logged or rendered.

## Accessibility and RTL requirements

Preserve the existing semantic landmarks and keyboard navigation. Course
selection must have a labelled control and visible focus state. Loading and
recoverable errors must use appropriate status/live announcements without
duplicated noisy announcements. Empty and not-found states need clear Persian
RTL copy, logical heading order, and no horizontal overflow at existing
supported breakpoints. Unsupported metrics remain visibly unavailable or
hidden, never misleadingly zero.

## Task81B proposed implementation allow-list

This is a proposal, not authorization. A separate Commander task must approve
the exact paths before implementation. The likely minimal allow-list is:

- `frontend/src/features/dashboard/DashboardDataBoundary.tsx`
- `frontend/src/features/dashboard/DashboardScreen.tsx`
- `frontend/src/features/dashboard/DashboardState.tsx`
- `frontend/src/features/dashboard/dashboard.types.ts`
- one new repository-consistent learning data-access/types module under
  `frontend/src/features/learning/` or the existing dashboard feature;
- focused dashboard contract and accessibility tests only.

No backend file, OpenAPI file, dependency manifest, auth protocol, or styling
file should be required. If inspection during Task81B finds a genuine backend
contract defect, stop and escalate instead of expanding the allow-list.

## Successor test strategy

Task81B should test, at minimum, typed parsing of valid/empty/malformed
CourseResults and LessonResults; same-origin credentials and no tenant query;
401/403/404/400/5xx/network mapping; course selection by ID; clearing after
404/session change; bounded pagination; no fabricated learner metrics; loading,
empty, error, keyboard, RTL, heading, focus, and live-region behavior; and no
cross-tenant/shared-cache state reuse. Existing auth contract tests remain
authoritative and must continue to pass.

## Risks and rejected alternatives

The main risks are confusing 401/403 with an empty catalog, treating an
untrusted course ID or tenant field as authority, inventing pagination totals,
and allowing stale client state across session changes. A new data-fetching
framework, BFF, shared cache, GraphQL endpoint, or backend aggregation was
rejected because it increases authority and deployment surface without being
required by the current contract.

## Acceptance Criteria

- Exact base `29b1b4d…` is inspected and recorded.
- Current Dashboard, auth/session, tests, OpenAPI, and Task80A/80B evidence are
  inspected from that base.
- Data flow, fetching ownership, typed contract, state machine, pagination,
  selection, auth/session, error, privacy, accessibility, and performance
  boundaries are explicit.
- Unsupported learner metrics are not made real or inferred.
- A minimal Task81B allow-list and successor test strategy are proposed.
- Gemini advisory, Qwen independent architecture, and Claude hard-gate review
  sequence is specified. No provider result may be fabricated.
- This task changes no runtime code, tests, API, OpenAPI, dependency,
  migration, workflow, Compose, release, deployment, production, Alpha, or
  protected `codesho` artifact.

## Provider review checklist

Gemini advisory review should cover Persian/RTL learner UX, honest empty/error
states, pagination without totals, responsive/accessibility continuity, and
unsupported metrics. Qwen must independently challenge session/tenant
authority, caching, URL-state confusion, pagination, contract drift,
fabricated learner state, dependencies, and test gaps. Claude must receive this
complete ADR, exact inspection evidence, Gemini's complete response, and
Qwen's complete response before its architecture hard gate. Required Qwen and
Claude PASS criteria are `CONTENT_RECEIVED_COMPLETE=YES`, `P0=0`, `P1=0`, and
`OPEN_BLOCKERS=0`; no Task81B implementation is authorized before real Claude
PASS and a separate Commander implementation task.

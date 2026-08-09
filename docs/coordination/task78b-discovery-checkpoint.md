# Task78B discovery checkpoint

## Scope

`SPRINT1-UI-STUDENT-DASHBOARD-DATA-CONTRACT-78B` starts from
`origin/main` at merge commit `12617e74845778280897bbebd76f0817056d9096`.
The work is isolated on branch `codex/task78b-student-dashboard-data-contract`.

## Findings

- The Dashboard UI currently renders `dashboardFixture` through
  `DashboardScreen`; it has no network/data-client boundary.
- The backend currently exposes the read-only session contract at
  `/api/v1/auth/session/`, returning authenticated user identity and the
  resolved tenant membership.
- No backend model or endpoint for course progress, lessons, assignments,
  recommendations, or scheduled sessions exists in the current tree.
- `TenantTransactionMiddleware` resolves the tenant from the subdomain and
  checks active membership inside `tenant_atomic` before non-preauth views.
- The existing session/auth contract is session-cookie based and follows the
  existing CSRF/session policy; the frontend auth client uses same-origin
  credentials.

## Commander disposition and implementation boundary

Commander confirmed that the current backend has no learning-domain module and
that 78B must remain limited to the existing read-only session contract. New
course/progress/assignment/session domain models, migrations, or endpoints are
deferred to a separately reviewed task.

The implementation therefore adds a client-side data boundary that reads
`/api/v1/auth/session/` with same-origin credentials and uses the authenticated
username and tenant slug for the identity surface. The session response is
runtime-parsed and incomplete or malformed payloads fail closed. Academic
fields that are not represented by the current backend contract render an
explicit unavailable state; the fixture is not imported into the authenticated
runtime path. Session failure renders the existing error state.

## Remediation checkpoint

The pre-Claude review recorded `CHANGES_REQUIRED` for synthetic academic data
in the authenticated ready model and incomplete session validation. Both were
remediated in the follow-up commit. The versioned hard-gate prompt remains
`CLAUDE_TASK78B_AUTH_SESSION_DATA_BOUNDARY_HARD_GATE_01_V1`; Claude PASS with
P0=0, P1=0, and OPEN_BLOCKERS=0 is required before merge.

Because this touches the authentication/tenant boundary, Claude hard-gate
review is required before merge. No product code was changed before this
disposition was observed.

## Safety

No protected `codesho`, Release, Deployment, Production, migration, or API
mutation was performed.

## Current handoff state

Implementation HEAD is now `346a306` on the pushed
`codex/task78b-student-dashboard-data-contract` branch. Focused tests (7/7),
ESLint, TypeScript, Next production build, and `git diff --check` are green.
The required Claude verdict for
`CLAUDE_TASK78B_AUTH_SESSION_DATA_BOUNDARY_HARD_GATE_01_V1` has not been
received, and the shared Commander browser session is unavailable; therefore
the branch remains unmerged and no protected action is authorized.

The Commander precheck then identified three P1 blockers: tenant was shown as
a class label, unavailable academic values were represented by zeroes, and
parser behavior was only source-tested. These are remediated in the current
implementation: tenant is no longer mapped to a class field, unavailable
numeric fields are nullable and rendered as unavailable, and behavioral tests
exercise valid, malformed, incomplete, wrong-type, and non-2xx session cases.

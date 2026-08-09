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
username for the existing Dashboard identity surface. The existing typed
fixture remains the explicitly bounded presentation source for fields that are
not represented by the current backend contract; it is not promoted to a
claimed real domain payload. Session failure renders the existing error state.

Because this touches the authentication/tenant boundary, Claude hard-gate
review is required before merge. No product code was changed before this
disposition was observed.

## Safety

No protected `codesho`, Release, Deployment, Production, migration, or API
mutation was performed.

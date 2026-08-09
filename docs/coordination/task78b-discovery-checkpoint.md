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

## Decision pending

The endpoint path, response schema, and mapping for the Dashboard data
contract must be confirmed by Commander before inventing domain data or adding
models/migrations. No product code has been changed in this checkpoint.

## Safety

No protected `codesho`, Release, Deployment, Production, migration, or API
mutation was performed.

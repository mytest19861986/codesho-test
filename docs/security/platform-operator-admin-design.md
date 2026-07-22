# Platform-Operator Django Admin Design

Status: design-only, Task56, BASE `64d9afd9d5d7f53076f15424683465298e85cbda`.
This document defines a future implementation boundary. It does not authorize
code, tests, migrations, API/OpenAPI changes, deployment, Alpha activation or
Production release.

## Authority and security posture

The scope follows employer decision 2-A: a narrowly allow-listed platform
operator capability in Django Admin, while tenant records remain hidden until
an explicit tenant-scoped policy is implemented and reviewed. `is_superuser`
alone is never an authorization decision. Authorization must fail closed when
the request has no authenticated user, the user is inactive, staff status is
absent, the approved operator policy is absent/inactive, tenant context is
missing for a tenant-scoped operation, or the requested model/action/field is
not allow-listed.

The implementation must keep business authorization in Django, establish
tenant context inside `transaction.atomic()` before tenant queries, preserve
PostgreSQL RLS boundaries, and avoid external provider calls in transactions.
Admin pages must not expose passcodes, password hashes, peppers, cookies,
tokens, credentials, raw provider responses, or other sensitive child data.
CSRF and same-origin session protections remain mandatory; login/session
behavior and cookie hardening are not weakened.

## Policy and permission matrix

The first implementation is platform-level operations only. The default is
deny; each cell below is an explicit policy decision, not a Django default.

| Model | List | View | Add | Change | Delete | Action | Field restrictions |
|---|---|---|---|---|---|---|---|
| `User` | Allow only the exact fields `id`, `email`, `first_name`, `last_name`, and `is_active`, and only after an active policy exists | Allow the same exact five fields for a single-object view, only after an active policy exists | Deny | Deny | Deny | Deny, including bulk actions | All fields other than `id`, `email`, `first_name`, `last_name`, and `is_active` are excluded; in particular never show `password`, `session_auth_epoch`, credentials, tokens, cookies or raw security metadata |
| `Tenant` | Deny until a tenant-scoped policy is separately approved | Deny until that policy exists | Deny | Deny | Deny | Deny | No tenant data is reachable through a global admin queryset |
| `TenantMembership` | Deny until a tenant-scoped policy is separately approved | Deny until that policy exists | Deny | Deny | Deny | Deny | No role, membership, guardian or learner data is exposed globally |

An operator policy is designed as a record with these exact keys: `id`,
`operator_user_id`, `model_label`, `action`, `scope_kind`, `active`,
`created_at`, `created_by_user_id`, `revoked_at`, and `revoked_by_user_id`.
`model_label` is one of `identity.User`, `platform_tenant.Tenant`, or
`platform_tenant.TenantMembership`; `action` is one of `list` or `view` for
the first User-only implementation; and `scope_kind` is `platform_user_safe`
only. The unique active key is
(`operator_user_id`, `model_label`, `action`, `scope_kind`); revocation is
one-way and irreversible on the same row: set `active=false`, `revoked_at`
and `revoked_by_user_id` exactly once. The revoked row is never reactivated or
broadened and cannot be deleted; any new grant requires a new policy row and
the same provisioning authority. The unique active key applies only while
`active=true`.

The implementation first has no active policy provisioning interface and must
therefore deny every admin request until a separately approved provisioning
procedure creates an exact policy record. No Django Admin screen, superuser
shortcut, fixture, startup hook or public API may create or activate policy in
this Task. A future provisioning authority must be an explicitly named,
separately approved deployment/security owner; policy creation and revocation
must themselves be audited. Policy precedence is deny if any applicable record
is absent, inactive, revoked, or conflicts; there is no allow-overrides-deny
rule. Hiding a menu or relying on a URL restriction is not authorization.
A Django superuser without the approved policy receives the same denial as any
other non-operator. Break-glass access is out of this candidate.

## Tenant and cross-tenant boundaries

Global Admin bypasses tenant-selection middleware, so no existing global
queryset is considered tenant-safe. In the first implementation,
`Tenant` and `TenantMembership` querysets and direct object access must be
empty/denied for all admin users, including approved operators. A future,
separately authorized tenant-scoped task must:

1. require an explicit tenant identifier selected through an approved flow;
2. enter `tenant_atomic(tenant_id)` before querying or mutating tenant data;
3. verify active membership/policy and reject absent, suspended or mismatched
   tenant context;
4. enforce the same boundary in object lookup, form validation, bulk actions
   and direct POST requests; and
5. return a non-sensitive denial without revealing whether another tenant or
   object exists.

Cross-tenant access is never an incidental consequence of staff or superuser
status. The implementation must test connection reuse and PostgreSQL RLS
negative paths, including context clearing after exceptions.

## Audit contract

Every permitted single-object User view and every denied sensitive
administrative attempt must produce a typed immutable security audit event.
User list requests are not audited in the first implementation because all
User list and view access is deny-only until policy provisioning is separately
approved. No mutation is permitted in the first implementation. The proposed
event types are:

- `ADMIN_USER_VIEWED` for an approved single-object User view;
- `ADMIN_USER_ACTION_DENIED` for denied User direct URL/POST/action attempts,
  including attempts to request excluded fields;
- `ADMIN_TENANT_ACCESS_DENIED` for all blocked Tenant/TenantMembership access;
- `ADMIN_POLICY_EVALUATED` only if the policy evaluation itself is audited;
- `ADMIN_MUTATION_SUCCEEDED` and `ADMIN_MUTATION_FAILED` are reserved for a
  future separately approved mutation task and are not emitted by the first
  implementation.

Each event has an immutable UUID `event_id`, UTC occurrence time, typed event
type, outcome (`success`, `failure` or `blocked`), non-sensitive reason code,
correlation ID, nullable `actor_user_id` (absent for unauthenticated requests),
nullable subject user ID when applicable, tenant ID only when an authorized
tenant context exists, and a bounded idempotency key when the operation can
retry. Metadata is a fixed allow-list of identifiers and counts; it excludes
request bodies, field values, credentials, cookies, tokens, IP/device secrets
and raw provider responses. Duplicate idempotency keys return the original
event result without a second row.

Coverage and failure behavior are exact: an approved single-object User view
appends `ADMIN_USER_VIEWED`; if that append fails, the view is denied with a
generic failure and no User data is rendered. A denied direct URL/POST/action,
excluded-field request, or Tenant/TenantMembership access appends its matching
blocked event; if that append fails, the request remains denied and returns a
generic denial without revealing object existence. An unauthenticated denial
uses `actor_user_id=NULL`. No first-implementation mutation exists; reserved
mutation events use rollback-on-audit-failure when a later task is approved.
Audit records remain append-only and immutable; no admin delete/change action
exists.

The existing typed audit enums and database allow-lists are read-only evidence
for this design. The proposed admin event types require a separately reviewed
forward-only migration and contract test before implementation.

## Migration, API and OpenAPI impact

No migration is created in Task56. A future implementation is expected to need
these exact proposed migration filenames, subject to dependency review:

- `backend/modules/platform_event/migrations/0009_platform_operator_admin_events.py`
- `backend/modules/identity/migrations/0007_platform_operator_policy.py`

The migration must add only approved typed audit allow-list values and the
minimal policy persistence required by the accepted matrix, preserve immutable
constraints, and pass empty-database and forward-only compatibility checks.
If inspection of the implementation task proves either migration unnecessary,
the file must not be created. No public API is proposed; OpenAPI must remain
unchanged and an explicit compatibility check must prove that fact.

## Future implementation file allow-list

The following exact filenames are the complete proposed implementation scope;
no wildcard or additional file is authorized by this design:

- `backend/modules/identity/admin.py`
- `backend/modules/platform_tenant/admin.py`
- `backend/modules/identity/admin_policy.py`
- `backend/modules/identity/models.py`
- `backend/modules/platform_event/models.py`
- `backend/modules/platform_event/security_audit.py`
- `backend/modules/platform_event/migrations/0009_platform_operator_admin_events.py`
- `backend/modules/identity/migrations/0007_platform_operator_policy.py`
- `backend/tests/test_admin_scope.py`
- `backend/tests/test_security_audit.py`

The implementation Task must revalidate the list against its exact diff before
editing. A separate approval is required for any file not listed here.

## Required test matrix

- unauthenticated, inactive, non-staff, staff-only and superuser-without-policy
  denial tests;
- approved-operator allow-list tests for each model/action/field cell;
- User sensitive-field redaction and direct URL/POST denial tests;
- Tenant and TenantMembership global, direct-URL/POST and cross-tenant
  non-disclosure denial tests; tenant selection, membership validation and
  suspended-tenant behavior are deferred to a separate tenant-scoped policy
  task;
- fail-closed behavior when policy, RLS or audit append fails; tenant context
  setup is not exercised by the deny-only first implementation;
- session fixation, CSRF, same-origin and logout behavior;
- audit success, denial, view/denial append failure and idempotency; mutation
  rollback and mutation audit events are deferred to a separately approved
  future mutation task and are not implemented or tested here;
- PostgreSQL constraints, immutable-row protections, RLS connection reuse and
  migration-from-empty-database checks;
- OpenAPI generation and compatibility check proving no public contract drift;
- `git diff --check`, backend lint/type checks and the relevant focused suite.

## Explicit non-goals and gates

This design does not authorize guardian/recovery, notifications, public admin
APIs, login UI, signup/onboarding/OAuth, payment, database role changes,
Production or real Alpha activation, protected `codesho` promotion, or
unrelated refactors. Production TLS/`__Host-` proof, legal retention/privacy,
cleanup scheduling and Alpha gates remain open.

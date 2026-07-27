# Synthetic Account Bootstrap Boundary

Status: `ARCHITECTURE_ONLY / PRIVACY_GATE / SYNTHETIC_ONLY / LEGAL_PENDING`

Date: 2026-07-27
Task: `SPRINT1-SYNTHETIC-ACCOUNT-BOOTSTRAP-ARCHITECTURE-71A`

## Problem

The internal synthetic adult-attestation foundation can establish an opaque
`adult_attested` claim, but it does not yet define whether or how that claim
could become an application account. A direct implementation would risk
connecting a subject to the wrong tenant, creating duplicate accounts during
retries, treating an attestation as an identity proof, or silently inventing
username, email, contact, credential, Guardian, or Recovery data.

This decision defines a future, synthetic-only boundary. It does not create an
account, membership, credential, endpoint, migration, or runtime behavior.

## Analysis

The conceptual lifecycle is:

```text
AdultAgeAttestation
        |
        v
SyntheticBootstrapRequest
        |
        v
User (opaque synthetic account)
        |
        v
TenantMembership (pending/disabled, no authorization)
        |
        v
Dormant / Initial Credential State (no secret material)
```

The attestation is an eligibility input, not a name, contact, identity proof,
or authorization to infer missing fields. The bootstrap request is the
transactional boundary and must carry only opaque references and controlled
state. The User is an account record, not a new subject. Membership is the
tenant authorization edge. The dormant credential state means that no
passcode, token, cookie, secret, or temporary credential exists until a
separate approved credential task defines one. Bootstrap must be fail-closed:
the resulting User and membership cannot authenticate or authorize through any
current or future path while dormant. Membership is pending/disabled, or
equivalently protected by a database-enforced activation gate, until a
separately authorized activation and credential task. Activation, role
enablement, and credential enrollment are outside Task71A.

The current `User` model requires Django's `username` and a unique `email`.
That is an implementation constraint, not permission to synthesize a person's
email or contact data. The current `TenantMembership` edge is tenant-scoped
and unique per `(tenant, user)`, which is the correct authorization boundary
but not by itself an attestation-to-account idempotency boundary.

## Options

### A: Refactor account identity fields for an explicit synthetic mode

Add a future account identity mode and an opaque, non-semantic account handle;
make human username/email optional for that mode, with database constraints
that prevent synthetic rows from claiming real identity fields. The User,
membership, request, and audit records would still be created transactionally.

- Security: strongest; no placeholder contact data and clear mode checks.
- Privacy: strongest; synthetic identity remains opaque and non-contactable.
- Cost: moderate schema, migration, admin, authentication, and validation work.
- Time: longer than placeholders because every identity consumer needs review.
- Extensibility: good; future identity modes can be explicit and constrained.

### B: Populate the current required fields with reserved opaque placeholders

Keep the current schema and derive a deterministic opaque username and a
non-deliverable reserved email-shaped value from a UUID.

- Security: medium; every sender, lookup, export, and uniqueness path must
  prove that placeholders cannot become contact or login credentials.
- Privacy: weaker; an email-shaped value can be mistaken for a real contact
  or leak into ordinary user-facing flows.
- Cost: lowest initial migration cost, but high hidden validation and cleanup
  cost.
- Time: fastest first implementation, with a high chance of rework.
- Extensibility: poor; synthetic conventions become permanent compatibility
  obligations.

This option is rejected. The project must not invent email, phone, name, or
identity data merely to satisfy a current field requirement.

### C: Stage the bootstrap request outside User until identity fields are approved

Create a future synthetic bootstrap request and verification state first, then
create a User only after an approved identity-field contract exists. The
request remains an opaque, tenant-scoped pending record and does not grant
login or membership access.

- Security: strong; no account is created before the identity contract is
  explicit, but the staging boundary must itself be protected.
- Privacy: strong; no placeholder contact data is needed.
- Cost: moderate to high because it adds a durable state machine and later
  reconciliation.
- Time: slower to deliver an account, but supports safe sequencing.
- Extensibility: strongest for future synthetic modes and legal review.

### Recommendation

Adopt **Option A as the intended account end-state**, sequenced through the
request boundary of **Option C**. Reject Option B. Task71B must first define
the identity-mode schema and request state machine, then implement them only
with a separately approved allow-list. No current model change is authorized
by Task71A.

## Reason

Option A makes the absence of real identity data explicit instead of encoding
absence as fake contact data. Option C provides a safe implementation order:
the system can validate attestation provenance and idempotency before an
account edge exists, while a future schema change is reviewed across all
username/email consumers. This combination minimizes privacy leakage and
limits migration risk without claiming Production or real-user readiness.

## Security and Privacy Invariants

- A bootstrap request may reference only opaque UUIDs: request, tenant,
  attestation, subject, and eventual account references. No name, email,
  phone, birth date, numeric age, identity document, raw payload, IP/device
  signal, cookie, token, passcode, secret, or free text is accepted.
- The attestation's tenant, request tenant, membership tenant, and provenance
  tenant must be identical. Missing, cross-tenant, malformed, or invalid
  provenance fails closed.
- An `AdultAgeAttestation` may link to **at most one** synthetic account in
  the lifetime of the contract. A repeated request with the same valid
  idempotency identity may replay the same outcome; a different request for an
  already-linked attestation is a conflict, never a second account.
- Account, membership, bootstrap state, and the bounded security-audit outcome
  commit together or roll back together. No signal or serializer owns this
  workflow; business logic must execute in one explicit service transaction.
- A bootstrap result is authorization-disabled by construction. The User cannot
  authenticate and the membership cannot authorize any request while dormant;
  the pending/disabled state or database-enforced activation gate must fail
  closed across every present and future authentication or authorization path.
  Activation, role enablement, and credential enrollment require a separately
  authorized task and are not implied by account creation.
- Raw credentials are never generated or persisted here. Dormant means no
  credential material and no session/token/cookie issuance.
- Provenance remains restricted and is never copied into ordinary audit
  metadata, User fields, membership fields, logs, analytics, responses, or
  support exports.
- Published evidence and audit events remain immutable. Bootstrap retries are
  idempotent and do not mutate an existing account or membership.
- No Guardian, Recovery, Notification, provider, real-user, public-signup, or
  Production behavior can be inferred from this architecture.

## Data Classification

| Concept | Minimum future data | Classification | Ordinary visibility |
|---|---|---|---|
| Subject | Opaque synthetic UUID | Restricted synthetic identifier | No direct display |
| Attestation | Opaque subject/attestation UUID, tenant, constant status/source, policy and UTC time | Restricted evidence | Bounded outcome only |
| Provenance | Existing restricted opaque receipt/reference and controlled context | Highly restricted / legal pending | Never ordinary audit |
| Bootstrap request | Opaque request, tenant, attestation, state, idempotency reference, UTC timestamps | Restricted workflow metadata | No raw provenance |
| User | Opaque account UUID and approved synthetic identity mode | Restricted account record | No invented contact data |
| Membership | Opaque user/tenant UUIDs, pending/disabled role edge | Tenant authorization boundary | Tenant-scoped only; no authorization while dormant |
| Credential state | Dormant/initial state only, no secret material | Restricted security state | No secret or token |
| Security audit | Bounded event/reason code and opaque references | Restricted audit | Outcome only |

## Logical Data Boundaries

The subject may connect to its attestation only within the attestation tenant.
The attestation may connect to one bootstrap request through an opaque,
unique reference. The request may connect to one User and one membership in
the same tenant. The audit event may record that the bounded workflow
completed, but must not expose provenance or identity fields.

These connections are intentionally unavailable to ordinary consumers:

- subject to real name, email, phone, identity document, or external account;
- subject or attestation to a different tenant's request, User, or membership;
- provenance to ordinary audit metadata, support search, analytics, or API;
- dormant account to passcode, token, cookie, or session;
- one attestation to multiple accounts or one request to multiple memberships.

The future User row is not a second subject record. It is an opaque account
edge whose only eligibility evidence is the approved, same-tenant attestation
and request path.

## Transaction, Idempotency, and Concurrency Contract

The future service must establish tenant context inside one
`transaction.atomic()` before any tenant query. It must lock or otherwise
serialize the attestation/request boundary, validate the restricted provenance,
and rely on database uniqueness as the final race guard. Required uniqueness
boundaries are at least `(tenant_id, attestation_id)` for the request and
`(tenant_id, attestation_id)` for the account linkage; a deterministic request
idempotency key must not cross tenants.

Two concurrent first requests may produce one committed account, one
membership, and one audit outcome. The loser must retry/read the committed
idempotent result or return the same deterministic conflict; it must never
create a second User. A replay with a changed tenant, attestation, provenance,
or payload is rejected, not merged into an existing request.

## Tenant and PostgreSQL/RLS Preconditions

Future request and membership tables require PostgreSQL RLS with FORCE RLS,
fail-closed tenant predicates, and runtime privileges limited to the workflow.
The service must set and verify `app.tenant_id` inside the transaction before
attestation, provenance, request, membership, or tenant-scoped audit reads.
Cross-tenant linkage, absent tenant context, invalid provenance, and runtime
SELECT/UPDATE/DELETE/TRUNCATE outside the permitted workflow must fail closed.
The global User row must not become a bypass around the tenant membership
boundary; every account authorization query must prove the same-tenant
membership edge.

## Implementation Preconditions

Task71B, if separately authorized, must provide:

1. an identity-mode and opaque-handle schema decision for the current
   username/email requirement;
2. a bootstrap request model/state machine and exact database constraints;
3. service-layer transaction and retry implementation without signals;
4. RLS policies, role grants, immutable/audit rules, and empty-database
   migration checks;
5. bounded API/OpenAPI decisions, if any, in a separate authorization;
6. concurrency, tenant-negative, provenance-negative, rollback, replay, and
   no-secret test coverage; and
7. independent security, privacy, and database/RLS review with all findings
   dispositioned.

### Future migration and rollback plan

The future migration must use an expand/verify/contract sequence, begin with
empty-database validation, and contain no backfill from real or historical
subjects. Existing User rows must remain readable at every safe migration
boundary. A rollback may remove an unused schema before data exists; after
account or membership data exists, rollback is a separately approved data and
legal decision, not an automatic destructive reverse migration. No migration
or rollback is part of Task71A.

### Future test matrix

The future implementation must test: same-tenant happy path; missing and
cross-tenant tenant context; invalid/missing/cross-tenant provenance;
duplicate attestation and duplicate request; replay with identical and changed
inputs; concurrent first requests; account/membership/audit atomic rollback;
RLS and role privilege negatives; no raw credential/token/cookie/secret;
immutable audit and evidence; empty-database migration; and API/OpenAPI
non-change when those surfaces are out of scope.

### Proposed Task71B allow-list

The following is a proposal only and is not authorization: identity/request
models and migrations; the bootstrap service; focused tests; any approved
OpenAPI artifact; and the four coordination/review artifacts needed to record
CI and findings. Task71B must receive a new exact allow-list and BASE_SHA.

## Explicit Exclusions

Task71A creates no model, migration, rollback, backfill, endpoint, OpenAPI,
frontend route, serializer, configuration, test, User, TenantMembership,
credential, session, cookie, token, passcode, audit event, provider call,
account, membership, public signup, real-user behavior, Production behavior,
deployment, release, Guardian, Recovery, or legal policy.

It does not authorize changing `User.username`, `User.email`, authentication,
or any current source code. It does not authorize PR #5 or protected
`codesho` promotion.

## Open Legal Decisions

Retention, deletion, erasure, aging-out, legal hold, lawful basis, notices,
consent, jurisdiction, subject-to-provenance linkage, and Guardian/Recovery
implications remain `LEGAL_PENDING`. No retention duration, deletion right, or
identity conclusion is invented here.

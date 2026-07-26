# Adult Attestation Provenance Separation

Status: `ARCHITECTURE_ONLY / PRIVACY_GATE / LEGAL_PENDING`

Date: 2026-07-26
Scope: internal synthetic adult-attestation foundation only

## Problem

The current adult-attestation foundation records a minimal `adult_attested`
claim for an opaque synthetic subject. The privacy gate is incomplete unless
the operational claim is kept logically separate from information about how,
where, or by which controlled process the claim was collected. A routine
security-audit event must not become a side channel for sensitive provenance.

## Analysis

Four concepts have different purposes and different connection rules:

- **Subject** is an opaque UUIDv4 representing a synthetic subject. It is not
  a name, contact, identity number, birth date, age, document, or raw payload.
- **Attestation** is the minimal immutable tenant-scoped claim that the
  subject passed the approved adult self-attestation contract. It contains the
  policy version, constant status/source values, timestamps, and an idempotency
  boundary, but no collection provenance.
- **Provenance** is a separate, restricted logical record describing the
  approved collection context at the minimum useful granularity. It uses
  opaque references and controlled enums only. It is not ordinary audit
  metadata or a free-form evidence store.
- **Security-audit event** records bounded security outcomes and reason codes.
  It may reference the attestation by an opaque evidence identifier, but must
  never contain sensitive provenance, raw signals, cookies, selectors, digests,
  contact data, identity evidence, or payloads.

The boundaries apply even when records share a database. Tenant context is
resolved fail-closed inside the transaction before tenant queries; PostgreSQL
RLS remains a second boundary. A provenance reference must not make an
ordinary audit consumer able to reconstruct collection context.

## Options

### A: Preserve the current combined model

Keep claim and provenance fields in one operational record. Security/privacy is
weakest because accidental joins and audit leakage are likely. Immediate cost
and migration complexity are lowest, but extensibility is poor and future
provenance changes expand the claim model.

### B: Separate provenance record with a limited opaque reference

Keep the attestation minimal and create a separately governed provenance
record, linked only by an opaque, non-semantic reference and tenant boundary.
This gives strong logical separation and least-privilege access at moderate
storage, policy, and migration cost. It is extensible for the internal
synthetic environment without creating a Production claim.

### C: Keep provenance outside the operational identity boundary

Store provenance in a separately governed service or controlled evidence
boundary, with only an opaque receipt/reference retained operationally. This
offers the strongest separation but the highest operational, provider,
availability, governance, and migration cost. It is not appropriate before
legal and operational authority exists.

## Recommendation

Adopt **Option B** as the architecture contract for the internal synthetic
environment. The current implementation remains unchanged by this document.
Any provenance record must be separately authorized, tenant-scoped, immutable,
least-privilege, and referenced only through opaque identifiers. Option C may
be reconsidered after an approved legal and operational boundary exists.

This recommendation is not a Production, public-availability, real-user,
deployment, release, or account-readiness claim.

## Reason

Option B provides a practical privacy boundary without inventing a provider or
legal policy. It prevents routine audit consumers from receiving provenance,
keeps the adult claim minimal, and leaves a controlled path for a future
synthetic-only implementation. It also makes the authority required for any
identity-bound or external provenance explicit.

## Security and Privacy Invariants

- `adult_attested` and collection provenance are logically separate; no
  ordinary audit metadata may carry provenance.
- Persist only opaque identifiers, controlled enums, policy version, bounded
  timestamps, and bounded status/source values. Never persist names, phone
  numbers, birth dates, numeric ages, identity documents/numbers, raw IP or
  device signals, cookies, selectors, digests, passcodes, secrets, or payloads.
- Tenant resolution fails closed and occurs inside `transaction.atomic()` before
  tenant queries. PostgreSQL RLS and database grants enforce the boundary.
- Attestation, provenance, receipts, and security-audit events are immutable;
  updates, deletes, and truncation are not an application workflow.
- Idempotency keys are deterministic within the relevant tenant and event
  boundary. Retries must not create duplicate accepted claims or events.
- Provenance access is deny-by-default and is not included in ordinary audit,
  support, analytics, or API serializers.
- A provenance reference is opaque, non-semantic, non-guessable, and must not
  be usable as an identity lookup key by an untrusted caller.
- External providers, if ever approved, are called outside database
  transactions; raw provider responses are not persisted.

## Data Classification

| Boundary | Allowed minimum | Classification | Ordinary audit visibility |
|---|---|---|---|
| Subject | Opaque UUIDv4 | Restricted synthetic identifier | Opaque reference only |
| Attestation | Tenant, opaque subject, constant status/source, policy version, UTC timestamps, idempotency boundary | Restricted operational evidence | Bounded outcome only |
| Provenance | Opaque provenance/receipt reference and approved controlled context enums | Highly restricted / legal pending | Not visible |
| Security audit | Event type, bounded reason code, tenant, opaque event/evidence reference, UTC time | Restricted security record | Yes, without provenance |

No row may contain free text or an unbounded metadata map that can reintroduce
prohibited data.

## Logical Data Boundaries

The subject may connect to its attestation inside the same tenant boundary.
The attestation may connect to a provenance record only through the restricted
opaque reference and a separately authorized access path. A security-audit
event may connect to an attestation or receipt through an opaque event/evidence
reference, but must not connect ordinary consumers to provenance.

The following are intentionally non-connectable in normal operation: subject
to collection operator identity; subject to raw network/device signals;
attestation to identity documents or birth data; audit event to provenance
details; and opaque references to names, contacts, or external account IDs.
Any future legal or security investigation path requires a separately approved,
least-privilege workflow and must not be inferred from this document.

## Implementation Preconditions

Before implementation, an exact schema and migration plan, tenant/RLS and
grant tests, immutable append/retention behavior, idempotency and retry
semantics, bounded OpenAPI and serializer rules, empty-database migration
verification, and provider-neutral security/privacy review are required.
Synthetic-only fixtures must remain opaque and must not be reused as real-user
data.

Retention, deletion, erasure, aging-out, and legal-hold behavior are
`LEGAL_PENDING`. This project does not invent a legal duration or claim that
any record may be deleted or retained without counsel.

## Explicit Exclusions

This decision creates no model, migration, backfill, endpoint, OpenAPI change,
configuration, test, frontend route, account, credential, membership, session,
Guardian/Recovery path, notification, provider integration, or source-code
behavior. It does not activate real users, public availability, Production,
deployment, release, Alpha, or protected-repository promotion. It does not
authorize a merge of PR #5.

Future work may define an internal synthetic provenance implementation, but
migration, backfill, public API, account creation, and any connection to real
users are separate authorized tasks only.

## Open Legal Decisions

- Whether provenance may be collected at all, and under which lawful basis.
- Retention, deletion, erasure, aging-out, and legal-hold periods.
- Whether any subject-to-provenance linkage is lawful and who may access it.
- Requirements for counsel-approved notices, consent, auditability, and
  jurisdictional handling.
- Whether a separately governed external evidence boundary is required.

All items remain `LEGAL_PENDING`; no legal conclusion is implied.

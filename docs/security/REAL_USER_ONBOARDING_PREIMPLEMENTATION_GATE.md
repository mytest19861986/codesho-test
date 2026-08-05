# Real-user onboarding preimplementation gate

Status: `BLOCKING / FAIL_CLOSED / LEGAL_PENDING / NO_IMPLEMENTATION`

Task: `SPRINT1-REAL-USER-ONBOARDING-LEGAL-AND-BOUNDARY-DECISION-72B`
Base: `0472239d06194875d1cdb6f6929dd8eaad8bc0d9`

## Gate verdict

`NO-GO` for Option B and Option C. Only Option A, the legal/policy packet, is
authorized. No technical artifact may interpret an unanswered legal or
Employer decision as consent, eligibility, deletion authority, Guardian
authority, tenant authority, Recovery authority, or activation.

## Blocking P0 gates

| Gate | Required evidence | Owner | Result |
| --- | --- | --- | --- |
| Jurisdiction, Controller, lawful basis | Jurisdictions, controller record, purpose/basis matrix | Employer + Counsel | `PENDING_EMPLOYER` / `PENDING_COUNSEL` |
| Notice and consent | Versioned notice/evidence plus acknowledgement, consent, withdrawal/re-consent | Counsel; product presentation by Employer | `PENDING_COUNSEL` |
| Adult/Minor/Guardian | Thresholds, eligibility, assent, authority, dispute, withdrawal, aging-out | Employer + Counsel | `PENDING_EMPLOYER` / `PENDING_COUNSEL` |
| Record lifecycle | Per-record retention, deletion, erasure, DSR, legal-hold policy | Counsel; operator by Employer | `PENDING_COUNSEL` |
| Product authority | Approved PRD, personas, valid/invalid/abandoned journeys | Employer | `PENDING_EMPLOYER` |
| DPIA/privacy assessment | Counsel determination and completed assessment or documented no-DPIA rationale, approver and review date | Counsel; operational inputs/owner by Employer | `PENDING_COUNSEL` / `PENDING_EMPLOYER` |

Any P0 pending state blocks collection, verification, persistence, account,
credential, membership, session, role, activation and public access.

## P1 security/privacy gates

- authoritative tenant assignment, same-tenant linkage, global uniqueness,
  idempotency and concurrency;
- identifier/contact minimization, verification and purpose/access control;
- exact ordering/expiry of eligibility, notice/consent, Guardian,
  verification, credential and activation gates;
- independent Recovery and Guardian anti-takeover boundaries;
- enumeration-resistant failures, abuse controls, replay protection and token
  secrecy;
- least-privilege provenance separated from audit, support and analytics;
- provider/residency/DPA/subprocessor and incident/DSR/breach/hold ownership.

Each is `PENDING_EMPLOYER` for product/operational authority, plus
`PENDING_COUNSEL` where legal/privacy authority applies, and requires
independent Security/Privacy review before Option B.

## Future security invariants

1. Before any PII collection/processing, the applicable purpose, lawful basis,
   notice and consent or other authority must be approved and presented at
   counsel-approved timing. Before any tenant-scoped read/link, authoritative
   tenant context must be proven. Their detailed relative ordering remains
   `PENDING_COUNSEL` and `PENDING_EMPLOYER` until the approved data flow
   resolves it. Missing or ambiguous context fails closed; a global account
   cannot bypass membership.
2. Eligibility/authority evidence is not identity proof, a credential, role,
   or activation. A later stage cannot infer an earlier stage.
3. Consent/Guardian evidence must be versioned, purpose-, actor-, jurisdiction-
   and time-bound and revocable under counsel-approved rules. Withdrawal,
   expiry, dispute or aging-out blocks dependent actions.
4. Verification/enrollment/Recovery artifacts must be single-purpose,
   same-tenant, subject/version/expiry-bound and replay-resistant. No secret or
   raw evidence enters URLs, logs, telemetry, analytics, audit or support.
5. Final state remains inactive, roleless and unable to authenticate until a
   separate activation decision proves all predecessor gates.
6. Provenance and Guardian/child evidence are deny-by-default and separate
   from routine audit; audit holds bounded outcomes and opaque references.
7. Provider failure, missing approval, unsupported jurisdiction, conflicting
   identity, cross-tenant linkage, stale evidence or lifecycle ambiguity never
   degrades to success.

## Threat-model evidence required

| Area | Required questions |
| --- | --- |
| Tenant linkage | Who assigns authority? How are transfers, duplicates, identifier collisions, retries and concurrent first use rejected? |
| Minor/Guardian | How are authority, impersonation, dispute, replacement, withdrawal and aging-out protected from takeover/confused deputy? |
| Recovery | Which independent factors/operators may recover, and how are Guardian/support paths prevented from bypassing authority? |
| Enumeration/abuse | How do response, timing, rate controls and audit avoid revealing identity, age, Guardian, tenant or state? |
| Replay/leakage | How is every artifact purpose/tenant/subject/version/expiry-bound, one-time and secret-safe? |
| Provenance/privacy | Who can access raw evidence, how are audit/support/analytics excluded, and how are DSR/hold actions audited? |

## Auditability and future evidence

Every closed decision must identify approver, date, jurisdiction/persona/
purpose, exact evidence version, effective/review dates, supersession rule and
operational owner. A future ADR must trace each field, transition, API
response, database privilege, audit event and cleanup action to an approved
decision ID. Evidence must be reviewable without copying raw PII, secrets or
restricted provenance into the repository.

Future test specifications must cover FORCE RLS, least-privilege grants,
missing/cross-tenant context, linkage uniqueness, concurrent/replayed requests,
withdrawal/expiry/dispute/aging-out, inactive authorization negatives,
Recovery/Guardian takeover, enumeration, provider failure, audit minimization,
and counsel-approved retention/DSR/hold. This task authorizes no tests/code.

## Option B Go/No-Go

Option B remains `NO-GO` unless all are true:

- [ ] all P0 rows are approved by named owners;
- [ ] Adult/Minor/Guardian and consent matrix is approved;
- [ ] data-flow/classification/purpose/access inventory is approved;
- [ ] every record has approved lifecycle and hold behavior;
- [ ] tenant assignment/uniqueness/idempotency/cross-tenant rejection is approved;
- [ ] activation and independent Recovery/Guardian contracts are approved;
- [ ] DPIA/privacy and provider/residency/DPA/RACI are approved;
- [ ] separate ADR/schema/API/OpenAPI/migration/rollback plans are reviewed;
- [ ] RLS/grant/tenant/concurrency/audit/lifecycle test plans are accepted;
- [ ] independent Security, Privacy, Database and Legal reviews pass;
- [ ] Commander issues a new bounded task and Employer supplies required
      product/legal/cost authority.

## Minimum scope and exclusions

The minimum next scope is decision closure only: jurisdiction/personas,
lawful basis/notice/consent/Guardian authority, data inventory, lifecycle,
conceptual gates, tenant/Guardian/Recovery/enumeration threats,
provider/residency/operations, and Go/No-Go. Option C is rejected.

No model, schema, migration, API/OpenAPI, UI, code state machine, PII, real
data, account, credential, session, active membership, role, public endpoint,
email/SMS/OAuth/provider integration, Guardian/Recovery implementation,
deployment, Alpha, Production or protected `codesho` promotion is authorized.

## Authority trace

Read this gate with the Task72B packet and the five Task72A-reviewed files:

- `docs/decisions/2026-07-26-adult-signup-internal.md`;
- `docs/decisions/2026-07-26-adult-signup-provenance-separation.md`;
- `docs/decisions/2026-07-26-synthetic-account-bootstrap-boundary.md`;
- `docs/decisions/2026-07-17-auth-alpha-decisions.md`; and
- `docs/security/AUTH_PASSCODE_CHANGE_001_DESIGN.md`.

Historical synthetic/Alpha decisions never broaden real-user authority. The
strictest unresolved gate controls.

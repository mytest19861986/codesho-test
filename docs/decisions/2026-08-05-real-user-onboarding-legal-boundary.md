# Real-user onboarding legal and boundary decision packet

Status: `LEGAL_POLICY_GATE / OPTION_A / FAIL_CLOSED / NO_IMPLEMENTATION`

Date: 2026-08-05
Task: `SPRINT1-REAL-USER-ONBOARDING-LEGAL-AND-BOUNDARY-DECISION-72B`
Base: `0472239d06194875d1cdb6f6929dd8eaad8bc0d9`

## Problem, options, and decision

Codesho has internal synthetic identity foundations, but no approved legal,
privacy, product, or activation contract for a real person. Reusing those
foundations could create unlawful collection, unsafe Minor/Guardian handling,
cross-tenant linkage, undeletable evidence, or premature authentication.

- **A — legal/policy packet first:** selected.
- **B — internal disabled foundation, without PII or activation:** deferred
  until every P0 gate closes and a separate task is authorized.
- **C — real-user creation now:** rejected.

This packet records questions, owners, evidence, and blocking effects. It does
not answer legal questions by engineering inference. `PENDING_COUNSEL` and
`PENDING_EMPLOYER` are blockers, not provisional approvals.

## Persona and jurisdiction matrix

| Persona | Jurisdiction / eligibility | Notice and lawful basis | Consent / authority | Activation |
| --- | --- | --- | --- | --- |
| Adult | `PENDING_COUNSEL`; thresholds per Employer-proposed launch jurisdictions | `PENDING_COUNSEL`; basis and notice per purpose | `PENDING_COUNSEL`; evidence and withdrawal | Blocked |
| Minor | Product eligibility `PENDING_EMPLOYER`; local thresholds `PENDING_COUNSEL` | Child-specific basis/notice `PENDING_COUNSEL` | Assent and Guardian requirements `PENDING_COUNSEL` | Blocked |
| Guardian | Supported relationships `PENDING_EMPLOYER`; authority law `PENDING_COUNSEL` | Guardian basis/notice `PENDING_COUNSEL` | Proof, scope, expiry, dispute, withdrawal and replacement `PENDING_COUNSEL` | Blocked |

The Employer must define intended launch jurisdictions/personas; counsel must
validate applicability and thresholds. Unknown, conflicting, unsupported, or
unverifiable eligibility fails closed before identity/contact collection,
credential, account, membership, or activation.

## P0 decision register

| ID | Decision | Owner/status | Evidence required | Blocking effect |
| --- | --- | --- | --- | --- |
| P0-01 | Launch jurisdictions/exclusions | `PENDING_EMPLOYER`, then `PENDING_COUNSEL` | Written launch list and counsel memo | No real-user collection |
| P0-02 | Controller identity/contact and controller/processor roles | `PENDING_EMPLOYER`, validated by `PENDING_COUNSEL` | Signed responsibility record | No notice/processing |
| P0-03 | Lawful basis per purpose/persona | `PENDING_COUNSEL` | Purpose-by-purpose determination | No collection/persistence |
| P0-04 | Versioned notice, presentation, proof of delivery | `PENDING_COUNSEL`; product presentation `PENDING_EMPLOYER` | Approved text/version/locale/timing/evidence | No eligibility completion |
| P0-05 | Consent/acknowledgement, withdrawal, re-consent | `PENDING_COUNSEL` | Consent matrix and consequences | No activation |
| P0-06 | Minor thresholds, assent, Guardian authority | `PENDING_COUNSEL`; supported personas `PENDING_EMPLOYER` | Rules per jurisdiction | Minor/Guardian path prohibited |
| P0-07 | Guardian dispute/replacement/withdrawal/aging-out | `PENDING_COUNSEL` | Transition, notice, expiry and conflict rules | Dependent activation prohibited |
| P0-08 | Retention/deletion/erasure/DSR/legal hold per record | `PENDING_COUNSEL`; operator `PENDING_EMPLOYER` | Approved schedule/procedure | No real-user record |
| P0-09 | PRD, personas and valid/invalid/abandoned journeys | `PENDING_EMPLOYER` | Approved product packet | No Option B design |
| P0-10 | DPIA/privacy assessment requirement and outcome | `PENDING_COUNSEL`; operational inputs/owner `PENDING_EMPLOYER` | Counsel decision whether required, completed assessment or documented no-DPIA rationale, approver and review date | No Option B design or real-data processing |

## P1 decision register

| ID | Decision | Owner/status | Evidence required | Blocking effect |
| --- | --- | --- | --- | --- |
| P1-01 | Tenant assignment and assertion authority | `PENDING_EMPLOYER`; independent Security review required after decision | Authority model/negative cases | No tenant linkage |
| P1-02 | Identifier/contact minimization and verification | `PENDING_EMPLOYER` + `PENDING_COUNSEL` | Field/purpose/verification matrix | No identifiers |
| P1-03 | Gate ordering, expiry, retry and re-entry | `PENDING_EMPLOYER` + `PENDING_COUNSEL`; independent Security/Privacy review required after decision | Approved data flow and conceptual lifecycle | No implementation design |
| P1-04 | Recovery and Guardian anti-takeover | `PENDING_EMPLOYER` + `PENDING_COUNSEL`; independent Security review required after decision | Independent threat model | No Recovery |
| P1-05 | Abuse, enumeration, replay and token leakage | `PENDING_EMPLOYER`; independent Security review required after decision | Control requirements | No public endpoint |
| P1-06 | Provenance access vs audit/support/analytics | `PENDING_EMPLOYER` + `PENDING_COUNSEL` | Purpose/access matrix | Deny ordinary access |
| P1-07 | Provider, residency, DPA, incident/breach governance | `PENDING_EMPLOYER` + `PENDING_COUNSEL` | Vendor/residency register, DPA, RACI | No provider/transfer |

## Data flow, classification, purpose and access inventory

This inventory is not authority to collect any listed data.

| Record/boundary | Minimum proposed purpose | Classification | Proposed access | Status |
| --- | --- | --- | --- | --- |
| Eligibility/age result | Select permitted path without birth date unless required | Highly restricted child/identity data | Dedicated eligibility workflow; not support/analytics | `PENDING_COUNSEL` |
| Identity/account reference | Bind an approved person once | Restricted identity | Identity roles; tenant link separate | `PENDING_EMPLOYER` + `PENDING_COUNSEL` |
| Contact/verification evidence | Deliver/prove approved verification | Restricted contact/security | Verification only; not ordinary audit | `PENDING_EMPLOYER` + `PENDING_COUNSEL` |
| Notice/consent evidence | Prove version, actor, authority, decision and time | Highly restricted legal evidence | Privacy/legal; opaque audit reference | `PENDING_COUNSEL` |
| Guardian relationship/evidence | Prove scoped authority | Highly restricted child/legal | Separate Guardian boundary | `PENDING_COUNSEL` |
| Tenant assignment/linkage | Establish authorization edge | Restricted authorization | Tenant-authority workflow | `PENDING_EMPLOYER` |
| Provenance/receipt | Prove controlled origin without raw duplication | Highly restricted/legal pending | Separate from audit/support/analytics | `PENDING_COUNSEL` |
| Credential/Recovery evidence | Authenticate/recover after authority | Restricted security | Independent security boundary | `PENDING_EMPLOYER`; Security review required after decision |
| Bounded security audit | Record outcome/opaque references | Restricted security | Append-only; no raw PII/evidence | `PENDING_COUNSEL` |

Required future flow: source -> purpose/lawful-basis check -> eligibility and
authority -> minimized restricted store -> approved consumer -> approved
lifecycle disposition. No flow to logs, telemetry, analytics, support exports,
training data, ordinary audit, or providers without a separate purpose/access
entry.

## Record lifecycle matrix

No duration or deletion behavior is settled. Synthetic/Alpha durations must
not be reused as real-user legal policy.

| Record | Retention | Deletion/erasure | DSR/export/correction | Hold/aging-out | Owner/status |
| --- | --- | --- | --- | --- | --- |
| Identity/account reference | Unset | Downstream linkage unset | Verification/scope unset | Hold precedence unset | `PENDING_COUNSEL` |
| Notice/consent evidence | Unset by version/withdrawal | Immutability vs erasure unresolved | Receipt/correction unset | Withdrawal/aging-out/hold unresolved | `PENDING_COUNSEL` |
| Provenance/receipt | Unset | Linkage/deletion unresolved | Visibility/access unresolved | Investigation/hold unset | `PENDING_COUNSEL` |
| Abandoned onboarding | Definition/timer unset | Purge/anonymization unset | DSR treatment unset | Minor/Guardian hold unset | `PENDING_COUNSEL` + `PENDING_EMPLOYER` |
| Guardian relationship/evidence | Authority expiry unset | Withdrawal/dispute cleanup unset | Guardian/minor rights unset | Conflict/aging-out/hold unset | `PENDING_COUNSEL` |
| Security/audit evidence | Duration unset | Append-only vs erasure unresolved | Disclosure/redaction unset | Trigger/release/owner unset | `PENDING_COUNSEL` |

The approved policy must define request authentication, search scope,
downstream propagation, deadlines, exceptions, hold authorization/release,
evidence, and operator. No deletion job or manual deletion authority is
implied.

## Conceptual gate ordering

Two independent precedence rules are mandatory: **before any collection or
processing of PII, the applicable purpose, lawful basis, notice and consent or
other authority must be approved and presented at counsel-approved timing**;
and **before any tenant-scoped read or link, authoritative tenant context must
be proven**. Their detailed relative order, including whether a data-free
tenant invitation can precede notice, remains `PENDING_COUNSEL` and
`PENDING_EMPLOYER` until the approved data flow resolves it. After both apply,
eligibility/age, any Guardian authority, minimized verification, separately
authorized credential enrollment and explicit activation must each fail
closed on all applicable predecessors.

Every transition must prove predecessors current, same-tenant and unrevoked.
Missing/expired/disputed evidence, withdrawal, tenant mismatch, unsupported
jurisdiction, provider failure, or ambiguous persona remains inactive and
non-authorizing. No account, credential, session, active membership, role,
notification, or public endpoint is authorized.

## Mandatory threat questions

- Who assigns tenant authority, and how are invitation, self-selection,
  operator assignment and transfer distinguished?
- Which invariants prevent cross-tenant linkage, global collisions, duplicate
  identity, retry/idempotency failure and concurrency races?
- Can identifiers, Guardian proof, receipts or Recovery factors enumerate a
  person or reveal another tenant's membership?
- How are Guardian authority, dispute, replacement, withdrawal and aging-out
  protected from takeover and confused-deputy actions?
- How are enrollment/Recovery artifacts purpose-, tenant-, subject-, version-
  and expiry-bound, one-time, replay-resistant and secret-safe?
- How do neutral responses and abuse controls avoid leaking onboarding state?
- How is provenance denied to ordinary audit, support and analytics while
  supporting an authorized investigation?

## Provider, residency and operations

| Decision | Evidence | Owner/status | Block |
| --- | --- | --- | --- |
| Build/provider for identity/contact/age/Guardian | Product/security/privacy assessment | `PENDING_EMPLOYER` + `PENDING_COUNSEL` | No integration |
| Regions and cross-border transfer | Data-flow map and counsel decision | `PENDING_COUNSEL` | No transfer |
| DPA, subprocessors, deletion/export/breach duties | Executed terms/due diligence | `PENDING_EMPLOYER` + `PENDING_COUNSEL` | No provider data |
| Incident, DSR, hold and breach RACI | Named roles/escalation/evidence | `PENDING_EMPLOYER` + `PENDING_COUNSEL` | No Production |

## Go/No-Go for Option B

Option B is `GO` only after auditable evidence for all items and a new exact
Commander task:

- [ ] Employer and counsel approve every P0.
- [ ] Adult/Minor/Guardian, consent/withdrawal/aging-out matrix is approved.
- [ ] Data classification/flow and purpose/access matrix is approved.
- [ ] Every record has retention/deletion/erasure/DSR/hold rules.
- [ ] Tenant authority/uniqueness/idempotency/cross-tenant rejection is approved.
- [ ] Activation proves inactive/no-role/no-session until every gate passes.
- [ ] Recovery and Guardian boundaries have an independent threat model.
- [ ] DPIA/privacy, provider/residency/DPA and operational RACI are approved.
- [ ] Separate ADR/schema/API/OpenAPI/migration plan is reviewed before code.
- [ ] RLS/FORCE/grant/tenant-negative/concurrency/audit/lifecycle tests are specified.
- [ ] Independent Security, Privacy, Database and Legal reviews pass.

Any unchecked item is `NO-GO`. Option C remains rejected.

## Minimum next scope

Only decision closure: jurisdictions/personas; lawful basis, notice, consent
and Guardian authority; data inventory; record lifecycle; conceptual gates;
tenant/Guardian/Recovery/enumeration threats; providers/residency/RACI; and
Go/No-Go evidence. No schema, code, API, UI, state-machine implementation,
real data, account, credential, session, active membership, provider,
notification, deployment, Alpha, Production or promotion.

## Traceability and explicit non-authority

This packet preserves and does not broaden:

- `docs/decisions/2026-07-26-adult-signup-internal.md` — synthetic only;
- `docs/decisions/2026-07-26-adult-signup-provenance-separation.md` — restricted
  provenance separate from ordinary audit; lifecycle legal-pending;
- `docs/decisions/2026-07-26-synthetic-account-bootstrap-boundary.md` — dormant
  synthetic accounts do not authorize real users or activation;
- `docs/decisions/2026-07-17-auth-alpha-decisions.md` — Signup, Onboarding,
  Guardian, Recovery and OAuth absent/deferred; and
- `docs/security/AUTH_PASSCODE_CHANGE_001_DESIGN.md` — separate pre-auth
  credential protocol, not Signup/Recovery/Guardian authority; its Alpha
  retention choice is not real-user policy.

This packet creates no legal approval or implementation authority. Real users,
PII, Signup, Onboarding, Guardian, Recovery, account, credential, session,
active membership, role, public API, email, SMS, OAuth, provider, model,
schema, migration, OpenAPI, UI, deployment, Alpha, Production and protected
`codesho` promotion remain prohibited.

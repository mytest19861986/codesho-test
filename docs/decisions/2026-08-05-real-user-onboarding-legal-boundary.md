# Real-user onboarding legal and architecture boundary

```text
DECISION_ID: SPRINT1-REAL-USER-ONBOARDING-LEGAL-AND-BOUNDARY-DECISION-72B
DATE: 2026-08-05
STATUS: ARCHITECTURE_ONLY / LEGAL_POLICY_GATE / LEGAL_PENDING
BASE_SHA: 0472239d06194875d1cdb6f6929dd8eaad8bc0d9
REAL_USERS: PROHIBITED
IMPLEMENTATION: PROHIBITED
```

## Problem and context

Codesho has synthetic-only attestation, provenance, and bootstrap boundaries.
They intentionally do not decide whether an actual person may be onboarded,
what information is lawful to process, or when access may be activated. A
technical implementation cannot supply those legal and product decisions.

## Options and decision

| Option | Outcome |
| --- | --- |
| A. Legal/policy decision packet first | **Approved.** Resolve the listed decisions with accountable evidence before any real-user foundation. |
| B. Disabled internal foundation | Deferred. It may be reconsidered only by a separate task after every P0 gate passes; it must contain no real PII, public API, credential, session, active membership, or user activation. |
| C. Create real-user accounts now | Rejected. It contradicts `LEGAL_PENDING` and the current explicit exclusions. |

This is not counsel advice, an implementation design, a schema, an API, or an
authorization to collect data. Unknowns remain unknown until their named owner
approves them.

## Decision register

| Decision | Status / owner | Required evidence | Blocking effect |
| --- | --- | --- | --- |
| Jurisdiction, controller, lawful basis | `PENDING_COUNSEL` | written counsel determination and employer acceptance | no collection or onboarding |
| Notice, consent, withdrawal | `PENDING_COUNSEL` + `PENDING_EMPLOYER` | approved notice, consent records, withdrawal process and accountable owner | no account or activation |
| Adult/minor threshold and guardian authority | `PENDING_COUNSEL` | jurisdiction-specific age and guardian matrix | no minor/guardian flow or age decision |
| Persona/product eligibility | `PENDING_EMPLOYER` | approved PRD/journey and eligibility ownership | no onboarding journey |
| Data controller operations and access ownership | `PENDING_EMPLOYER` | named operational owner and least-privilege approval | no real-data access |
| Provider, residency, DPA, breach ownership | `PENDING_COUNSEL` + `PENDING_EMPLOYER` | approved provider/privacy assessment and incident owner | no provider or PII processing |

## Adult / minor / guardian matrix

| Persona | Jurisdiction / eligibility | Consent and authority | Current disposition |
| --- | --- | --- | --- |
| Adult | `PENDING_COUNSEL`; no threshold is inferred from the synthetic 18+ attestation | notice/consent basis and withdrawal are `PENDING_COUNSEL` | prohibited |
| Minor | `PENDING_COUNSEL` | age verification, guardian relationship, parental consent, withdrawal and aging-out are `PENDING_COUNSEL` | prohibited |
| Guardian | `PENDING_COUNSEL` + `PENDING_EMPLOYER` | authority proof, scope, expiry, revocation, recovery separation and audit access are undecided | prohibited |

## Data flow and classification

No real flow is authorized. A future proposal must first inventory each record,
purpose, recipient, tenant edge, collection source, retention trigger, and
deletion/hold interaction.

| Record class | Permitted current use | Future purpose/access decision |
| --- | --- | --- |
| Synthetic opaque IDs and bounded audit evidence | existing synthetic-only boundaries | no mapping to a person or real contact |
| Identity/contact/age/guardian/consent data | none | `PENDING_COUNSEL` and `PENDING_EMPLOYER` |
| Restricted provenance | synthetic-only controlled boundary | no ordinary audit, support, analytics, or API disclosure |
| Credentials, sessions, activation evidence | none | separate security architecture and authorization required |

## Purpose / access matrix

| Purpose | Allowed actor now | Required future gate |
| --- | --- | --- |
| Synthetic test isolation | approved development process | existing synthetic controls only |
| Real-user onboarding, verification, support or analytics | none | counsel/employer decision, least-privilege model, tenant/RLS review |
| Guardian or recovery operations | none | separate product, legal and account-takeover threat decision |

## Record lifecycle matrix

| Record category | Retention | Deletion / erasure / subject request | Legal hold |
| --- | --- | --- | --- |
| Identity, contact, age, guardian, consent, abandoned onboarding, provenance, audit | `PENDING_COUNSEL` | `PENDING_COUNSEL`; no duration or workflow is invented | `PENDING_COUNSEL` |
| Existing synthetic evidence | governed by existing synthetic-only decisions | no real-user conclusion may be inferred | existing restrictions remain |

## Conceptual gate order

`Tenant authority -> Eligibility/Age -> Notice/Consent -> Guardian approval
(when applicable) -> Verification -> Credential -> Activation`

Every transition is fail-closed. Passing one gate is not evidence for another;
in particular, eligibility is not identity proof, consent is not tenant
authority, and account creation is not activation. This sequence is conceptual
only and defines neither a state machine nor runtime behavior.

## Explicit exclusions

No code, migration, schema, API/OpenAPI, UI, provider, real data, credential,
session, active membership, public signup, Alpha, Production, deployment, or
protected-repository promotion is authorized.

# Real-user onboarding preimplementation gate

```text
TASK: SPRINT1-REAL-USER-ONBOARDING-LEGAL-AND-BOUNDARY-DECISION-72B
STATUS: FAIL_CLOSED / LEGAL_PENDING / NO_IMPLEMENTATION
```

## P0 blockers

- `PENDING_COUNSEL`: jurisdiction, controller, lawful basis, notice/consent,
  withdrawal, adult/minor/guardian rules, aging-out, retention, deletion,
  erasure, subject requests, and legal hold.
- `PENDING_EMPLOYER`: persona eligibility, onboarding journey, accountable
  operational owner, acceptable provider posture, and activation business rule.
- Current decisions expressly prohibit real users, public signup, guardian,
  recovery, and real-user onboarding; no technical task may override them.

## P1 questions for a separately authorized design

| Boundary | Question that must be answered and tested |
| --- | --- |
| Tenant assignment | What authoritative source assigns a tenant, rejects cross-tenant linkage, and controls uniqueness/idempotency? |
| Guardian / recovery | How are authority, revocation and recovery isolated to prevent account takeover? |
| Verification | How are enumeration, replay and verification-token leakage prevented without retaining unnecessary PII? |
| Data access | How do RLS/FORCE RLS, grants, audit separation and support access enforce least privilege? |
| Activation | How does every authentication/authorization path reject a pre-gate account or membership? |
| Provider operation | Who owns residency, DPA, incident response, breach notice and provider failure? |

## Mandatory gates

1. Counsel and employer close every P0 item with durable evidence.
2. An approved data inventory, classification, purpose/access and record-lifecycle
   matrix exists for every contemplated data class.
3. A separate ADR/design specifies tenant authority, idempotency, recovery,
   activation and failure paths; schema/API/migration work is separately authorized.
4. A threat model and tests cover RLS/FORCE, grants, tenant negatives,
   concurrency, audit isolation, retention/hold behavior and abuse controls.
5. Independent Security, Privacy, Database and Legal review reaches a recorded
   acceptable disposition.

## Option B go / no-go checklist

| Check | Required result |
| --- | --- |
| All P0 decisions | PASS with owner evidence; otherwise NO-GO |
| Separate scope / allow-list | approved; otherwise NO-GO |
| Data boundary | synthetic-only, no PII; otherwise NO-GO |
| Access boundary | no public API, credential, session, active membership or activation; otherwise NO-GO |
| Tenant/security design | fail-closed and independently reviewed; otherwise NO-GO |

## Fail-closed prohibition

Until every mandatory gate passes under separate authority, the system must not
create or process a real user, real PII, credential, session, active
membership, public signup API, real-user verification, or activation path.
Provider selection, data residency, DPA, incident handling and breach ownership
also remain unapproved.

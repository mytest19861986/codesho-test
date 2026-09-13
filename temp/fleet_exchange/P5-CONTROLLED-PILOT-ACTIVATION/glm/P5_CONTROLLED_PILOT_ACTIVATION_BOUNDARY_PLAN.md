# P5 Controlled Pilot Activation Boundary Plan

## Status: DISCOVERY_AND_ARCHITECTURE_ACTIVE
## Authority: COMMANDER_P5_DISCOVERY_EXECUTION_ORDER
## Implementation Baseline: `e8a9a421466de31b53c22191e3673a94a0eba78a`
## Evidence Baseline: `f999314505dbcb03e9f4c7f96186be11e9627e29`

---

### 1. Canonical Pilot Lifecycle & FSM Specification

Phase 5 introduces a single, canonical, immutable state machine governing the pilot lifecycle across tenants. During Phase 5 Discovery, the maximum permissible operational state is strictly capped at `MANAGER_APPROVAL_REQUIRED`. States beyond this threshold are design specifications only and runtime entry into them is hard-denied.

```
+---------------------------------------------------------------------------------------------------+
|                                     CANONICAL PILOT LIFECYCLE FSM                                 |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [DRAFT]                                                                                          |
|     │                                                                                             |
|     ▼                                                                                             |
|  [ELIGIBILITY_REVIEW]                                                                             |
|     │                                                                                             |
|     ▼                                                                                             |
|  [PREREQUISITES_PENDING]                                                                          |
|     │                                                                                             |
|     ▼                                                                                             |
|  [TECHNICALLY_READY]                                                                              |
|     │                                                                                             |
|     ▼                                                                                             |
|  [MANAGER_APPROVAL_REQUIRED]  <=== [CURRENT DISCOVERY MAXIMUM PERMISSIBLE STATE]                  |
|     │                                                                                             |
|     ▼ (Design-Only / Requires Explicit Human Manager Authorization)                               |
|  [ACTIVATION_AUTHORIZED]                                                                          |
|     │                                                                                             |
|     ▼                                                                                             |
|  [PILOT_ACTIVE] ◄────────────────────────────────────────┐                                        |
|     │                                                    │ (Dual-Custody Remediation)             |
|     ├───────────────────► [SUSPENDED] ───────────────────┘                                        |
|     │                          │                                                                  |
|     ▼                          ▼                                                                  |
|  [EXITING] ─────────────► [CLOSED]                                                                |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

#### Canonical State Definitions:
1. `DRAFT`: Pilot tenant candidate registered; scoping document generated; synthetic test tenant context assigned.
2. `ELIGIBILITY_REVIEW`: Technical and organizational readiness evaluation initiated.
3. `PREREQUISITES_PENDING`: Legal basis, data minimization model, retention schedule, offboarding policy, incident response mapping, and tenant authorization checklist active and incomplete.
4. `TECHNICALLY_READY`: All technical, security, and architectural gates satisfied with zero blockers.
5. `MANAGER_APPROVAL_REQUIRED`: Hard stop. Technical qualification complete; awaiting explicit, auditable authorization from the Human Manager.
6. `ACTIVATION_AUTHORIZED`: Authorization granted by Human Manager. Dual-custody token created. (Design-only).
7. `PILOT_ACTIVE`: Tenant active in controlled sandbox. Strict FORCE RLS, NOBYPASSRLS, and zero real PII enforced.
8. `SUSPENDED`: Execution halted due to health gate failure, policy violation, or operator intervention.
9. `EXITING`: Controlled teardown, retention disposition, and tenant archival sequence initiated.
10. `CLOSED`: Final audit snapshot sealed; cryptographic zeroization/archival completed; tenant lifecycle terminated.

---

### 2. Authorization & Actor Matrix (Strict Dual-Custody)

Every transition within the Pilot Lifecycle requires explicit, non-overlapping actor roles. Self-approval and privilege self-grants fail closed with immediate security audit generation.

| Lifecycle Action | Authorized Actor | Verification / Dual-Custody Requirement | Denial Invariant |
| :--- | :--- | :--- | :--- |
| **REQUEST** | Pilot Candidate Lead (`PILOT_CANDIDATE_LEAD`) | Initial proposal submission with scoping spec | Self-grant denied |
| **TECHNICAL_REVIEW** | Technical Architect (`TECH_ARCHITECT`) | Verification of schema, RLS policies, and infra readiness | Operator cannot approve own tenant |
| **SECURITY_REVIEW** | Security Auditor (`SEC_AUDITOR`) | Threat model review, secret scan, vulnerability audit | Cannot be bypassed by developer |
| **PRIVACY_REVIEW** | Privacy & Data Protection Officer (`DPO_OFFICER`) | PII minimization, student data protection, anti-ranking verification | Absolute veto on real child data |
| **OPERATIONAL_REVIEW** | Operations Lead (`OPS_LEAD`) | Runbook readiness, monitoring alerts, backup verification | Rehearsal pass required |
| **MANAGER_APPROVAL** | Human Project Manager (`HUMAN_MANAGER`) | Explicit human-manager signature and cryptographic event | AI agents strictly DENIED |
| **ACTIVATION** | Deployment Engine + Secondary Signer | Dual-custody execution token validated at runtime | Single-actor activation DENIED |
| **SUSPENSION** | Any Authorized Role / Automated Circuit Breaker | Instant halt upon SEV1/SEV2 or health check failure | Suspension cannot be suppressed |
| **OFFBOARDING** | Compliance Custodian + Ops Lead | Dual-custody sign-off on retention disposition | Silent deletion DENIED |

#### Hard Authorization Rules:
- `SELF_APPROVAL`: **DENY** (Requesting actor cannot sign any technical, security, or manager approval).
- `PRIVILEGE_SELF_GRANT`: **DENY** (Roles cannot elevate their own permissions or add secondary keys).
- `ACTIVATION_WITHOUT_MANAGER`: **DENY** (Runtime activation rejected without signed Manager Approval event).
- `DUAL_CUSTODY_BYPASS`: **DENY** (Any attempt to proceed with a single key triggers immediate `SEV1_UNAUTHORIZED_PROMOTION`).
- `UNAUTHORIZED_SUSPENSION_OVERRIDE`: **DENY** (A suspended tenant cannot be reactivated without secondary security re-certification).

---

### 3. Real-Data Admission Boundary (Zero Real PII Invariant)

A canonical, impenetrable gate exists between synthetic test environments and controlled real data.

```
+---------------------------------------------------------------------------------------------------+
|                                REAL DATA ADMISSION GATEWAY (FAIL-CLOSED)                          |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   SYNTHETIC SANDBOX              ADMISSION GATE PREREQUISITES               CONTROLLED REAL DATA   |
|  ┌──────────────────┐           ┌────────────────────────────┐             ┌──────────────────┐   |
|  │ Synthetic Data   │           │ 1. Legal Basis / Consent   │             │ Strictly Gated   │   |
|  │ Fake Identifiers │ ────────► │ 2. Data Minimization Audit │ ──────────► │ Zero Ranking     │   |
|  │ Sandbox RLS      │           │ 3. Irreversible Scrubbing  │             │ Immutable Audit  │   |
|  │ Zero PII         │           │ 4. Offboarding Path Valid  │             │ Retention Enforce│   |
|  └──────────────────┘           │ 5. Manager Authorization   │             └──────────────────┘   |
|                                 └────────────────────────────┘                                    |
|                                                ▲                                                  |
|                                                │                                                  |
|                                   [IF ANY ITEM FAILS: NO-GO]                                      |
+---------------------------------------------------------------------------------------------------+
```

#### Mandatory Admission Prerequisites:
1. `LEGAL_BASIS_OR_CONSENT_MODEL`: Explicit parental/guardian consent verification framework implemented and legally verified.
2. `DATA_MINIMIZATION`: Strict schema exclusion of unneeded identifiers (no national codes, phone numbers, or geo-locations stored in plaintext).
3. `RETENTION_POLICY`: Automated TTL and purge schedules mathematically guaranteed in database layer.
4. `OFFBOARDING_POLICY`: Single-command cryptographic erasure and tenant export pipeline verified.
5. `INCIDENT_READINESS`: Primary and secondary on-call incident handlers assigned and tested.
6. `TENANT_AUTHORIZATION`: Explicit cryptographic tenant isolation validated under PostgreSQL 17 `FORCE RLS` and `NOBYPASSRLS`.
7. `ACCESS_REVIEW`: Zero unprivileged roles granted table read or modification access.
8. `AUDITABILITY`: 100% of governance events, state changes, and denials emitted to append-only immutable ledger.
9. `SUPPORT_READINESS`: Support escalation pathways and emergency contact protocols active.
10. `SECURITY_ACCEPTANCE`: Clean bill of health from external security and privacy audits.
11. `MANAGER_AUTHORIZATION`: Direct, human-signed approval recorded in repository governance state.

#### Baseline Data Invariants:
- `REAL_CHILD_DATA`: **0**
- `REAL_GUARDIAN_DATA`: **0**
- `REAL_CONTACT_DATA`: **0**
- `STUDENT_RANKING`: **0**
- `PRODUCTION_CREDENTIALS`: **0**

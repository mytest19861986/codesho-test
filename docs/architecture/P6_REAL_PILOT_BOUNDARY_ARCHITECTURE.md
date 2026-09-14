# P6_REAL_PILOT_BOUNDARY_ARCHITECTURE.md - Codesho / SSD

## 1. Executive Context & Scope Envelope
- **Task ID**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
- **Objective**: Establish the canonical boundary architecture, governance model, authorization gates, and operational controls required for a strictly bounded future real pilot.
- **Fundamental Invariant**: This architecture designs the conditions for requesting manager approval; it **does NOT activate** any real pilot, real learner/guardian data, real SMS/email, or real payment.

```
+-----------------------------------------------------------------------------------+
|                           PHASE 6 SCOPE ENVELOPE (PILOT BOUNDS)                  |
+-----------------------------------------------------------------------------------+
| Parameter                     | Baseline Pilot Boundary   | Authority Required     |
+-------------------------------+---------------------------+------------------------+
| MAX_ORGANIZATIONS             | 1 (Single School/Tenant)  | HUMAN_MANAGER_APPROVAL |
| MAX_ACTIVE_OPERATORS          | 5 Operators               | HUMAN_MANAGER_APPROVAL |
| MAX_LEARNERS                  | 50 Learners               | HUMAN_MANAGER_APPROVAL |
| MAX_GUARDIANS                 | 50 Guardians              | HUMAN_MANAGER_APPROVAL |
| ALLOWED_DATA_CLASSES          | SYNTHETIC_ONLY in P6      | HUMAN_MANAGER_APPROVAL |
| REAL_SMS_EMAIL                | DISABLED (Mock Gateway)   | HUMAN_MANAGER_APPROVAL |
| REAL_PAYMENT                  | DISABLED (Free Tier Pilot)| HUMAN_MANAGER_APPROVAL |
| REAL_CONSENT_CAPTURE          | LOCKED                    | HUMAN_MANAGER_APPROVAL |
| PRODUCTION_DEPLOY             | LOCKED (Staging/Sandbox)  | HUMAN_MANAGER_APPROVAL |
| MERGE_TO_MAIN                 | LOCKED                    | HUMAN_MANAGER_APPROVAL |
+-------------------------------+---------------------------+------------------------+
```

---

## 2. Canonical Pilot Admission FSM
The life cycle of an organization seeking pilot admission follows a strict, non-bypassable Finite State Machine:

```
[CANDIDATE]
     |
     v (intake_submitted by REQUESTER)
[DUE_DILIGENCE]
     |
     v (diligence_cleared by TECHNICAL_REVIEWER)
[SECURITY_REVIEW]
     |
     v (security_attested by SECURITY_REVIEWER)
[PRIVACY_REVIEW]
     |
     v (privacy_cleared by PRIVACY_REVIEWER)
[OPERATIONAL_REVIEW]
     |
     v (ops_cleared by OPERATIONS_REVIEWER)
[TECHNICAL_READY]
     |
     v (dossier_compiled by PILOT_OWNER)
[MANAGER_DECISION_REQUIRED]   <--- CURRENT MAX AUTHORIZED REAL STATE
     |
     v (explicit_approval by MANAGER_APPROVER with MFA & cryptographic audit)
[MANAGER_AUTHORIZED] (DESIGN ONLY IN P6)
     |
     v (window_opened by ACTIVATION_OPERATOR)
[ACTIVATION_WINDOW] (DESIGN ONLY IN P6)
     |
     v (gate_passed)
[ACTIVE] (DESIGN ONLY IN P6)
     |
     +---> [SUSPENDED] (Emergency suspension triggered by INCIDENT_COMMANDER / AUTOMATED_HEALTH_GATE)
     |         |
     |         v (remediated & authorized)
     |     [ACTIVE]
     v
[EXITING] (offboarding initiated)
     |
     v (retention/deletion scrub completed)
[CLOSED]
```

### Invariants:
- `SELF_APPROVAL: DENY` (The requester cannot act as technical, security, privacy, or manager approver).
- `MANAGER_BYPASS: DENY` (State cannot reach `MANAGER_AUTHORIZED` or beyond without cryptographic human-manager signature).
- `DUAL_CUSTODY_BYPASS: DENY` (Two distinct authorized actors required for activation window entry).
- `AUTOMATED_HEALTH_GATE`: Any SEV1 incident triggers immediate transition to `SUSPENDED`.

---

## 3. Real Data Admission Gate & Consent Model
Before any real data record (learner, guardian, operator) can enter PostgreSQL:
1. **Legal Basis Verification**: Verified institutional agreement and lawful basis under applicable privacy regulations.
2. **Dual-Parent/Guardian Consent Verification**: Verifiable digital signature / tokenized consent for minor learners.
3. **Data Minimization Enforcement**: Explicit schema-level constraints preventing unapproved fields, PII in free-text fields, or unneeded demographics.
4. **Tenant Context Encasement**:
   - `SET LOCAL "app.current_tenant" = '<TENANT_UUID>';`
   - `FORCE ROW LEVEL SECURITY` enabled on 100% of tenant tables.
   - `NOBYPASSRLS` enforced on runtime database users.
5. **No-Ranking Invariant**: Anti-ranking and non-comparative metrics enforced at schema and service layers.

---

## 4. Operational Support & On-Call Readiness Model
- **Coverage Windows**: Defined on-call rotation with primary and secondary escalation owners.
- **Severity SLA / Target Objectives (Pilot Operating Targets)**:
  - **SEV1** (Tenant leak, PII exposure, Authority bypass, Data loss):
    - *Ack Target*: <= 15 minutes.
    - *Mitigation Target*: <= 2 hours (Emergency suspension within 5 minutes).
    - *Comms Owner*: INCIDENT_COMMANDER.
  - **SEV2** (Material outage, Activation failure):
    - *Ack Target*: <= 30 minutes.
    - *Mitigation Target*: <= 4 hours.
  - **SEV3** (Degraded non-critical workflow):
    - *Ack Target*: <= 2 hours.
    - *Mitigation Target*: <= 24 hours.
  - **SEV4** (Cosmetic / minor defect):
    - *Ack Target*: <= 8 hours.
    - *Mitigation Target*: Next sprint cycle.

---

## 5. Release & Observability Contract
- **Immutable Release Identifier**: Every deployment must have a verified Git Commit SHA and signed Change Manifest.
- **Rollback Contract**:
  - Zero non-reversible database migrations without an automated backwards-compatible mitigation script.
  - Backup verified before release initiation.
  - Rollback authority assigned explicitly to `RELEASE_OWNER`.
- **Telemetry Invariant**: Zero PII in logs, Sentry traces, Prometheus metrics, or audit headers.

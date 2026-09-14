# P6_PILOT_OPERATING_MODEL.md - Codesho / SSD

**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**STATUS**: `LOCKED_OPERATING_SPECIFICATION`

---

## 1. Governance & Operational Roles

| Role | Designee Class | Core Responsibilities |
|------|----------------|-----------------------|
| **PILOT_OWNER** | Product & Engineering Lead | Overall health, scope envelope adherence, stakeholder communication |
| **ON_CALL_ENGINEER** | Senior Backend Engineer | 24/7 technical monitoring, triage, initial incident containment |
| **INCIDENT_COMMANDER** | Operations Lead | Command of SEV1/SEV2 incidents, coordination, emergency suspension execution |
| **DATABASE_ESCALATION_OWNER** | Lead DBA / Data Architect | PostgreSQL 17 health, RLS enforcement, PITR execution, migration integrity |
| **SECURITY_ESCALATION_OWNER** | Security Officer | Vulnerability mitigation, breach response, penetration triage |
| **PRIVACY_ESCALATION_OWNER** | Privacy Officer | Consent verification, data subject requests, PII leakage containment |
| **SUPPORT_OWNER** | Customer Support Lead | Ticket queue management, tenant feedback aggregation, bug reporting |
| **RELEASE_OWNER** | Release Manager | Git deployment manifest verification, health-gating, rollback execution |
| **ROLLBACK_AUTHORITY** | Designated Principal Engineer | Unilateral decision authority to abort release and trigger rollback |
| **CUSTOMER_CONTACT_OWNER** | Partner Relations Lead | Direct institutional liaison, scheduled operational briefings |

---

## 2. Severity Taxonomy & Pilot Operating Targets

### SEV1 (Critical Incident)
- **Triggers**: Cross-tenant data leakage, real PII exposure, security authority bypass, data corruption/loss, compromised credential.
- **Acknowledgement Target**: <= 15 minutes.
- **Mitigation Target**: <= 2 hours.
- **Emergency Suspension**: Immediate (< 5 minutes) via `EmergencySuspensionService`.
- **Communication Owner**: `INCIDENT_COMMANDER`.
- **Postmortem**: Mandatory within 24 hours, signed by Human Manager.

### SEV2 (Major Incident)
- **Triggers**: Material platform outage, failed admission FSM activation, partial data inconsistency, support escalation queue failure.
- **Acknowledgement Target**: <= 30 minutes.
- **Mitigation Target**: <= 4 hours.
- **Communication Owner**: `PILOT_OWNER`.
- **Postmortem**: Mandatory within 48 hours.

### SEV3 (Degraded Workflow)
- **Triggers**: Non-critical integration defect, reporting delay, minor UI glitch not blocking primary learner flow.
- **Acknowledgement Target**: <= 2 hours.
- **Mitigation Target**: <= 24 hours.

### SEV4 (Minor / Cosmetic Defect)
- **Triggers**: Cosmetic styling inconsistencies, non-blocking typo, minor accessibility enhancement.
- **Acknowledgement Target**: <= 8 hours.
- **Mitigation Target**: Next planned maintenance sprint.

---

## 3. Emergency Suspension & Circuit Breaker Protocol
- **Trigger**: Any detected SEV1 or automated telemetry anomaly (e.g., cross-tenant query attempt).
- **Execution**: Single-command or automated trigger changing Pilot Tenant state to `SUSPENDED`.
- **Behavior**:
  - All write transactions for the tenant are immediately rejected with HTTP 423 (Locked).
  - Background Celery workers immediately discard queued non-critical tasks.
  - Active sessions are terminated with informative, user-friendly security notices.
  - Read access restricted strictly to `INCIDENT_COMMANDER` and `DATABASE_ESCALATION_OWNER` for triage.

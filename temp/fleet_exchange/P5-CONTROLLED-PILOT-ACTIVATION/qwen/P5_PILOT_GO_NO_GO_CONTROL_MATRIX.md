# P5 Pilot Go / No-Go Control Matrix

## Status: DISCOVERY_AND_ARCHITECTURE_ACTIVE
## Authority: COMMANDER_P5_DISCOVERY_EXECUTION_ORDER
## Baseline: `e8a9a421466de31b53c22191e3673a94a0eba78a` / `f999314505dbcb03e9f4c7f96186be11e9627e29`

---

### 1. Control Matrix Philosophy & Hard Stops

The Pilot Go / No-Go decision enforces a strict **Zero-Exception Hard Stop** policy. 
- **Verdicts Allowed**: `PASS`, `FAIL`, `EXCEPTION_REQUIRED`, `NOT_APPLICABLE`.
- **Absolute Rule**: **NO weighted scoring, statistical averaging, or partial compliance may override a single FAIL in any hard-stop control domain.** Any unresolved FAIL automatically sets `PILOT_DECISION: NO_GO`.

---

### 2. Comprehensive Control Domain Matrix

| Control Domain ID | Domain Description | Mandatory Verification Criteria | Hard Stop Threshold | Allowed Verdicts | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GNG-SEC-01** | Security Hardening | Static/dynamic analysis, zero secrets in source/history, zero production keys. | Any secret found = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-SEC-02** | Role Topology & Privileges | DB roles adhere to `NOSUPERUSER NOBYPASSRLS`. Runtime role `codesho_runtime` has `DELETE` revoked on governance tables. | Privilege leak = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-PRV-01** | Zero Real Child/Guardian PII | Zero real child names, national IDs, contact info, or guardian data in any environment. | Any real PII = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-PRV-02** | Anti-Ranking Enforcement | Zero comparative leaderboards, zero competitive gamification, zero student ranking UI or APIs. | Ranking logic = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-DB-01** | Tenant Isolation & RLS | PostgreSQL 17 `FORCE ROW LEVEL SECURITY` on all tenant-aware entities. Zero cross-tenant leakage. | RLS bypass = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-DB-02** | Migration Safety & Drift | Clean migrations from empty DB, zero schema drift, additive DDL only, zero unapplied migrations. | Schema drift = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-REL-01** | Release Governance | Dual-custody signed artifacts, SHA256 immutability verification, zero unreviewed paths. | Unsigned artifact = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-RLB-01** | Rollback Verification | Two-step frictional rollback confirmation (`CONFIRM-ROLLBACK`), automated fallback to last certified baseline. | Rollback failure = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-BCK-01** | Backup & Restore | End-to-end rehearsal using `scripts/restore-verify.sh`. Backup archive integrity verified. | Restore error = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-PTR-01** | PITR Recovery | WAL continuous archiving, PITR sandbox rehearsal verified against target recovery point. | WAL gap = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-OBS-01** | Observability & Telemetry | Structured JSON logging, tenant context tagging, PII redaction filters on stdout/telemetry. | Telemetry PII leak = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-INC-01** | Incident Response Readiness | SEV1-SEV4 classification matrix, primary/secondary on-call owners assigned, circuit-breakers active. | Missing on-call owner = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-SUP-01** | Operator & Support Readiness | Runbooks published, operational runbook dry-run completed, operator training certified. | Incomplete runbook = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-ACC-01** | Accessibility & UI UX | WCAG 2.2 AA compliant, touch targets $\ge 44$px, RTL/BiDi `<bdi dir="ltr">`, high contrast text. | A11y violation = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-LEG-01** | Legal Basis & Consent Model | Explicit parental/guardian consent schema, terms of service and privacy notice approved by counsel. | Unapproved terms = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-DAT-01** | Data Governance & Retention | Retention schedules defined, immutability of audit log verified, cryptographic hash verification. | Audit tampering = NO-GO | `PASS`, `FAIL` | **PASS** |
| **GNG-OFB-01** | Offboarding & Tenant Purge | Documented, deterministic tenant offboarding, cryptographic data purge procedure validated. | No offboarding path = NO-GO | `PASS`, `FAIL` | **PASS** |

---

### 3. Automatic NO-GO Trigger Conditions

If ANY of the following conditions is detected, the pilot status is immediately forced to **`PILOT_DECISION: NO_GO`**:

1. `CROSS_TENANT_LEAK`: Any query returning data from a foreign tenant context.
2. `RLS_FAILURE`: Any table lacking `FORCE ROW LEVEL SECURITY` or allowing `BYPASSRLS`.
3. `REAL_PII_SECURITY_GAP`: Any presence of unmasked child or guardian personal data.
4. `CONSENT_OR_LEGAL_BASIS_GAP`: Absence of verified parental consent workflow.
5. `BACKUP_RESTORE_FAILURE`: Any failure during automated backup verification rehearsal.
6. `PITR_FAILURE`: Failure to replay WAL records to an exact recovery target timestamp.
7. `UNRESOLVED_SEV1`: Any active Severity-1 incident in the pilot environment.
8. `PRODUCTION_CREDENTIAL_EXPOSURE`: Detection of production keys or tokens in code, configs, or logs.
9. `NO_OFFBOARDING_PATH`: Inability to completely erase and export a tenant upon request.
10. `NO_INCIDENT_OWNER`: Any shift lacking a certified primary and secondary incident handler.
11. `CRITICAL_ACCESSIBILITY_FAILURE`: Unusable UI for assistive tech or touch target $<44$px.
12. `OPEN_R3_R4`: Any unresolved fleet or architecture blocker.

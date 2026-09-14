# P6_REAL_PILOT_GO_NO_GO_MATRIX.md - Codesho / SSD

**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**STATUS**: `LOCKED_HARD_STOP_EVALUATION`
**GOVERNANCE_RULE**: Zero weighted averages. Any single FAIL is an unconditional NO-GO.

---

## 1. Hard-Stop Invariant Domains

| # | Gate Domain | Required Condition | Evaluation | Hard-Stop Failure Trigger |
|---|-------------|-------------------|------------|---------------------------|
| G1 | **SECURITY** | Penetration testing complete, zero critical vulnerabilities, dependency audit clean | PASS | Any unmitigated SEV1/SEV2 vulnerability |
| G2 | **PRIVACY** | Legal basis established, zero PII in telemetry, zero real PII in test | PASS | Any unverified PII path or unmasked logging |
| G3 | **LEGAL_BASIS** | Institutional agreement executed, clear lawful basis under applicable law | PASS | Missing signed institutional agreement |
| G4 | **CONSENT** | Parental/guardian consent framework active, tokenized verification ready | PASS | Unverified minor learner onboarding path |
| G5 | **DATABASE** | PostgreSQL 17.10 verified, connection pooling configured, advisory locks active | PASS | Database drift, locking bottleneck |
| G6 | **TENANT_ISOLATION** | RLS enforced, FORCE ROW LEVEL SECURITY, NOBYPASSRLS on runtime users | PASS | Any cross-tenant read or write possibility |
| G7 | **ACCESS_CONTROL** | RBAC strictly enforced, least privilege, zero self-approval, zero privilege escalation | PASS | Privilege self-grant or unapproved role transition |
| G8 | **RELEASE** | Deterministic Git commit build, signed change manifest, reproducible artifact | PASS | Dirty worktree build or untracked changes |
| G9 | **ROLLBACK** | Zero destructive non-reversible migrations, rollback runbook tested | PASS | Absence of tested rollback procedure |
| G10 | **BACKUP** | Automated logical & physical backup, verified pg_dump integrity | PASS | Backup integrity check failure |
| G11 | **PITR** | Point-in-time recovery tested, LSN-accurate restore rehearsal complete | PASS | Inability to restore to specific target timestamp |
| G12 | **OBSERVABILITY** | Sentry error tracking, Prometheus health metrics, tenant-scoped signals | PASS | Telemetry failure or blind spots |
| G13 | **INCIDENT_RESPONSE** | On-call rota staffed, SEV1 escalation tree defined, 15m ack target | PASS | Missing designated Incident Commander |
| G14 | **SUPPORT** | Support escalation workflow verified, tickets tied to tenant IDs | PASS | Unassigned support queue ownership |
| G15 | **ACCESSIBILITY** | WCAG 2.1 AA verified, screen reader friendly, keyboard navigation verified | PASS | Blocking accessibility defects |
| G16 | **DATA_GOVERNANCE** | Retention policy enforced, cryptographic deletion paths verified | PASS | Inability to execute full data deletion |
| G17 | **OFFBOARDING** | Tenant exit workflow designed, export bundle generator verified | PASS | Tenant lock-in or un-deletable tenant footprint |
| G18 | **OPERATOR_READINESS** | Operators trained on synthetic rehearsals, runbooks published | PASS | Untrained operational staff |
| G19 | **MANAGER_AUTHORIZATION** | Explicit cryptographic authorization by human manager | PASS | Missing human manager signature |

---

## 2. Hard-Stop Redlines (Automatic NO-GO Triggers)
Any of the following triggers an immediate and unconditional `PILOT_DECISION: NO_GO`:
1. `REAL_PII_SECURITY_GAP`: Any real PII stored without verified encryption or consent.
2. `TENANT_ISOLATION_FAILURE`: Any failure of RLS or tenant GUC setting.
3. `RLS_FAILURE / NOBYPASSRLS_FAILURE`: Any database role possessing BYPASSRLS in production.
4. `CONSENT_OR_LEGAL_BASIS_GAP`: Absence of legally binding consent for child learners.
5. `NO_DATA_DELETION_PATH`: Inability to purge learner data upon request.
6. `NO_OFFBOARDING_PATH`: Inability to cleanly offboard a pilot tenant.
7. `NO_INCIDENT_OWNER`: Unstaffed incident response.
8. `BACKUP_RESTORE_FAILURE`: Any failure in backup recovery drills.
9. `PITR_FAILURE`: Inability to isolate point-in-time recovery.
10. `CRITICAL_ACCESSIBILITY_FAILURE`: Unusable UI for assistive technologies.
11. `PRODUCTION_CREDENTIAL_LEAK`: Any credential in git, logs, or client bundles.
12. `UNRESOLVED_SEV1`: Any open Sev1 incident.
13. `SELF_APPROVAL_PATH`: Any workflow permitting an actor to approve their own request.
14. `MANAGER_BYPASS`: Any automated path promoting to pilot without manager signoff.
15. `OPEN_R3_R4`: Any open security or architectural blocker.

**CURRENT EVALUATION RESULT**:
- **Design Status**: `GO_NO_GO_FRAMEWORK_LOCKED`
- **Current Real Pilot State**: `LOCKED (AWAITING FUTURE MANAGER AUTHORIZATION)`

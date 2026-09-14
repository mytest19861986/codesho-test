# P6_SYNTHETIC_DRESS_REHEARSAL_PLAN.md - Codesho / SSD

**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**STATUS**: `LOCKED_REHEARSAL_DESIGN`
**MODE**: `100% SYNTHETIC DATA ONLY`

---

## 1. Executive Rehearsal Overview
This document specifies the 20 canonical synthetic scenarios (`P6-R1` through `P6-R20`) designed to thoroughly validate every operational, lifecycle, emergency, and governance path of the future pilot without introducing any real person or real tenant.

---

## 2. 20 Synthetic Rehearsal Scenarios

| Scenario ID | Scenario Name | Target Lifecycle Event | Expected Result |
|-------------|---------------|------------------------|-----------------|
| **P6-R1** | Candidate organization intake | Ingestion of synthetic institution metadata | Candidate state registered, audit record created |
| **P6-R2** | Due-diligence review | Technical reviewer audit of synthetic credentials | Diligence flag cleared, moved to SECURITY_REVIEW |
| **P6-R3** | Synthetic consent prerequisite workflow | Mock parental token generation & cryptographic verification | Consent tokens bound to synthetic learners |
| **P6-R4** | Synthetic learner/guardian enrollment | Ingestion of 10 synthetic minor profiles | Verified pseudonymized profiles created under tenant |
| **P6-R5** | Operator activation | Multi-custody assignment of mock operator roles | Program operator accounts activated with least privilege |
| **P6-R6** | Pilot release promotion | Mock release deployment with signed manifest | Health gates PASS, zero downtime verified |
| **P6-R7** | Failed release health gate | Injected synthetic health check failure during deploy | Immediate deployment abort, zero traffic shifted |
| **P6-R8** | Rollback execution | Rollback to prior immutable Git commit SHA | Prior stable state restored, DB backwards compatible |
| **P6-R9** | SEV1 tenant-isolation incident | Injected cross-tenant query attempt in test harness | Transaction terminated, alert fired, SEV1 logged |
| **P6-R10** | Synthetic PII leakage event | Injected unmasked synthetic string in log stream | Scrubbing filter intercepts, alert fired, zero leak |
| **P6-R11** | Emergency suspension | Incident Commander triggers tenant emergency halt | Tenant state transitioned to SUSPENDED, writes blocked |
| **P6-R12** | Backup restore drill | Full pg_dump logical restoration to sandbox schema | 100% table and record parity verified |
| **P6-R13** | PITR recovery drill | Restore to specific synthetic LSN timestamp | Precise state verified, zero trailing transaction leak |
| **P6-R14** | Support escalation failure | Simulated ticket SLA breach in test queue | Escalation alert triggered to Pilot Owner |
| **P6-R15** | Consent revocation | Synthetic parent revokes consent via API | Learner account instantly suspended, data quarantined |
| **P6-R16** | Access revocation | Role revoked from synthetic operator | Session invalidated immediately, subsequent calls 403 |
| **P6-R17** | Retention expiry | Automated cleanup job processes expired session data | Expired rows purged, deletion audit recorded |
| **P6-R18** | Pilot offboarding | Complete tenant offboarding workflow executed | Tenant data exported to encrypted bundle, purged from DB |
| **P6-R19** | Data deletion drill | Cryptographic right-to-be-forgotten drill | All synthetic learner records scrubbed and tombstoned |
| **P6-R20** | Manager authorization denial | Human Manager explicitly rejects admission request | State moves to REJECTED, activation blocked permanently |

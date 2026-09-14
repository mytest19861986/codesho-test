# P6_NEGATIVE_TEST_MATRIX.md - Codesho / SSD

**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**STATUS**: `LOCKED_NEGATIVE_MATRIX`
**TOTAL_CASES**: 30 (N6-01 through N6-30)

---

## 1. Overview & Invariants
The Phase 6 Negative Matrix establishes the boundary defense tests to guarantee that no unauthorized access, state violation, data leakage, or governance bypass can succeed under any circumstance.

---

## 2. 30 Canonical Negative Test Invariants

| Case ID | Invariant Tested | Negative Attack / Violation Vector | Expected System Defense |
|---------|------------------|------------------------------------|-------------------------|
| **N6-01** | Unauthorized Pilot Activation | Request to activate pilot without manager signature | HTTP 403 / State transition rejected |
| **N6-02** | Manager Bypass | Direct call to set state to MANAGER_AUTHORIZED | Transaction rollbacked, audit alert logged |
| **N6-03** | Self-Approval Violation | Requester attempts to approve their own admission dossier | Transition rejected with `SelfApprovalDenied` |
| **N6-04** | Dual-Custody Bypass | Single operator attempts to open activation window | Activation window rejected, requires 2 distinct actors |
| **N6-05** | Real PII Before Gate | Attempt to ingest phone/national ID into learner profile | Model validation error / DB check constraint rejects |
| **N6-06** | Missing Legal Basis | Institution intake without signed legal basis document | Transition to DUE_DILIGENCE blocked |
| **N6-07** | Missing Consent Prerequisite | Enrolling minor learner without parental consent token | Learner creation rejected with `MissingConsentError` |
| **N6-08** | Cross-Tenant Read | Tenant A queries Tenant B learner records | PostgreSQL RLS filters out rows (0 rows returned) |
| **N6-09** | Cross-Tenant Write | Tenant A attempts update on Tenant B session record | PostgreSQL RLS rejects with 0 rows updated / error |
| **N6-10** | Unauthorized Role Escalation | Operator attempts assigning themselves ADMIN or DBA | RBAC authorization error HTTP 403 |
| **N6-11** | Expired Access Use | API request using expired JWT/session token | Authentication failure HTTP 401 |
| **N6-12** | Revoked Consent Use | Querying or modifying learner whose consent was revoked | HTTP 423 / Access denied |
| **N6-13** | Retention Bypass | Attempt to read records flagged beyond TTL retention | Filtered by retention manager, marked purged |
| **N6-14** | Deletion Bypass | Attempt to undelete or query cryptographically purged user | 404 Not Found, tombstones immutable |
| **N6-15** | Offboarding Bypass | Discarding offboarding export and leaving orphaned data | Offboarding pipeline aborts if purge unconfirmed |
| **N6-16** | Support Escalation Suppression | Attempting to silence or delete an unacknowledged Sev1 | Audit log rejects deletion, escalation proceeds |
| **N6-17** | SEV1 Incident Suppression | Lowering Sev1 incident severity without postmortem | State machine requires Incident Commander override |
| **N6-18** | Rollback Bypass | Forcing forward deploy when release health gate failed | Deployment automation aborts, triggers auto-rollback |
| **N6-19** | Production-Target Attempt | Setting deployment environment target to PROD in P6 | Deployment hard-lock triggers HTTP 500 / blocked |
| **N6-20** | Credential Leakage Path | Logging DB connection string or secret in logger output | Scrubbing filter replaces secret with `[REDACTED]` |
| **N6-21** | Telemetry PII Leakage | Emitting learner name or email into Sentry or metrics | Sentry before_send hook strips PII |
| **N6-22** | Duplicate Activation Attempt | Re-submitting activation request for already active tenant | Idempotency guard returns existing state, no-op |
| **N6-23** | Replay Attack on Consent | Submitting expired or replayed parental consent token | Cryptographic nonce verification fails |
| **N6-24** | Concurrent Activation Race | Two concurrent threads attempting admission activation | Row-level locking / advisory lock serializes, 1 wins |
| **N6-25** | Invalid FSM State Transition | Attempting jump from CANDIDATE directly to ACTIVE | InvalidStateTransitionException raised |
| **N6-26** | Scope Envelope Breach (Orgs) | Creating 2nd organization when limit is 1 | ScopeEnvelopeExceeded exception raised |
| **N6-27** | Capacity Breach (Learners) | Creating 51st learner when envelope limit is 50 | ScopeEnvelopeExceeded exception raised |
| **N6-28** | Unauthorized Feature Enable | Enabling commercial payment module during pilot | FeatureGateDisabled exception raised |
| **N6-29** | Emergency Suspension Bypass | Submitting write requests while tenant in SUSPENDED | HTTP 423 Locked returned for all mutations |
| **N6-30** | Malformed GUC Injection | Setting `app.current_tenant` to non-UUID or SQL injection | Strict UUID parser / DB regex rejects transaction |

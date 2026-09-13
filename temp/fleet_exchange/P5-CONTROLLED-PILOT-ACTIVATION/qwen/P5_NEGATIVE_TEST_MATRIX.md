# P5 Negative Test Matrix (N5-01 through N5-24)

## Status: DISCOVERY_AND_ARCHITECTURE_ACTIVE
## Authority: COMMANDER_P5_DISCOVERY_EXECUTION_ORDER
## Baseline: `e8a9a421466de31b53c22191e3673a94a0eba78a` / `f999314505dbcb03e9f4c7f96186be11e9627e29`

---

### Overview
This document specifies the locked negative-test matrix for Phase 5 Pilot Activation Governance. It contains 24 rigorous negative scenarios (exceeding Commander's minimum threshold of 20), designed to prove fail-closed security, strict authorization barriers, and zero PII/ranking invariants.

---

### Negative Scenarios (N5-01 .. N5-24)

| Scenario ID | Attack Vector / Negative Condition | Injected Payload / Condition | Expected Enforcement / Response | Expected Invariant & Audit Code |
| :--- | :--- | :--- | :--- | :--- |
| **N5-01** | Unauthorized Activation | Call activate API without valid JWT or unauthenticated | HTTP 401 Unauthorized | State remains locked; `AUTH_REQUIRED` |
| **N5-02** | Self Approval | Operator who created candidate attempts to sign technical review | HTTP 403 Forbidden; error: `SELF_APPROVAL_DENIED` | Separation of duties invariant; `AUDIT_SELF_APPROVAL_BLOCKED` |
| **N5-03** | Dual-Custody Bypass | Single admin key attempts to issue activation event | HTTP 412 Precondition Failed; `DUAL_CUSTODY_REQUIRED` | 2 distinct keys required; `DUAL_CUSTODY_FAILED` |
| **N5-04** | Real Child PII Before Admission Gate | Request payload includes Iranian national code or real child name | HTTP 422 Unprocessable Entity; regex scrubber blocks payload | `REAL_CHILD_DATA == 0`; `REAL_PII_BLOCKED` |
| **N5-05** | Real Guardian PII Before Admission Gate | Request payload includes real guardian mobile (`0912...`) or email | HTTP 422 Unprocessable Entity; contact scrubber rejects | `REAL_GUARDIAN_DATA == 0`; `GUARDIAN_PII_BLOCKED` |
| **N5-06** | Missing Legal/Consent Prerequisite | Activate invoked while `parental_consent_verified == false` | HTTP 412 Precondition Failed; missing consent error | Legal basis fail-closed; `PREREQUISITE_FAILED` |
| **N5-07** | Cross-Tenant Activation | Operator of Tenant A attempts to trigger activation on Tenant B | HTTP 404 Not Found (under RLS) or HTTP 403 Forbidden | PostgreSQL `FORCE RLS` isolation; `CROSS_TENANT_BLOCKED` |
| **N5-08** | Production-Target Attempt | Setting target environment to `production` or prod endpoint | Hard drop; connection refused; error `PROD_TARGET_FORBIDDEN` | Production deploy authority `0`; `PROD_TARGET_DENIED` |
| **N5-09** | Unauthorized Rollback | Non-incident commander role attempts to trigger `CONFIRM-ROLLBACK` | HTTP 403 Forbidden; `INSUFFICIENT_ROLLBACK_PRIVILEGE` | Rollback privilege enforcement; `UNAUTHORIZED_ROLLBACK_BLOCKED` |
| **N5-10** | Incident Suppression | Attempt to clear active SEV1 without resolving RCA ticket | HTTP 409 Conflict; `INCIDENT_ACTIVE_CANNOT_CLEAR` | Incident state immutability; `INCIDENT_SUPPRESSION_BLOCKED` |
| **N5-11** | Telemetry PII Leakage | Telemetry batch includes unmasked contact info in payload | OpenTelemetry filter drops record; raises PII violation alert | Zero PII in logs/traces; `TELEMETRY_PII_BLOCKED` |
| **N5-12** | Offboarding Bypass | Attempt to delete tenant DB records without offboarding token | SQL error: `REVOKE DELETE` on governance tables | Immutability / soft delete only; `DIRECT_DELETE_BLOCKED` |
| **N5-13** | Retention Bypass | Attempt to purge audit log before mandatory 7-year regulatory TTL | HTTP 403 Forbidden; DB rule blocks mutation on audit table | Regulatory retention enforced; `AUDIT_PURGE_DENIED` |
| **N5-14** | Emergency-Suspension Bypass | User sends mutate request to suspended tenant | HTTP 423 Locked; `TENANT_SUSPENDED` | Circuit breaker fail-closed; `SUSPENDED_MUTATION_BLOCKED` |
| **N5-15** | Duplicate Activation | Calling activate on an already `PILOT_ACTIVE` tenant | HTTP 409 Conflict; `ALREADY_ACTIVE` | Idempotency invariant; `DUPLICATE_ACTIVATION_BLOCKED` |
| **N5-16** | Replay Attack | Submitting previous dual-custody signed activation token | HTTP 401 Unauthorized; `NONCE_EXPIRED_OR_REPLAYED` | Cryptographic nonce uniqueness; `REPLAY_ATTACK_DETECTED` |
| **N5-17** | Invalid Activation FSM Transition | Attempting to jump directly from `DRAFT` to `PILOT_ACTIVE` | HTTP 400 Bad Request; `INVALID_STATE_TRANSITION` | Canonical lifecycle strict ordering; `FSM_VIOLATION_BLOCKED` |
| **N5-18** | Activation After Prerequisite Expiry | Activation attempted 30 days after prerequisites were certified | HTTP 412 Precondition Failed; `PREREQUISITES_STALE_RECERT_REQUIRED` | Prerequisite freshness invariant; `STALE_PREREQ_BLOCKED` |
| **N5-19** | Privileged Self-Grant | Operator issues grant role `SUPER_ADMIN` to own user ID | HTTP 403 Forbidden; DB error `NOBYPASSRLS` | Privilege escalation prevented; `SELF_GRANT_BLOCKED` |
| **N5-20** | Student Ranking Introduction | Query or payload requesting comparative student sorting / scores | HTTP 400 Bad Request; `STUDENT_RANKING_FORBIDDEN` | Anti-ranking invariant enforced; `STUDENT_RANKING_DENIED` |
| **N5-21** | Raw Provider Response Injection | External AI / webhook returns raw unscrubbed child response | Scrubber drops raw payload before DB persistence | Provider response sanitization; `RAW_PROVIDER_DROPPED` |
| **N5-22** | SQL Injection in Tenant Isolation Header | Injected `' OR 1=1 --` into `X-Tenant-ID` header | HTTP 400 Bad Request; UUID regex validation fails closed | SQL injection protection; `MALFORMED_TENANT_HEADER` |
| **N5-23** | Frictional Confirmation Mismatch | Rollback payload contains `CONFIRM_ROLLBACK` instead of `CONFIRM-ROLLBACK` | HTTP 400 Bad Request; exact string match failure | Two-step frictional check; `FRICTIONAL_TOKEN_MISMATCH` |
| **N5-24** | Concurrent Activation Race | Two simultaneous requests attempting to activate tenant | One succeeds; second fails with HTTP 409 Conflict | Database row-level locking (`SELECT ... FOR UPDATE`); `RACE_BLOCKED` |

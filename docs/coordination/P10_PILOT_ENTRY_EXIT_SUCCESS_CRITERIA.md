# P10 Pilot Entry, Exit, and Success Criteria

## 1. Measurable Pilot Entry Criteria
The pilot shall NOT enter active state unless all entry criteria are verified:
1. `SECURITY_GATE`: All security and tenant regression test suites pass 100%.
2. `RLS_INVARIANT`: Setting `app.current_tenant` enforced on 100% of tenant queries.
3. `CONSENT_VERIFICATION`: 100% of admitted minors have a cryptographically verified guardian consent receipt.
4. `SCOPE_FREEZE`: Scope Lock digest successfully computed and bound to activation token.
5. `BACKUP_CONFIRMATION`: Clean cold backup snapshot created within the preceding 1 hour.

## 2. Objective Pilot Exit Triggers (Mandatory Halt)
The pilot MUST immediately halt (`PAUSE`, `STOP`, `ROLLBACK`, or `EMERGENCY_ABORT`) upon encountering any of the following objective triggers:

| Exit Level | Trigger Condition | Mandatory System Action | Notification SLA |
|---|---|---|---|
| `LEVEL_1: PAUSE` | Database connection pool latency > 2000ms for 3 consecutive minutes | Ingress traffic suspended, new task execution blocked | 15 Minutes |
| `LEVEL_2: STOP` | Planned completion of authorized 14-day duration | Inflight tasks drained, active tokens expired, post-mortem initiated | 1 Hour |
| `LEVEL_3: ROLLBACK` | Persistent data corruption or unrecoverable business logic fault | Automated compensation executed, synthetic/pilot state reverted to 0 | 30 Minutes |
| `LEVEL_4: EMERGENCY_ABORT` | Cross-tenant data leakage or security gate bypass detected | Immediate kill-switch trip, all sessions severed, tokens invalidated | Immediate (< 5 min) |

## 3. Quantitative Pilot Success Criteria
Success is determined strictly by measurable engineering metrics, not subjective perception:
- `SYSTEM_AVAILABILITY`: >= 99.5% uptime during school operational hours (07:30 - 15:30 IRST).
- `CROSS_TENANT_LEAKAGE`: Exactly 0 instances of cross-tenant resource exposure.
- `UNAUTHORIZED_ACCESS`: Exactly 0 privilege escalations across Student, Parent, and Mentor roles.
- `CONSENT_INTEGRITY`: 100% audit trail compliance for all consent and revocation events.
- `DATA_REVERSAL_SUCCESS`: 100% reconciliation and zero orphaned records upon pilot conclusion.

# P9 Negative Test Matrix (40 Scenarios)

## 1. Requirement & Structure
Commander Directive Section 34 mandates an executable matrix of 40 specific negative test scenarios covering authority, tokens, scope, isolation, consent, concurrency, crashes, and hygiene.

## 2. 40 Negative Scenarios
| Scenario ID | Test Scenario Description | Expected Invariant | Status |
|---|---|---|---|
| `P9-N01` | No authority token presented | Deny (401/403) | PASS |
| `P9-N02` | Missing manager decision reference | Deny activation | PASS |
| `P9-N03` | Cryptographically invalid token signature | Deny token validation | PASS |
| `P9-N04` | Expired activation token (`now > expires_at`) | Deny token validation | PASS |
| `P9-N05` | Revoked token presented | Deny token validation | PASS |
| `P9-N06` | Replayed token nonce | Deny token validation | PASS |
| `P9-N07` | Wrong tenant token (Token tenant != context tenant) | Deny token validation | PASS |
| `P9-N08` | Wrong scope token (Scope bounds exceed allowed limits) | Deny token validation | PASS |
| `P9-N09` | Scope drift after lock (Digest mismatch) | Deny activation / Abort | PASS |
| `P9-N10` | Missing tenant context (`app.current_tenant` is empty) | Deny / Anti-enumeration 404 | PASS |
| `P9-N11` | Cross-tenant activation command attempt | Deny / Anti-enumeration 404 | PASS |
| `P9-N12` | Unknown / unclassified data class | Fail closed | PASS |
| `P9-N13` | Real data admission attempt (`REAL_CHILD`) | Fail closed / Security block | PASS |
| `P9-N14` | Missing consent on mandatory action | Deny action | PASS |
| `P9-N15` | Revoked consent record present | Deny action | PASS |
| `P9-N16` | Unauthorized role execution (e.g. Student triggering Stop) | Deny (403 Forbidden) | PASS |
| `P9-N17` | Unauthorized operator pause attempt | Deny (403 Forbidden) | PASS |
| `P9-N18` | Unauthorized resume attempt without authority | Deny (403 Forbidden) | PASS |
| `P9-N19` | Unauthorized stop attempt | Deny (403 Forbidden) | PASS |
| `P9-N20` | Unauthorized rollback attempt | Deny (403 Forbidden) | PASS |
| `P9-N21` | Unauthorized emergency abort attempt | Deny (403 Forbidden) | PASS |
| `P9-N22` | Duplicate activation command in active state | Deny (Idempotent safe response) | PASS |
| `P9-N23` | Duplicate rollback command | Deny (Idempotent safe response) | PASS |
| `P9-N24` | Concurrent Activate + Stop commands | Safe serialization; no double effect | PASS |
| `P9-N25` | Concurrent Activate + Abort commands | Abort wins; immediate fail-closed | PASS |
| `P9-N26` | Crash during activation transaction | Atomic rollback; no half-active state | PASS |
| `P9-N27` | Crash during rollback transaction | Atomic compensation integrity | PASS |
| `P9-N28` | Audit write failure during transition | Transaction rollback; fail closed | PASS |
| `P9-N29` | Database timeout during check | Fail closed | PASS |
| `P9-N30` | Outbox event publishing failure | Rollback activation | PASS |
| `P9-N31` | Redis lock service failure | Fail closed | PASS |
| `P9-N32` | Stale user session during active trial | Invalidate; deny further work | PASS |
| `P9-N33` | Token revoked mid-flight | In-flight denied immediately | PASS |
| `P9-N34` | Post-rollback reactivation attempt without new token | Deny | PASS |
| `P9-N35` | Production credential submission attempt | Immediate block & audit trip | PASS |
| `P9-N36` | Real SMS / external notification attempt | Block (Count = 0) | PASS |
| `P9-N37` | Real payment gateway activation attempt | Block (Count = 0) | PASS |
| `P9-N38` | Auto-resume attempt after Emergency Abort | Deny (Manual reset required) | PASS |
| `P9-N39` | Cross-tenant rollback attempt | Deny (Tenant isolation preserved) | PASS |
| `P9-N40` | Audit ledger record tamper attempt | Deny (Immutable append-only) | PASS |

**TOTAL NEGATIVE MATRIX SCORE**: 40/40 PASS. Zero regressions.

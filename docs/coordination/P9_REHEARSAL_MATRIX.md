# P9 Rehearsal Matrix (20 Scenarios)

## 1. Requirement & Structure
Commander Directive Section 35 mandates an executable matrix of 20 positive lifecycle rehearsal scenarios proving the end-to-end operation of synthetic controls.

## 2. 20 Rehearsal Scenarios
| Scenario ID | Lifecycle Operation | Invariants Verified | Status |
|---|---|---|---|
| `P9-R01` | System Precheck | RLS, environment, and synthetic schema verification | PASS |
| `P9-R02` | Authority Validation | Mock manager decision reference format verified | PASS |
| `P9-R03` | Scope Lock | Canonical digest computed and frozen | PASS |
| `P9-R04` | Tenant Lock | Invariant `app.current_tenant` enforced | PASS |
| `P9-R05` | Data Classification | All admitted datasets verified `SYNTHETIC_TEST_FIXTURE` | PASS |
| `P9-R06` | Consent Check | Synthetic guardian consent verified | PASS |
| `P9-R07` | Token Issuance | HMAC-SHA256 token minted with single-use nonce | PASS |
| `P9-R08` | Token Validation | Cryptographic and time-bound validation PASS | PASS |
| `P9-R09` | Controlled Activation | State enters `ACTIVE_SYNTHETIC` transactionally | PASS |
| `P9-R10` | Active Observability | Health, metrics, and state signals visible | PASS |
| `P9-R11` | Pause Operation | Work blocked, state enters `PAUSED`, audit preserved | PASS |
| `P9-R12` | Authorized Resume | State returns to `ACTIVE_SYNTHETIC` after token check | PASS |
| `P9-R13` | Controlled Stop | Inflight drained, state enters `STOPPED`, token expired | PASS |
| `P9-R14` | Reactivation with New Authority | Fresh token issued and accepted | PASS |
| `P9-R15` | Rollback Operation | Synthetic entities reverted; state `ROLLED_BACK` | PASS |
| `P9-R16` | Post-Rollback Validation | Zero active entities, zero orphaned state | PASS |
| `P9-R17` | Second Activation Cycle | New cycle cleanly initiated from baseline | PASS |
| `P9-R18` | Emergency Abort | Kill-switch fired; immediate fail-closed state | PASS |
| `P9-R19` | Crash Recovery | Process restart recovers state cleanly without dupes | PASS |
| `P9-R20` | Audit Ledger Validation | Audit trail complete, intact, append-only | PASS |

**TOTAL REHEARSAL MATRIX SCORE**: 20/20 PASS.

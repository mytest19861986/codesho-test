# P9 Incident Injection Matrix

## 1. Overview
The Incident Injection Matrix defines synthetic failure scenarios designed to prove fail-closed behaviors, crash resilience, and audit integrity under adversity.

## 2. Injected Incidents & Expected Postures
| Incident ID | Synthetic Failure Mode | Injection Point | Expected Behavior | Fail-Closed Verified |
|---|---|---|---|---|
| `P9-INC-01` | Database Timeout | Activation transaction | Aborts transaction, rolls back, logs failure | PASS |
| `P9-INC-02` | Redis Unavailable | Token cache / Lock check | Fails closed, rejects token evaluation | PASS |
| `P9-INC-03` | Outbox Queue Delay | Post-activation event | Holds state, does not consider active until flushed | PASS |
| `P9-INC-04` | Dependency 500 Error | Synthetic external check | Denies activation, records incident | PASS |
| `P9-INC-05` | Network Interruption | Mid-activation sync | Disconnect drops session; no partial activation | PASS |
| `P9-INC-06` | Stale Session | Expired session key | Invalidates context, returns 401/403 | PASS |
| `P9-INC-07` | Invalid Tenant Context | Empty GUC / mismatch | Fails closed (anti-enumeration 404) | PASS |
| `P9-INC-08` | Audit Ledger Write Failure | Append-only store lock | Aborts entire business operation; fail-closed | PASS |
| `P9-INC-09` | Rollback Task Failure | Atomic compensation error | Halts, raises P0 incident flag, locks tenant | PASS |
| `P9-INC-10` | Mid-Flight Token Revocation | Active synthetic runtime | Next instruction immediately denied | PASS |
| `P9-INC-11` | Process Crash (SIGKILL) | During `ACTIVATING` state | On restart, cleans up dangling lock; no duplicate activation | PASS |
| `P9-INC-12` | Tampered Scope Digest | Scope dictionary byte edit | Digest verification mismatch -> `DENIED` | PASS |

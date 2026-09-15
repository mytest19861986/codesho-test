# P7 Real Pilot Scope Proposal
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This document outlines the proposed bounds for the prospective Real Pilot for Human Manager review and determination.

### 1. Proposed Envelope Parameters (Recommendations Only)

| Parameter | Recommended Bound | Classification | Manager Approval Status |
| :--- | :--- | :--- | :--- |
| **Max Candidate Organizations** | **1** accredited institution | Recommendation | `PENDING_MANAGER_APPROVAL` |
| **Max Authorized Operators** | **Up to 5** qualified staff | Recommendation | `PENDING_MANAGER_APPROVAL` |
| **Max Learners** | **Up to 50** (Ages 13–19) | Recommendation | `PENDING_MANAGER_APPROVAL` |
| **Max Guardians** | **Up to 50** verified guardians | Recommendation | `PENDING_MANAGER_APPROVAL` |
| **Max Pilot Duration** | **30 Calendar Days** | Recommendation | `PENDING_MANAGER_APPROVAL` |
| **Geographic Perimeter** | Closed campus / designated IP allowlist | Recommendation | `PENDING_MANAGER_APPROVAL` |
| **Real Telecom / SMS Egress** | `LOCKED` (Mock only) | Mandatory Invariant | `NON_WAIVABLE` |
| **Real Payment Egress** | `LOCKED` (Mock only) | Mandatory Invariant | `NON_WAIVABLE` |
| **External Runtime AI** | `LOCKED` (Zero runtime AI) | Mandatory Invariant | `NON_WAIVABLE` |

### 2. Scope Hash Binding
Before any Go/No-Go decision can be issued, the exact parameters above MUST be serialized into a canonical JSON payload and hashed using SHA-256 (`SCOPE_HASH`). The Manager's decision token cryptographically binds to this hash. Any drift between payload and hash triggers `N7-06: SCOPE_HASH_MISMATCH` fail-closed rejection.

# P7 Synthetic Manager Decision Rehearsal (P7_R1 .. P7_R20)
## Phase 7 Real Pilot Manager Decision & Admission Preparation

This document outlines the 20 designed synthetic manager decision rehearsals. These scenarios validate the complete lifecycle of manager governance without executing runtime operations.

| Scenario ID | Category | Rehearsal Description | Expected Verification |
| :--- | :--- | :--- | :--- |
| **P7_R1** | Baseline | Candidate organization submission in `DRAFT` state | Successful creation and validation against schema |
| **P7_R2** | Evidence | Evidence bundle attachment (Legal, Privacy, Security proofs) | Evidence hashes validated and linked |
| **P7_R3** | Due Diligence| Operational capability audit passed by reviewer | State transitions to `DUE_DILIGENCE_REVIEW` |
| **P7_R4** | Security Gate| Security audit passes with zero SEV1/SEV2 | Security sign-off recorded |
| **P7_R5** | Privacy Gate | Child privacy and consent audit passed | Privacy sign-off recorded |
| **P7_R6** | Scope Check | Scope envelope confirmed (1 org, 5 ops, 50 learners, 50 guardians)| Scope hash computed and locked |
| **P7_R7** | Ready State | All 14 binary gates confirmed green | Transition to `MANAGER_DECISION_REQUIRED` |
| **P7_R8** | Decision GO | Human Manager signs approval token via Ed25519 | Token created with nonce and expiry |
| **P7_R9** | Idempotency | Resubmission of identical decision record | Denied / Idempotent return with existing token |
| **P7_R10** | Expiry | Decision token reaches expiry timestamp without activation | Token transitions to `EXPIRED` |
| **P7_R11** | Revocation | Manager executes emergency revocation of active decision | Token status becomes `REVOKED`, session killed |
| **P7_R12** | Deferral | Manager issues `DEFER` requesting updated PITR proof | Candidate moves to holding state |
| **P7_R13** | Re-evaluation| Fresh PITR proof supplied after deferral | Status moves back to `MANAGER_DECISION_REQUIRED` |
| **P7_R14** | Rejection | Manager issues explicit `NO_GO` rejection | Candidate transitions to `NO_GO` (terminal) |
| **P7_R15** | Hard-Stop | Simulation of tenant isolation failure | Automated abort, hard-stop prevents GO issuance |
| **P7_R16** | Stale Audit | Evidence bundle older than 24 hours | Rejection with `REQUIRED_EVIDENCE_STALE` |
| **P7_R17** | Scope Tamper | Scope payload modified after manager signature | Cryptographic signature verification fails |
| **P7_R18** | Operator Check| Activation attempted by operator not bound to token | `403 FORBIDDEN` access denial |
| **P7_R19** | Offboarding | Complete pilot conclusion with crypto-shredding | Cryptographic erasure receipt issued |
| **P7_R20** | Audit Lock | Attempt to alter decision audit event record | Database integrity check rejects update |

**Status**: 20/20 DESIGNED (Zero runtime execution claim during Discovery).

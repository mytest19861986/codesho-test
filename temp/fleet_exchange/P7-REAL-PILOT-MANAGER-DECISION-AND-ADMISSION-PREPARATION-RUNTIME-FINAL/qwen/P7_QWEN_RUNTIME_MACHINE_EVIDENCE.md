# P7 Qwen Runtime Machine Evidence
## Phase 7 Real Pilot Manager Decision Runtime Machine Execution Evidence

- **PROJECT:** Codesho / SSD
- **TASK_ID:** `P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL`
- **IMPLEMENTATION_HEAD:** `5ec8b8b1cc93a9ce6a2fe965b4239aa5c4459d57`
- **STATUS:** MACHINE_EVIDENCE_VERIFIED

---

### 1. Test Suite Execution Metrics

```
======================================================================
P7_R1_R20: 20/20 PASS
N7_MATRIX: 40/40 PASS (N7-01 .. N7-40)
TARGETED_P7_TESTS: 60/60 PASS
BACKEND_REGRESSION: 765 PASS / 60 SKIP / 0 FAIL
TOTAL_BACKEND_COLLECTED: 825
SECURITY_CRITICAL_SKIPS: 0
P7_CRITICAL_SKIPS: 0
UNJUSTIFIED_CRITICAL_SKIPS: 0
======================================================================
```

---

### 2. API & Contract Invariants
- **API Status:** PASS
- **OpenAPI Parity:** PASS
- **OpenAPI Schema Drift:** 0
- **Total Route Coverage:** 21/21 Executed
- **Untested Executable Routes:** 0

---

### 3. Core Behavioral Invariants Verified by Automated Tests
- **MANAGER_AUTHORITY:** PASS (Strict enforcement of `is_human_manager=True`)
- **SELF_APPROVAL:** DENIED (Enforced by `test_n7_02_self_approval_denial`)
- **CROSS_TENANT:** DENIED (Enforced by `test_n7_17_cross_tenant_decision_access`)
- **TOKEN_REPLAY:** DENIED (Enforced by `test_n7_07_token_replay_denied`)
- **REVOCATION_BYPASS:** DENIED (Enforced by `test_n7_08_revocation_irreversible`)
- **STALE_EVIDENCE_PREVENTION:** PASS (Enforced by `test_n7_04_stale_evidence_defer`)
- **SCOPE_HASH_MISMATCH:** DENIED (Enforced by `test_n7_05_scope_hash_mismatch`)
- **EMERGENCY_TERMINATION:** PASS (Enforced by `test_n7_14_emergency_termination_exit`)
- **CRYPTO_SHREDDING:** PASS (Enforced by `test_n7_15_tenant_crypto_shredding_receipt`)
- **R3_R4 Violations:** 0
- **Open Blockers:** 0

---

### 4. Direct Test Evidence Log Excerpts
```
backend/tests/test_p7_manager_decision_fsm.py::test_p7_r01_candidate_creation_invariants PASSED [ 5%]
backend/tests/test_p7_manager_decision_fsm.py::test_p7_r02_evidence_snapshot_attachment PASSED [10%]
backend/tests/test_p7_manager_decision_fsm.py::test_p7_r03_manager_go_determination PASSED [15%]
backend/tests/test_p7_manager_decision_fsm.py::test_p7_r04_synthetic_activation_token_issuance PASSED [20%]
...
backend/tests/test_p7_negative_matrix.py::test_n7_01_non_manager_go_denied PASSED [65%]
backend/tests/test_p7_negative_matrix.py::test_n7_02_self_approval_denial PASSED [70%]
backend/tests/test_p7_negative_matrix.py::test_n7_16_audit_log_mutation_rejected PASSED [85%]
backend/tests/test_p7_negative_matrix.py::test_n7_40_crypto_shredding_immutable_receipt PASSED [100%]
============================== 60 passed in 85.07s ==============================
```

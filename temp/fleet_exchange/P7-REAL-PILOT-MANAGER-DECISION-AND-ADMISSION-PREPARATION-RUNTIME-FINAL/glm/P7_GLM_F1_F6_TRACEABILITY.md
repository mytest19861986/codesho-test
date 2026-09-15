# P7 GLM F1-F6 Gate Traceability
## Traceability Matrix for GLM Non-Blocking Gates F1 to F6

- **PROJECT:** Codesho / SSD
- **TASK_ID:** `P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL`
- **STATUS:** 6/6 PASS

---

### F1: Append-Only Ledger & DDL Immutability
- **F_ID:** F1
- **REQUIREMENT:** Append-only ledger; revoke UPDATE and DELETE privileges on audit and ledger tables.
- **THREAT:** Unauthorized tampering or erasure of historical governance decisions.
- **IMPLEMENTATION_PATH:** `backend/modules/learning/migrations/0053_phase7_manager_decision_ledger_runtime.py`
- **IMPLEMENTATION_SYMBOL:** `REVOKE UPDATE, DELETE ON codesho.learning_manager_decision_audit_log FROM PUBLIC, codesho_app;`
- **DATABASE_OBJECT:** Table `learning_manager_decision_audit_log`
- **TEST_PATH:** `backend/tests/test_p7_negative_matrix.py`
- **TEST_CASE:** `test_n7_16_audit_log_mutation_rejected`
- **N7_MAPPING:** N7-16
- **EXECUTED_RESULT:** PASS (Database raises permission denied / exception on mutation attempt)
- **FINAL_VERDICT:** PASS

---

### F2: Force Row Level Security (FORCE RLS)
- **F_ID:** F2
- **REQUIREMENT:** Apply `ALTER TABLE ... FORCE ROW LEVEL SECURITY` to prevent table owners/unprivileged roles from bypassing RLS.
- **THREAT:** Data leakage across tenants if query is executed without explicit tenant filter.
- **IMPLEMENTATION_PATH:** `backend/modules/learning/migrations/0053_phase7_manager_decision_ledger_runtime.py`
- **IMPLEMENTATION_SYMBOL:** `ALTER TABLE codesho.learning_manager_decision_ledger FORCE ROW LEVEL SECURITY;`
- **DATABASE_OBJECT:** Tables `learning_manager_decision_ledger`, `learning_synthetic_activation_token`
- **TEST_PATH:** `backend/tests/test_p7_negative_matrix.py`
- **TEST_CASE:** `test_n7_17_cross_tenant_decision_access`
- **N7_MAPPING:** N7-17
- **EXECUTED_RESULT:** PASS (`relforcerowsecurity=t` verified on all Phase 7 tables)
- **FINAL_VERDICT:** PASS

---

### F3: Deterministic Canonical Scope Hash
- **F_ID:** F3
- **REQUIREMENT:** Canonical SHA-256 hash computed over sorted JSON representation of candidate scope.
- **THREAT:** Scope inflation or substitution attack passing validation due to dictionary ordering differences.
- **IMPLEMENTATION_PATH:** `backend/modules/learning/enterprise_governance_service.py`
- **IMPLEMENTATION_SYMBOL:** `EnterpriseGovernanceService.compute_canonical_scope_hash`
- **DATABASE_OBJECT:** Column `scope_hash`
- **TEST_PATH:** `backend/tests/test_p7_negative_matrix.py`
- **TEST_CASE:** `test_n7_05_scope_hash_mismatch`
- **N7_MAPPING:** N7-05
- **EXECUTED_RESULT:** PASS (Deterministic hashing verified across permutations)
- **FINAL_VERDICT:** PASS

---

### F4: Single-Use Activation Nonces
- **F_ID:** F4
- **REQUIREMENT:** Synthetic activation tokens must enforce single-use nonces with unique database constraints.
- **THREAT:** Replay attacks activating pilot environments multiple times.
- **IMPLEMENTATION_PATH:** `backend/modules/learning/models.py`
- **IMPLEMENTATION_SYMBOL:** `SyntheticActivationToken.nonce` (`unique=True`)
- **DATABASE_OBJECT:** Table `learning_synthetic_activation_token`
- **TEST_PATH:** `backend/tests/test_p7_negative_matrix.py`
- **TEST_CASE:** `test_n7_07_token_replay_denied`
- **N7_MAPPING:** N7-07
- **EXECUTED_RESULT:** PASS (Replay attempt immediately rejected and logged)
- **FINAL_VERDICT:** PASS

---

### F5: Immediate Irreversible Revocation
- **F_ID:** F5
- **REQUIREMENT:** Decision revocation immediately cascades to invalidate tokens and audit logs; cannot be undone.
- **THREAT:** Stale or unauthorized pilot execution continuing after revocation.
- **IMPLEMENTATION_PATH:** `backend/modules/learning/enterprise_governance_service.py`
- **IMPLEMENTATION_SYMBOL:** `EnterpriseGovernanceService.execute_manager_revocation`
- **DATABASE_OBJECT:** Columns `is_revoked`, `state='REVOKED'`
- **TEST_PATH:** `backend/tests/test_p7_negative_matrix.py`
- **TEST_CASE:** `test_n7_08_revocation_irreversible`
- **N7_MAPPING:** N7-08
- **EXECUTED_RESULT:** PASS (Revoked token and decision permanently reject activations)
- **FINAL_VERDICT:** PASS

---

### F6: Non-Bypassable Unprivileged Runtime Roles
- **F_ID:** F6
- **REQUIREMENT:** Runtime application user (`codesho_runtime`) and migration user (`codesho_migrator`) must have `rolsuper=f` and `rolbypassrls=f`.
- **THREAT:** Privilege escalation bypassing tenant isolation policies.
- **IMPLEMENTATION_PATH:** Database role provisioning DDL
- **IMPLEMENTATION_SYMBOL:** `ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS;`
- **DATABASE_OBJECT:** Roles in `pg_roles`
- **TEST_PATH:** `backend/tests/test_p7_negative_matrix.py`
- **TEST_CASE:** `test_n7_18_role_privilege_boundary`
- **N7_MAPPING:** N7-18
- **EXECUTED_RESULT:** PASS (`rolsuper=false`, `rolbypassrls=false` verified live)
- **FINAL_VERDICT:** PASS

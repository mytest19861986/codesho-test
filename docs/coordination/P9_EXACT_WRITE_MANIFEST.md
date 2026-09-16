# P9 Controlled Activation Readiness Write Manifest

## 1. Governance & Execution Boundaries
- **PHASE**: Phase 9 Controlled Activation Readiness Rehearsal
- **TASK**: `P9-CONTROLLED-ACTIVATION-READINESS-REHEARSAL`
- **MODE**: `SYNTHETIC_ONLY`
- **SYNTHETIC_RUNTIME_EXECUTION**: `AUTHORIZED` (Synthetic Tenants/Users/Data/Tokens/Stubs/Incidents only)
- **REAL_WORLD_EFFECT**: `0`
- **WILDCARD_PATHS_PERMITTED**: `NO` (Strict explicit paths only)
- **CANONICAL_TENANT_KEY**: `app.current_tenant`

## 2. Authorized P9 Canonical Artifacts (Exactly 14 Canonical Files)
1. `docs/coordination/P9_EXECUTION_DOSSIER.md`
2. `docs/coordination/P9_EXACT_WRITE_MANIFEST.md`
3. `docs/coordination/P9_ACTIVATION_FSM_SPEC.md`
4. `docs/coordination/P9_AUTHORITY_TOKEN_SPEC.md`
5. `docs/coordination/P9_SCOPE_LOCK_SPEC.md`
6. `docs/coordination/P9_SYNTHETIC_DATA_AND_CONSENT_FIXTURES.md`
7. `docs/coordination/P9_OBSERVABILITY_AND_AUDIT_SPEC.md`
8. `docs/coordination/P9_PAUSE_STOP_ROLLBACK_ABORT_RUNBOOK.md`
9. `docs/coordination/P9_INCIDENT_INJECTION_MATRIX.md`
10. `docs/coordination/P9_NEGATIVE_TEST_MATRIX.md`
11. `docs/coordination/P9_REHEARSAL_MATRIX.md`
12. `docs/coordination/P9_POST_ROLLBACK_INTEGRITY_REPORT.md`
13. `docs/coordination/P9_OPERATOR_RUNBOOK.md`
14. `docs/coordination/P9_FINAL_ACCEPTANCE_MATRIX.md`

## 3. Authorized Executable Synthetic Code & Test Files
15. `backend/modules/pilot_activation/__init__.py`
16. `backend/modules/pilot_activation/domain.py`
17. `backend/modules/pilot_activation/fsm.py`
18. `backend/modules/pilot_activation/tokens.py`
19. `backend/modules/pilot_activation/scope_lock.py`
20. `backend/modules/pilot_activation/synthetic_engine.py`
21. `backend/modules/pilot_activation/audit.py`
22. `backend/tests/test_p9_activation_synthetic.py`

## 4. Coordination & Ledger Files (Exactly 3 Files)
23. `docs/coordination/CURRENT_TASK.md`
24. `docs/coordination/PROJECT_STATE.md`
25. `docs/coordination/CODEX_TO_COMMANDER.md`

## 5. Explicitly Prohibited Writes
- Any modification to live production configuration (`backend/config/settings/production.py` or `.env*`) (DENIED)
- Any modification to accepted frontend (`frontend/`) unless operator UI is authorized (DENIED - FROZEN AT 83f9ae3)
- Any modification to live external communications (SMS/Email providers) (DENIED)
- Any modification to live payment providers (DENIED)
- Any real organization, real PII, child or guardian data (DENIED)
- Any commit directly to `main` (LOCKED_FOR_MANAGER)

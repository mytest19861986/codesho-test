# P10 Exact Write Manifest

## 1. Governance & Execution Boundaries
- **PHASE**: Phase 10 Human Manager Decision Package
- **TASK**: `P10-HUMAN-MANAGER-GO-NO_GO-DEFER-DECISION-PACKAGE`
- **MODE**: `DECISION_PREPARATION_ONLY`
- **REAL_WORLD_EXECUTION**: `PROHIBITED`
- **REAL_PILOT_ACTIVATION**: `PROHIBITED`
- **PRODUCTION_ACTIVATION**: `PROHIBITED`
- **WILDCARD_PATHS_PERMITTED**: `NO` (Strict explicit paths only)
- **CANONICAL_TENANT_KEY**: `app.current_tenant`
- **P9_CANONICAL_HEAD**: `9629db8013bff0d4a204ab032c37560c86548db4`
- **FRONTEND_HEAD**: `83f9ae322f4d3b6095d1649e07d329d7ad8d407a`
- **BACKEND_BASELINE_HEAD**: `7c4c1f09c876b6345b3550103a6ef30265376478`

## 2. Authorized P10 Canonical Artifacts (Exactly 12 Canonical Files)
1. `docs/coordination/P10_MANAGER_DECISION_EXECUTIVE_BRIEF.md`
2. `docs/coordination/P10_GO_NO_GO_DEFER_DECISION_FORM.md`
3. `docs/coordination/P10_TECHNICAL_READINESS_SUMMARY.md`
4. `docs/coordination/P10_REAL_WORLD_EVIDENCE_GAP_REGISTER.md`
5. `docs/coordination/P10_RISK_REGISTER.md`
6. `docs/coordination/P10_GO_BLOCKER_MATRIX.md`
7. `docs/coordination/P10_PRE_ACTIVATION_CHECKLIST.md`
8. `docs/coordination/P10_PILOT_ENTRY_EXIT_SUCCESS_CRITERIA.md`
9. `docs/coordination/P10_SCOPE_DEFINITION_TEMPLATE.md`
10. `docs/coordination/P10_EVIDENCE_INDEX.md`
11. `docs/coordination/P10_DECISION_AUDIT_RECORD_TEMPLATE.md`
12. `docs/coordination/P10_FINAL_MANAGER_DECISION_PACKAGE.md`

## 3. Coordination Artifacts
13. `docs/coordination/P10_EXACT_WRITE_MANIFEST.md`
14. `docs/coordination/CURRENT_TASK.md`
15. `docs/coordination/PROJECT_STATE.md`
16. `docs/coordination/CODEX_TO_COMMANDER.md`

## 4. Explicitly Prohibited Writes
- Any modification to backend code or models (`backend/`) (DENIED)
- Any modification to frontend code (`frontend/`) (DENIED)
- Any database migration creation or alteration (DENIED)
- Any production credential or configuration edit (DENIED)
- Any real PII or live student/guardian data (DENIED)
- Any direct push or promotion to `main` (LOCKED_FOR_MANAGER)

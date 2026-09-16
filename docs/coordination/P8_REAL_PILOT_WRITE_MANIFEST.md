# P8 Real Pilot Write Manifest

## 1. Governance & Mutation Boundaries
- **PHASE**: Phase 8 Discovery
- **TASK**: `P8-REAL-PILOT-ADMISSION-DECISION-AND-CONTROLLED-ACTIVATION-PREPARATION-DISCOVERY`
- **RUNTIME_MUTATION_PERMITTED**: `NO` (0 python/model/migration/runtime mutations)
- **WILDCARD_PATHS_PERMITTED**: `NO` (Strict explicit paths only)

## 2. Authorized Discovery File Accounting & Exact Paths

### A. Canonical Discovery Artifacts (Exactly 13 Files):
1. `docs/coordination/P8_REAL_PILOT_ADMISSION_DISCOVERY_DOSSIER.md`
2. `docs/architecture/P8_REAL_PILOT_ACTIVATION_ARCHITECTURE.md`
3. `docs/coordination/P8_REAL_PILOT_WRITE_MANIFEST.md`
4. `docs/coordination/P8_MANAGER_GO_NO_GO_DEFER_PACKAGE.md`
5. `docs/coordination/P8_REAL_PILOT_SCOPE_AND_LIMITS.md`
6. `docs/coordination/P8_REAL_DATA_ADMISSION_MATRIX.md`
7. `docs/coordination/P8_CONSENT_AND_AUTHORIZATION_READINESS.md`
8. `docs/coordination/P8_PRODUCTION_READINESS_MATRIX.md`
9. `docs/coordination/P8_OPERATIONS_SUPPORT_AND_INCIDENT_PLAN.md`
10. `docs/coordination/P8_CONTROLLED_ACTIVATION_PROTOCOL.md`
11. `docs/coordination/P8_EXIT_ROLLBACK_EMERGENCY_PLAN.md`
12. `docs/coordination/P8_SYNTHETIC_ACTIVATION_REHEARSAL.md`
13. `docs/coordination/P8_NEGATIVE_TEST_MATRIX.md`

### B. Additional Transfer & Coordination Files (Exactly 3 Files):
14. `docs/coordination/CURRENT_TASK.md` (Active task tracking)
15. `docs/coordination/PROJECT_STATE.md` (Repository macro state)
16. `docs/coordination/CODEX_TO_COMMANDER.md` (Authoritative ledger)

**TOTAL_DISCOVERY_FILES_IN_SCOPE**: Exactly 16 files (13 Canonical + 3 Coordination). Zero implicit files. Zero wildcards.

## 3. Explicit Path Denials
- Any file under `backend/modules/` (DENIED)
- Any file under `backend/config/` (DENIED)
- Any migration file `backend/*/migrations/` (DENIED)
- Any file under `frontend/src/` or `frontend/app/` (DENIED)
- Any production credential or `.env` modification (DENIED)
- Any raw provider or agent transcripts in repo (DENIED)
- Any real PII or live child data (DENIED)

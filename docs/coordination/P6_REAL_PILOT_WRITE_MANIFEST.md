# P6_REAL_PILOT_WRITE_MANIFEST.md - Codesho / SSD

**TASK**: `P6-CONTROLLED-REAL-PILOT-READINESS-DISCOVERY`
**STATUS**: `LOCKED_DISCOVERY_SPECIFICATION`
**RULE**: EXACT_PATHS_ONLY | ZERO_WILDCARDS | NO_RUNTIME_MUTATION_IN_DISCOVERY

---

## 1. Summary of Paths
- Total Discovery Artifact Paths: 9
- Total Runtime Candidate Paths (for future P6 execution if authorized): 6
- Unreviewed Paths: 0

---

## 2. Discovery Artifacts (CREATE)
1. `docs/coordination/P6_CONTROLLED_REAL_PILOT_READINESS_DISCOVERY_DOSSIER.md` [CREATE]
2. `docs/architecture/P6_REAL_PILOT_BOUNDARY_ARCHITECTURE.md` [CREATE]
3. `docs/coordination/P6_REAL_PILOT_WRITE_MANIFEST.md` [CREATE]
4. `docs/coordination/P6_REAL_PILOT_GO_NO_GO_MATRIX.md` [CREATE]
5. `docs/coordination/P6_REAL_DATA_ADMISSION_GATE.md` [CREATE]
6. `docs/coordination/P6_PILOT_OPERATING_MODEL.md` [CREATE]
7. `docs/coordination/P6_SYNTHETIC_DRESS_REHEARSAL_PLAN.md` [CREATE]
8. `docs/coordination/P6_NEGATIVE_TEST_MATRIX.md` [CREATE]
9. `docs/coordination/P6_MANAGER_DECISION_PACKAGE.md` [CREATE]

---

## 3. Runtime Candidate Paths for Future Implementation (LOCKED - DESIGN ONLY)
*The following paths are identified for future runtime implementation if and only if authorized by Commander & Human Manager:*

1. `backend/modules/pilot_governance/models.py` [MODIFY / REFERENCE]
   - Addition of `PilotAdmissionRequest`, `PilotScopeEnvelope`, `EmergencySuspensionAudit`.
2. `backend/modules/pilot_governance/admission_service.py` [CREATE]
   - Implementation of canonical Pilot Admission FSM and dual-custody approval checks.
3. `backend/modules/pilot_governance/migrations/0052_phase6_pilot_admission_fsm.py` [CREATE]
   - Database schema migration for admission FSM, strict checks, RLS policies.
4. `backend/modules/pilot_governance/tests/test_p6_admission_fsm.py` [CREATE]
   - P6-R1..P6-R20 dress rehearsal synthetic scenario tests.
5. `backend/modules/pilot_governance/tests/test_p6_negative_matrix.py` [CREATE]
   - N6-01..N6-30 negative regression and security matrix tests.
6. `frontend/src/components/pilot/ManagerDecisionCockpit.tsx` [CREATE]
   - Web UI for Manager Go/No-Go Decision Cockpit with friction locks and full audit transparency.

---

## 4. Read-Only Reference Files
1. `backend/modules/pilot_governance/enterprise_governance_service.py` [READ_ONLY_REFERENCE]
2. `backend/modules/pilot_governance/models.py` [READ_ONLY_REFERENCE]
3. `backend/modules/learning/models.py` [READ_ONLY_REFERENCE]
4. `PROJECT_STATE.md` [READ_ONLY_REFERENCE]
5. `CURRENT_TASK.md` [READ_ONLY_REFERENCE]

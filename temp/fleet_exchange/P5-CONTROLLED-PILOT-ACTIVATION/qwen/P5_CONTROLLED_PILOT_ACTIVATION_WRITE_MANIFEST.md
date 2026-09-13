# P5 Controlled Pilot Activation Write Manifest

## Status: DISCOVERY_AND_ARCHITECTURE_ACTIVE
## Authority: COMMANDER_P5_DISCOVERY_EXECUTION_ORDER
## Baseline: `e8a9a421466de31b53c22191e3673a94a0eba78a` / `f999314505dbcb03e9f4c7f96186be11e9627e29`

---

### Manifest Invariants
- `EXACT_PATHS_ONLY`: **TRUE**
- `ZERO_WILDCARDS`: **TRUE**
- `UNREVIEWED_PATHS`: **0**
- `RUNTIME_MUTATION_DURING_DISCOVERY`: **STRICTLY_FORBIDDEN**

---

### File Classification

#### 1. Discovery Artifacts (Active in Current Task)
| File Path | Action | Reviewer Relevance |
| :--- | :--- | :--- |
| `docs/architecture/P5_CONTROLLED_PILOT_ACTIVATION_BOUNDARY_PLAN.md` | `CREATE` | Qwen, GLM, Gemini |
| `docs/coordination/P5_PILOT_GO_NO_GO_CONTROL_MATRIX.md` | `CREATE` | Qwen, GLM, Gemini |
| `docs/coordination/P5_SYNTHETIC_PILOT_REHEARSAL_PLAN.md` | `CREATE` | Qwen, GLM, Gemini |
| `docs/coordination/P5_NEGATIVE_TEST_MATRIX.md` | `CREATE` | Qwen, GLM, Gemini |
| `docs/coordination/P5_CONTROLLED_PILOT_ACTIVATION_WRITE_MANIFEST.md` | `CREATE` | Qwen, GLM, Gemini |
| `docs/coordination/P5_CONTROLLED_PILOT_ACTIVATION_DISCOVERY_DOSSIER.md` | `CREATE` | Commander, Qwen, GLM, Gemini |
| `docs/coordination/CURRENT_TASK.md` | `MODIFY` | Commander, Fleet |

#### 2. Prospective Runtime Implementation Files (DESIGN-ONLY / LOCKED)
*The following files are cataloged for prospective implementation upon Commander Runtime Authorization. They SHALL NOT be modified during Discovery.*

| File Path | Prospective Action | Intended Responsibility |
| :--- | :--- | :--- |
| `backend/governance/models.py` | `MODIFY` | Add `PilotTenantLifecycle`, `PilotPrerequisiteChecklist`, `DualCustodyApprovalEvent` models |
| `backend/governance/views.py` | `MODIFY` | Add endpoints for pilot evaluation, prerequisite validation, and dual-custody approval |
| `backend/governance/urls.py` | `MODIFY` | Wire governance pilot routes under `/api/v1/governance/pilot/` |
| `backend/governance/serializers.py` | `MODIFY` | Add validation serializers with anti-ranking and PII scrubbers |
| `backend/governance/tests/test_p5_pilot_activation_fsm.py` | `CREATE` | Full automated suite verifying canonical FSM and R1-R16 scenarios |
| `backend/governance/tests/test_p5_negative_matrix.py` | `CREATE` | Full automated suite executing N5-01 through N5-24 |
| `frontend/src/features/governance/PilotActivationControlBoard.tsx` | `CREATE` | WCAG 2.2 AA compliant activation control board, checklist, and frictional confirmation |
| `frontend/src/features/governance/PilotGoNoGoView.tsx` | `CREATE` | Live Go/No-Go matrix inspector with zero-ranking enforcement |

#### 3. Read-Only Reference Files
| File Path | Classification | Context |
| :--- | :--- | :--- |
| `AGENTS.md` | `READ_ONLY_REFERENCE` | Master instructions and authority hierarchy |
| `infra/postgres/init/001-roles.sh` | `READ_ONLY_REFERENCE` | DB role topology (`codesho_runtime`, `NOSUPERUSER NOBYPASSRLS`) |
| `backend/governance/migrations/0050_revoke_delete_on_immutable_tables.py` | `READ_ONLY_REFERENCE` | Immutability and revoke delete baseline |
| `scripts/restore-verify.sh` | `READ_ONLY_REFERENCE` | Automated backup verification harness |
| `docs/sprint-zero/deployment-observability-dr.md` | `READ_ONLY_REFERENCE` | Disaster recovery and PITR runbooks |

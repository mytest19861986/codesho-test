# Phase 3 Vertical Slice 7 Write Manifest (P3-VS7)

## Target Authority
- Task: `P3-VS7-ADVANCED-ASSESSMENT-AUTOMATED-EVALUATION-AND-CODE-PLAYGROUND`
- Status: `DISCOVERY_LOCKED` (Zero Runtime Changes Permitted until Fleet Review PASS & Commander Authorization)
- Authority: `COMMANDER_P3_VS6_FINAL_DISPOSITION`

## Manifest Invariants
- ZERO_WILDCARDS: YES
- EXACT_PATHS_ONLY: YES
- UNREVIEWED_PATHS: 0

---

## 1. Documentation & Architecture
- `docs/architecture/PHASE3_VS7_BOUNDARY_PLAN.md` (Boundary architecture specification)
- `docs/coordination/PHASE3_VS7_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Task coordination state)

---

## 2. Planned Backend Components (Locked for Discovery)
- `backend/modules/learning/assessments.py` (Automated evaluation engine, sandbox run state machine, test runner integration)
- `backend/modules/learning/models.py` (Enhancements for CodeAssessment, CodeExecutionRun, AssessmentResult)
- `backend/modules/learning/serializers.py` (CodeAssessmentSerializer, CodeExecutionRunSerializer, AssessmentResultSerializer)
- `backend/modules/learning/views.py` (CodeAssessmentListView, CodeExecutionRunView, AssessmentResultView)
- `backend/modules/learning/urls.py` (Routing for assessment and playground execution endpoints)
- `backend/modules/learning/migrations/0020_p3_vs7_assessments.py` (Table definitions and constraints)
- `backend/modules/learning/migrations/0021_p3_vs7_assessments_rls.py` (PostgreSQL 17 FORCE RLS)

---

## 3. Planned Backend Tests (Locked for Discovery)
- `backend/tests/test_p3_vs7_assessments.py` (Evaluation workflow, test runner execution, timeout handling, idempotency)
- `backend/tests/test_p3_vs7_assessments_rls.py` (Cross-tenant isolation negative tests)

---

## 4. Planned Frontend Components (Locked for Discovery)
- `frontend/src/components/assessments/InteractivePlaygroundCard.tsx` (Interactive code editor and runner component)
- `frontend/src/components/assessments/TestEvaluationPanel.tsx` (Test-case results and automated score display)

---

## 5. Visual Evidence & Regression Testing (Antigravity Sweep)
- Route: `/` (Landing)
- Route: `/login` (Login)
- Route: `/dashboard/student` (Student Dashboard & Interactive Code Playground)
- Route: `/dashboard/mentor` (Mentor Review & Assessment Evaluation)
- Route: `/dashboard/parent` (Parent Progress Overview)
- Route: `/admin/learning` (Admin Curriculum & Assessments)

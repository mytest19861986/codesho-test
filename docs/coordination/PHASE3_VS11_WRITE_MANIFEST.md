# Phase 3 Vertical Slice 11 Write Manifest (P3-VS11)

## Manifest Governance
- **TASK_ID**: `P3-VS11-LEARNING-PERSONALIZATION-AND-ADAPTIVE-PROGRESSION-ENGINE`
- **SCOPE_TITLE**: موتور شخصی‌سازی یادگیری، تحلیل مسیر رشد دانش‌آموز و سیستم پیشنهاد مسیر آموزشی تطبیقی
- **STATUS**: `RUNTIME_UNLOCKED / IMPLEMENTATION_ACTIVE`
- **ZERO_WILDCARDS**: `YES`
- **EXACT_PATHS_ONLY**: `YES`
- **UNREVIEWED_PATHS**: `0`

---

## Allowed File Targets (Exact Paths Only)

### 1. Architecture & Coordination Documentation
- `docs/architecture/PHASE3_VS11_BOUNDARY_PLAN.md` (Design & Boundary Spec)
- `docs/coordination/PHASE3_VS11_WRITE_MANIFEST.md` (Locked File Manifest)
- `docs/coordination/CURRENT_TASK.md` (Active Task Pointer)
- `docs/coordination/PHASE3_VS11_DISCOVERY_DOSSIER.md` (Triple Fleet Review Dossier)
- `docs/coordination/PHASE3_VS11_FINAL_REPORT.md` (Post-Implementation Report)
- `docs/openapi.yaml` (API Contract Parity)

### 2. Backend Implementation (LOCKED UNTIL COMMANDER RUNTIME UNLOCK)
- `backend/modules/learning/models.py` (Append SkillDefinition, SkillDependency, LessonSkillMapping, StudentSkillProgress, StudentLearningProfile, LearningRecommendation)
- `backend/modules/learning/migrations/0028_p3_vs11_adaptive_progression.py` (Schema & Models)
- `backend/modules/learning/migrations/0029_p3_vs11_adaptive_progression_rls.py` (FORCE RLS & Composite FK DDL)
- `backend/modules/learning/personalization_service.py` (Profile Rebuild, Mastery State Machine, Recommendation Engine)
- `backend/modules/learning/serializers.py` (Personalization & Recommendation Serializers)
- `backend/modules/learning/views.py` (StudentProfileView, RecommendationListView, RecommendationActionView, SkillGraphView)
- `backend/modules/learning/urls.py` (Endpoint Routing)

### 3. Automated Verification & Testing (LOCKED UNTIL RUNTIME UNLOCK)
- `backend/tests/test_p3_vs11_personalization.py` (Negative Isolation N1-N20 Matrix, DAG Cycle Detection, Composite FK Integrity, RLS Fail-Closed)

### 4. Frontend Components & UX (LOCKED UNTIL RUNTIME UNLOCK)
- `frontend/src/components/personalization/AdaptiveRecommendationCard.tsx` (Explainable Recommendation UI with BiDi)
- `frontend/src/components/personalization/StudentSkillRadar.tsx` (Growth Indicator & Skill Graph)
- `frontend/src/components/personalization/LearningGapAlert.tsx` (Encouraging Remedial Feedback)
- `frontend/src/app/dashboard/student/page.tsx` (Integration into Student Dashboard)

---

## Prohibited Paths (Zero Tolerance)
- No modifications to billing/payments (`backend/modules/billing/`)
- No live external AI mentor or third-party LLM providers
- No modification of core auth without explicit authorization
- No wildcard directories or unlisted migration files

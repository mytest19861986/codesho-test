# Phase 2 Implementation Write Manifest

## Target Authority
- Base Order: `COMMANDER_CONTINUATION_ORDER` / `COMMANDER_VS3_DISPOSITION`
- Package: `PHASE2-CORE-PRODUCT-BUILD`
- Active Task: `P2-VS4-CROSS-ROLE-LEARNING-INTEGRATION-AND-HARDENING`
- Execution Principle: Zero Wildcards, Strict File Allow-list, Multi-Role Fail-Closed Isolation

---

## 1. Backend: Cross-Role Business Integration, Authorization Matrix & Hardening
- `backend/modules/learning/models.py` (Curriculum, Submissions, Feedbacks, Progress integrity)
- `backend/modules/learning/serializers.py` (Cross-role representations & student/mentor/parent/admin payloads)
- `backend/modules/learning/services.py` (End-to-end multi-role state propagation engine)
- `backend/modules/learning/views.py` (All 4 surfaces: Student, Mentor, Parent, Admin REST endpoints)
- `backend/modules/learning/urls.py` (Unified learning URL router)
- `backend/tests/test_phase2_cross_role_integration.py` (End-to-end multi-role business flow & state machine drift prevention)
- `backend/tests/test_phase2_cross_role_authorization.py` (Comprehensive 4-role authorization matrix & fail-closed negative tests)

---

## 2. API Contract & OpenAPI Specification
- `docs/openapi.yaml` (Canonical OpenAPI declarations for all integrated Phase 2 routes)

---

## 3. Frontend: Multi-Role Integration, Navigation & Unified Product Flow
- `frontend/src/features/dashboard/DashboardScreen.tsx` (Student surface with feedback and progress reflection)
- `frontend/src/features/mentor/MentorDashboardScreen.tsx` (Mentor queue and feedback submission)
- `frontend/src/features/parent/ParentDashboardScreen.tsx` (Parent read-only monitoring)
- `frontend/src/features/admin_learning/AdminLearningScreen.tsx` (Admin curriculum management)
- `frontend/src/app/dashboard/student/page.tsx` (Integrated Student route)
- `frontend/src/app/dashboard/mentor/page.tsx` (Integrated Mentor route)
- `frontend/src/app/dashboard/parent/page.tsx` (Integrated Parent route)
- `frontend/src/app/admin/learning/page.tsx` (Integrated Admin route)

---

## 4. Frontend Quality Assurance Visual Storage
- `temp/phase2/vs4/student-flow/desktop.png` (Desktop 1440x900)
- `temp/phase2/vs4/student-flow/mobile.png` (Mobile 390x844)
- `temp/phase2/vs4/mentor-flow/desktop.png` (Desktop 1440x900)
- `temp/phase2/vs4/mentor-flow/mobile.png` (Mobile 390x844)
- `temp/phase2/vs4/parent-flow/desktop.png` (Desktop 1440x900)
- `temp/phase2/vs4/parent-flow/mobile.png` (Mobile 390x844)
- `temp/phase2/vs4/admin-flow/desktop.png` (Desktop 1440x900)
- `temp/phase2/vs4/admin-flow/mobile.png` (Mobile 390x844)

---

## 5. Coordination & Review Dispositions
- `docs/coordination/PHASE2_WRITE_MANIFEST.md` (This document)
- `docs/coordination/CURRENT_TASK.md` (Active task pointers)
- `docs/coordination/CODEX_TO_COMMANDER.md` (Progress checkpoints and evidence logs)

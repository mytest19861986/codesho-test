# Phase 3 Vertical Slice 5 Write Manifest (P3-VS5)

## Target Authority
- Task: `P3-VS5-STUDENT-ENROLLMENT-COHORT-AND-PROGRESSION-POLICIES`
- Status: `DISCOVERY_LOCKED` (Zero Runtime Changes Permitted until Fleet Review PASS)
- Authority: `COMMANDER_P3_VS4_FINAL_DISPOSITION`

## Manifest Invariants
- ZERO_WILDCARDS: YES
- EXACT_PATHS_ONLY: YES
- UNREVIEWED_PATHS: 0

---

## 1. Documentation & Architecture
- `docs/architecture/PHASE3_VS5_BOUNDARY_PLAN.md` (Boundary architecture specification)
- `docs/coordination/PHASE3_VS5_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Task coordination state)

---

## 2. Planned Backend Components (Locked for Discovery)
- `backend/modules/learning/enrollment.py` (Enrollment engine, capacity management, prerequisite checker)
- `backend/modules/learning/models.py` (CourseEnrollment and Cohort models)
- `backend/modules/learning/serializers.py` (CourseEnrollmentSerializer, CohortSerializer)
- `backend/modules/learning/views.py` (StudentEnrollmentView, StudentEnrollActionView)
- `backend/modules/learning/urls.py` (Routing for enrollment endpoints)
- `backend/modules/learning/migrations/0016_p3_vs5_enrollment.py` (Table definitions)
- `backend/modules/learning/migrations/0017_p3_vs5_enrollment_rls.py` (PostgreSQL 17 FORCE RLS)

---

## 3. Planned Backend Tests (Locked for Discovery)
- `backend/tests/test_p3_vs5_enrollment.py` (Capacity limits, state transitions, idempotency)
- `backend/tests/test_p3_vs5_enrollment_rls.py` (Cross-tenant negative isolation test)

---

## 4. Planned Frontend Components (Locked for Discovery)
- `frontend/src/components/enrollment/EnrollmentCard.tsx` (Course enrollment status and action card)
- `frontend/src/components/enrollment/CohortBadge.tsx` (Cohort status badge)

---

## 5. Visual Evidence & Regression Testing (Antigravity Sweep)
- Route: `/` (Landing)
- Route: `/login` (Login)
- Route: `/dashboard/student` (Student Dashboard & Course Enrollment Status)
- Route: `/dashboard/mentor` (Mentor Cohort Overview)
- Route: `/dashboard/parent` (Parent Enrollment Review)
- Route: `/admin/learning` (Admin Curriculum & Enrollment Policy)

# Phase 3 Vertical Slice 6 Write Manifest (P3-VS6)

## Target Authority
- Task: `P3-VS6-STUDENT-ASSIGNMENT-SUBMISSION-AND-MENTOR-FEEDBACK-WORKFLOW`
- Status: `DISCOVERY_LOCKED` (Zero Runtime Changes Permitted until Fleet Review PASS & Commander Authorization)
- Authority: `COMMANDER_P3_VS5_FINAL_DISPOSITION`

## Manifest Invariants
- ZERO_WILDCARDS: YES
- EXACT_PATHS_ONLY: YES
- UNREVIEWED_PATHS: 0

---

## 1. Documentation & Architecture
- `docs/architecture/PHASE3_VS6_BOUNDARY_PLAN.md` (Boundary architecture specification)
- `docs/coordination/PHASE3_VS6_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Task coordination state)

---

## 2. Planned Backend Components (Locked for Discovery)
- `backend/modules/learning/submissions.py` (Submission state machine, scoring validator, mentor review engine)
- `backend/modules/learning/models.py` (Enhancements to Assignment, Submission, and Feedback models)
- `backend/modules/learning/serializers.py` (AssignmentSubmissionSerializer, MentorFeedbackSerializer)
- `backend/modules/learning/views.py` (StudentSubmissionView, MentorReviewQueueView, MentorFeedbackActionView)
- `backend/modules/learning/urls.py` (Routing for submission and mentor feedback endpoints)
- `backend/modules/learning/migrations/0018_p3_vs6_submissions.py` (Table definitions and constraints)
- `backend/modules/learning/migrations/0019_p3_vs6_submissions_rls.py` (PostgreSQL 17 FORCE RLS)

---

## 3. Planned Backend Tests (Locked for Discovery)
- `backend/tests/test_p3_vs6_submissions.py` (Submission workflow, late policies, scoring validation, idempotency)
- `backend/tests/test_p3_vs6_submissions_rls.py` (Cross-tenant isolation negative tests)

---

## 4. Planned Frontend Components (Locked for Discovery)
- `frontend/src/components/submissions/AssignmentSubmissionCard.tsx` (Student assignment submission component)
- `frontend/src/components/submissions/MentorReviewQueue.tsx` (Mentor feedback and scoring component)

---

## 5. Visual Evidence & Regression Testing (Antigravity Sweep)
- Route: `/` (Landing)
- Route: `/login` (Login)
- Route: `/dashboard/student` (Student Dashboard & Assignment Submission)
- Route: `/dashboard/mentor` (Mentor Review Queue)
- Route: `/dashboard/parent` (Parent Progress Overview)
- Route: `/admin/learning` (Admin Curriculum & Assignments)

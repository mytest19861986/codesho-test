# Phase 3 Vertical Slice 4 Write Manifest (P3-VS4)

## Target Authority
- Task: `P3-VS4-LEARNING-ANALYTICS-AND-STUDENT-GAMIFICATION-PROGRESSION`
- Status: `DISCOVERY_LOCKED` (Zero Runtime Changes Permitted)
- Authority: `COMMANDER_P3_VS3_FINAL_DISPOSITION`

## Manifest Invariants
- ZERO_WILDCARDS: YES
- EXACT_PATHS_ONLY: YES
- UNREVIEWED_PATHS: 0

---

## 1. Documentation & Architecture
- `docs/architecture/PHASE3_VS4_BOUNDARY_PLAN.md` (Boundary architecture specification)
- `docs/coordination/PHASE3_VS4_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Task coordination state)

---

## 2. Planned Backend Components (Locked for Discovery)
- `backend/modules/learning/gamification.py` (Gamification and streak evaluation engine)
- `backend/modules/learning/models.py` (StudentBadgeAward and StudentProgressionProfile models)
- `backend/modules/learning/serializers.py` (GamificationProfileSerializer, zero PII)
- `backend/modules/learning/views.py` (StudentGamificationView)
- `backend/modules/learning/urls.py` (Endpoint routing for gamification)
- `backend/modules/learning/migrations/0014_p3_vs4_gamification.py` (Table creation)
- `backend/modules/learning/migrations/0015_p3_vs4_gamification_rls.py` (FORCE RLS migration)

---

## 3. Planned Backend Tests (Locked for Discovery)
- `backend/tests/test_p3_vs4_gamification.py` (Milestone awards, streak rules, idempotency)
- `backend/tests/test_p3_vs4_gamification_rls.py` (Cross-tenant negative isolation test)

---

## 4. Planned Frontend Components (Locked for Discovery)
- `frontend/src/components/gamification/BadgeShelf.tsx` (Student badges and showcase widget)
- `frontend/src/components/gamification/StreakIndicator.tsx` (Streak counter and flame indicator)

---

## 5. Visual Evidence & Regression Testing (Antigravity Sweep)
- Route: `/` (Landing)
- Route: `/login` (Login)
- Route: `/dashboard/student` (Student Dashboard & Badge Showcase)
- Route: `/dashboard/mentor` (Mentor Dashboard)
- Route: `/dashboard/parent` (Parent Dashboard)
- Route: `/admin/learning` (Admin Learning Operations)

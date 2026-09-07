# Phase 3 Vertical Slice 3 Write Manifest (P3-VS3)

## Target Authority
- Task: `P3-VS3-COMMUNICATION-NOTIFICATIONS-DISPATCHER`
- Status: `DISCOVERY_LOCKED` (Zero Runtime Changes Permitted)
- Authority: `COMMANDER_P3_VS2_FINAL_DISPOSITION`

## Manifest Invariants
- ZERO_WILDCARDS: YES
- EXACT_PATHS_ONLY: YES
- UNREVIEWED_PATHS: 0

---

## 1. Documentation & Architecture
- `docs/architecture/PHASE3_VS3_BOUNDARY_PLAN.md` (Boundary architecture specification)
- `docs/coordination/PHASE3_VS3_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Task coordination state)

---

## 2. Planned Backend Components (Locked for Discovery)
- `backend/modules/learning/notifications.py` (Notification generator and dispatcher service)
- `backend/modules/learning/models.py` (In-app NotificationItem model with tenant isolation)
- `backend/modules/learning/serializers.py` (NotificationItemSerializer, zero PII)
- `backend/modules/learning/views.py` (NotificationListView, NotificationMarkReadView)
- `backend/modules/learning/urls.py` (Notification endpoint routing)
- `backend/modules/learning/tasks.py` (Celery background dispatch task)
- `backend/modules/learning/migrations/0012_p3_vs3_notifications.py` (Table creation)
- `backend/modules/learning/migrations/0013_p3_vs3_notifications_rls.py` (FORCE RLS migration)

---

## 3. Planned Backend Tests (Locked for Discovery)
- `backend/tests/test_p3_vs3_notifications.py` (Delivery guarantees, read tracking, idempotency)
- `backend/tests/test_p3_vs3_notification_rls.py` (Cross-tenant negative isolation test)

---

## 4. Planned Frontend Components (Locked for Discovery)
- `frontend/src/components/notifications/NotificationBell.tsx` (Integration with backend notification API)
- `frontend/src/components/notifications/NotificationDrawer.tsx` (Drawer component for notification feeds)

---

## 5. Visual Evidence & Regression Testing (Antigravity Sweep)
- Route: `/` (Landing)
- Route: `/login` (Login)
- Route: `/dashboard/student` (Student Dashboard & Notification Bell)
- Route: `/dashboard/mentor` (Mentor Dashboard & Queue Notifications)
- Route: `/dashboard/parent` (Parent Dashboard & Activity Notifications)
- Route: `/admin/learning` (Admin Learning Operations)

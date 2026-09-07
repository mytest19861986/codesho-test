# Phase 3 Vertical Slice 2 Write Manifest (P3-VS2)

## Target Authority
- Task: `P3-VS2-PRODUCT-EVENTS-ANALYTICS-AND-ACTIVITY`
- Authority: `COMMANDER_P3_BOUNDARY_FINAL_DISPOSITION` / `P3_VS2_DISCOVERY_AUTHORIZED`
- Execution Principles:
  * Zero Wildcards, Strict File Allow-list
  * Authoritative Business Records Preserved (Progress, Submission, Feedback are primary authorities)
  * Projections are Safe, Tenant-Bounded Aggregates (Not sources of truth)
  * Zero PII & Zero Third-Party Tracking (No Google Analytics, Meta Pixel, Amplitude, etc.)
  * Strict PostgreSQL RLS & Composite Tenancy Isolation
  * Independent Multi-Agent Verification (Qwen: Backend/Events, GLM: DB/RLS/Privacy, Gemini: UI/UX/Accessibility)

---

## 1. Backend: Product Events, Projections & Role Activity Feeds
- `backend/modules/learning/models.py` (Tenant-bounded Projections: CourseProgressAggregate, AssignmentSubmissionMetrics, RoleActivityFeed)
- `backend/modules/learning/events.py` (Authoritative Domain Events: LessonCompleted, AssignmentSubmitted, FeedbackDelivered)
- `backend/modules/learning/projections.py` (Idempotent Projection Appliers, Dedup by source_event_id, Watermarks)
- `backend/modules/learning/serializers.py` (Role-specific projection serializers with zero PII)
- `backend/modules/learning/views.py` (Role endpoints: Student learning analytics, Mentor queue metrics, Parent progress summary, Admin tenant overview)
- `backend/modules/learning/urls.py` (VS2 Analytics & Activity feed route bindings)
- `backend/modules/learning/migrations/0008_p3_vs2_projections_rls.py` (FORCE RLS, Tenant policy, Composite FKs)

---

## 2. Backend Automated Test Suite
- `backend/tests/test_p3_vs2_events.py` (Transactional event emission and idempotency)
- `backend/tests/test_p3_vs2_projections.py` (Projection appliers, rebuild from source events, reconciliation)
- `backend/tests/test_p3_vs2_authorization_matrix.py` (Negative cross-tenant and role-access 4-quadrant tests)
- `backend/tests/test_p3_vs2_privacy_scan.py` (Zero PII payload and zero external tracking scan)

---

## 3. OpenAPI Contract
- `docs/openapi.yaml` (Authoritative REST contract declarations for VS2 analytics and feed endpoints)

---

## 4. Frontend: Role Dashboard Visual Integration & Metrics
- `frontend/src/features/dashboard/DashboardScreen.tsx` (Student Progress & Recent Activity Feed component)
- `frontend/src/features/mentor/MentorDashboardScreen.tsx` (Mentor Workload Metrics & Pending Review Feed)
- `frontend/src/features/parent/ParentDashboardScreen.tsx` (Parent Read-Only Progress Summary)
- `frontend/src/features/admin_learning/AdminLearningScreen.tsx` (Admin Tenant Aggregate Overview)

---

## 5. Visual Evidence & Screenshots
- `temp/phase3/vs2/student/desktop.png` (Desktop 1440x900)
- `temp/phase3/vs2/student/mobile.png` (Mobile 390x844)
- `temp/phase3/vs2/mentor/desktop.png` (Desktop 1440x900)
- `temp/phase3/vs2/mentor/mobile.png` (Mobile 390x844)
- `temp/phase3/vs2/parent/desktop.png` (Desktop 1440x900)
- `temp/phase3/vs2/parent/mobile.png` (Mobile 390x844)

---

## 6. Coordination & Evidence Artifacts
- `docs/coordination/PHASE3_VS2_WRITE_MANIFEST.md` (This file)
- `docs/coordination/CURRENT_TASK.md` (Updated task lifecycle state)
- `docs/coordination/CODEX_TO_COMMANDER.md` (Progress ledger and review dispositions)

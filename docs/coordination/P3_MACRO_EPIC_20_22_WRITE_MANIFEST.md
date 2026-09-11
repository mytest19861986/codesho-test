# P3-MACRO-EPIC-20-22 Write Manifest & Implementation Blueprint

## 1. Package Overview
- **Epic ID**: `P3-MACRO-EPIC-20-22-CURRICULUM-DELIVERY-AND-PROGRAM-OPERATIONS`
- **Scope**:
  - `P3-VS20`: Curriculum Versioning & Release Governance
  - `P3-VS21`: Cohort Schedule & Learning Session Orchestration
  - `P3-VS22`: Program Delivery Quality & Operations Control Center
- **Mode**: `MACRO_FAST_ENTERPRISE`

---

## 2. Models to Add in `backend/modules/learning/models.py`
1. `CurriculumVersion`: Semantic versioning, status FSM (`DRAFT` -> `REVIEW` -> `APPROVED` -> `PUBLISHED` -> `RETIRED`).
2. `CourseRelease`: Active release mapping for courses.
3. `ModuleReleaseSnapshot`: Immutable snapshot of module title, order, and payload.
4. `LessonReleaseSnapshot`: Immutable snapshot of lesson content hash and payload.
5. `ReleaseApprovalRecord`: Audit record for curriculum approval decisions.
6. `CurriculumReleaseAuditLog`: Append-only audit log with XOR constraint between version and course release.
7. `CohortSchedule`: Delivery schedule linked to a specific CourseRelease.
8. `LearningSession`: Individual learning session occurrence templates.
9. `SessionOccurrence`: Conducted session instances with actual timestamps and attendance.
10. `SessionAttendanceState`: Synthetic attendance state (strictly non-punitive).
11. `SessionChangeRecord`: Reschedule and cancellation audit log.
12. `ProgramDeliveryAggregate`: Non-authoritative delivery progress projection (`is_authoritative = False`).
13. `CurriculumReleaseCoverage`: Adoption projection across cohorts.
14. `CohortScheduleHealth`: Health and delay projection.
15. `DeliveryExceptionQueue`: Operational exception queue.

---

## 3. Database Migrations
- Migration `0042_p3_macro_epic_20_22_models.py`: Defines all 15 models, composite primary keys/foreign keys, and Django check constraints.
- Migration `0043_p3_macro_epic_20_22_rls_force.py`: Applies PostgreSQL 17 `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, `p3_tenant_isolation_policy`, and `REVOKE UPDATE, DELETE` on immutable/audit tables.

---

## 4. Service Layer & Outbox Events
- `CurriculumGovernanceService`:
  - `create_version(tenant_id, course_id, semver, ...)`
  - `publish_version(tenant_id, version_id, actor_id)` -> emits outbox event `curriculum.version.published`
  - `create_release(tenant_id, course_id, version_id, ...)`
- `CohortSchedulingService`:
  - `create_cohort_schedule(tenant_id, cohort_id, release_id, ...)`
  - `reschedule_session(tenant_id, session_id, new_start, ...)` -> emits outbox event `cohort.session.rescheduled`
  - `record_occurrence(tenant_id, session_id, ...)`
- `ProgramOperationsService`:
  - `refresh_delivery_projections(tenant_id, cohort_id)`
  - `log_delivery_exception(tenant_id, ...)`

---

## 5. API Endpoints
- `/api/v1/learning/curriculum/versions/` [GET, POST]
- `/api/v1/learning/curriculum/versions/<id>/publish/` [POST]
- `/api/v1/learning/cohorts/<cohort_id>/schedules/` [GET, POST]
- `/api/v1/learning/sessions/<id>/reschedule/` [POST]
- `/api/v1/learning/operations/delivery-overview/` [GET]
- `/api/v1/learning/operations/exceptions/` [GET, POST]

---

## 6. Frontend Workspace
- `frontend/src/components/curriculum/CurriculumOperationsWorkspace.tsx`:
  - Operator control center for curriculum releases, cohort delivery timelines, and exception queue.
  - WCAG 2.2 AA compliant, full RTL/BiDi isolation with `<bdi dir="ltr">`.
  - Zero leaderboards, zero competitive peer rankings.
- Page: `frontend/src/app/dashboard/admin/curriculum-operations/page.tsx`.

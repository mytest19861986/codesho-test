P3-MACRO-EPIC-20-22 Discovery Review)
You said همکار گرامی Gemini (معمار ارشد طراحی رابط، سیستم دیزاین و دسترسی‌پذیری)، متن کامل سند مشخصات کاربری …

همکار گرامی Gemini (معمار ارشد طراحی رابط، سیستم دیزاین و دسترسی‌پذیری)،

متن کامل سند مشخصات کاربری و طراحی بسته کلان P3-MACRO-EPIC-20-22 به‌صورت اینلاین جهت بررسی تخصصی و صدور رأی رسمی تقدیم می‌گردد:




# P3-MACRO-EPIC-20-22 Boundary Plan & Architecture Specification (v1.0-CANONICAL)




## 1. Epic Overview

- **Epic ID**: `P3-MACRO-EPIC-20-22-CURRICULUM-DELIVERY-AND-PROGRAM-OPERATIONS`

- **FA Title**: حاکمیت برنامه آموزشی، انتشار محتوای درسی و عملیات اجرای دوره

- **Branch**: `codex/phase3-product-platform-foundation`

- **Authority Directive**: `COMMANDER_P3_MACRO_EPIC_20_22_DISCOVERY_UNLOCK: GRANTED`

- **Delivery Mode**: `MACRO_FAST_ENTERPRISE` (Single Epic Package, Combined Discovery, Parallel Fleet Review)

- **Scope**:

- **P3-VS20**: Curriculum Versioning & Release Governance (`CurriculumVersion`, `CourseRelease`, `ModuleReleaseSnapshot`, `LessonReleaseSnapshot`, `ReleaseApprovalRecord`, `CurriculumReleaseAuditLog`).

- **P3-VS21**: Cohort Schedule & Learning Session Orchestration (`LearningSession`, `CohortSchedule`, `SessionOccurrence`, `SessionAttendanceState`, `SessionChangeRecord`).

- **P3-VS22**: Program Delivery Quality & Operations Control Center (`ProgramDeliveryAggregate`, `CurriculumReleaseCoverage`, `CohortScheduleHealth`, `DeliveryExceptionQueue`).




---




## 2. Domain Boundaries & Architectural Invariants




### 2.1. P3-VS20: Curriculum Versioning & Release Governance

- **Lifecycle FSM**:

`DRAFT` → `REVIEW` → `APPROVED` → `PUBLISHED` → `RETIRED`

- **Hard Invariants**:

1. `PUBLISHED_VERSION_MUTATION: PROHIBITED` — Once `PUBLISHED`, neither the version metadata nor snapshots can be updated or deleted.

2. `HISTORICAL_SUBMISSION_REBIND: PROHIBITED` — Completed student submissions and progress records retain an immutable foreign key reference to the exact curriculum version/snapshot they interacted with.

3. `SILENT_CONTENT_REPLACEMENT: PROHIBITED` — Updates to curriculum require creating a new `CurriculumVersion` in `DRAFT`.

4. `RELEASE_AUDIT: APPEND_ONLY` — Database-level enforcement (`REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM PUBLIC, app_role;`).




### 2.2. P3-VS21: Cohort Schedule & Learning Session Orchestration

- **Lifecycle FSM**:

`SCHEDULED` → `IN_SESSION` → `COMPLETED`, `RESCHEDULED`, `CANCELLED`

- **Hard Invariants & Privacy Boundaries**:

1. `NO_REAL_CALENDAR_PROVIDER: TRUE` — No external Google Calendar, Outlook, or CalDAV webhooks.

2. `NO_REAL_COMMUNICATION_PROVIDER: TRUE` — No live Twilio/Kavenegar/SendGrid provider calls.

3. `NO_REAL_CHILD_ATTENDANCE_DATA: TRUE` — Synthetic attendance records only.

4. `NO_AUTOMATED_PUNITIVE_ACTION: TRUE` — Zero automated expulsion, penal grading, or automated parent alerts for absences.

5. `MENTOR_COHORT_ALIGNMENT: ENFORCED` — Assigned mentor must have an active supervision or caseload assignment for the cohort/course.




### 2.3. P3-VS22: Program Delivery Quality & Operations Control Center

- **Derived Projections**:

`ProgramDeliveryAggregate`, `CurriculumReleaseCoverage`, `CohortScheduleHealth`, `DeliveryExceptionQueue`.

- **Hard Invariants & Anti-Ranking Policy**:

1. `NON_AUTHORITATIVE_PROJECTION: TRUE` — Constraint `chk_deliveryagg_non_authoritative CHECK (is_authoritative = FALSE)`.

2. `STUDENT_RANKING: PROHIBITED (0)` — No leaderboards, no competitive peer comparisons, no public percentiles.

3. `STUDENT_RISK_SCORE: PROHIBITED (0)` — No automated algorithmic drop-out risk labels.

4. `PSYCHOLOGICAL_CLASSIFICATION: PROHIBITED (0)` — No behavioral or psychological labeling.




---




## 3. Database Schema & PostgreSQL 17 RLS Specifications




1. **Multi-Tenancy & RLS**:

- All tables include `tenant_id uuid NOT NULL`.

- All tables enforce `ALTER TABLE ... ENABLE ROW LEVEL SECURITY; ALTER TABLE ... FORCE ROW LEVEL SECURITY;`.

- RLS Policy: `USING (tenant
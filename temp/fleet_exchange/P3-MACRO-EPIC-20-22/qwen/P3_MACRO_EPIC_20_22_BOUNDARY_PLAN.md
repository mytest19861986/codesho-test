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
   - RLS Policy: `USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);`.
2. **Foreign Key Topology (Zero Bare UUIDs)**:
   - All relational cross-table links enforce composite foreign keys `(tenant_id, target_id)`.
   - Deferrable integrity on actor references: `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`.
3. **Immutability & Revocation**:
   - `REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM PUBLIC, app_role;`
   - `REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM PUBLIC, app_role;`
   - `REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM PUBLIC, app_role;`
4. **21-Key PII Exclusion List**:
   - Metadata fields scrubbed against: `name`, `phone`, `email`, `national_id`, `location`, `avatar_url`, `phone_number`, `mobile`, `fingerprint`, `face_id`, `voice_sample`, `bank_account`, `iban`, `credit_card`, `card_number`, `cvv`, `password`, `token`, `secret`, `ssn`, `address`.

---

## 4. UI/UX Accessibility & BiDi Specifications

1. **Role Access**: Curriculum Managers & Program Operators (`/dashboard/admin/curriculum-operations`, `/dashboard/admin/cohort-schedules`).
2. **WCAG 2.2 AA Compliance**:
   - Minimum touch targets $\ge 44 \times 44\text{ px}$.
   - Minimum color contrast $4.5:1$ for body text, $3.0:1$ for UI controls.
   - High-visibility focus indicators.
3. **BiDi / RTL Isolation**:
   - All synthetic release versions, session timestamps, and metrics wrapped with `<bdi dir="ltr">`.
   - Layout strictly uses CSS logical properties (`margin-inline`, `padding-inline`).

---

## 5. Negative Test Proof Matrix (N1 - N33)

| ID | Domain Category | Target Invariant | Expected Behavior / Proof |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation | Query without `app.current_tenant` GUC | Fail-closed: 0 rows returned across all new tables |
| **N2** | Tenant Isolation | Cross-tenant UUID query | Rejection: 0 rows leaked across tenant boundaries |
| **N3** | Composite FK | Cross-tenant version or cohort assignment | IntegrityError: Foreign key violation |
| **N4** | Immutability | UPDATE query on `PUBLISHED` CurriculumVersion | Rejection / CheckConstraint violation |
| **N5** | Immutability | DELETE query on `PUBLISHED` CurriculumVersion | Rejection: Foreign key constraint or trigger prevents deletion |
| **N6** | Immutability | Direct UPDATE on `ModuleReleaseSnapshot` | Database Error: Permission Denied (REVOKE UPDATE) |
| **N7** | Immutability | Direct DELETE on `LessonReleaseSnapshot` | Database Error: Permission Denied (REVOKE DELETE) |
| **N8** | Immutability | Direct UPDATE or DELETE on Release Audit Log | Database Error: Permission Denied (REVOKE UPDATE, DELETE) |
| **N9** | Anti-Ranking | Query parameter attempting student ranking | 400 Bad Request: `ranking_queries_prohibited` |
| **N10** | Non-Authoritative | Aggregate record with `is_authoritative = TRUE` | CheckConstraint violation (`chk_deliveryagg_non_authoritative`) |
| **N11** | FSM Transition | Illegal transition `PUBLISHED` -> `DRAFT` | FSMValidationError (400 Bad Request) |
| **N12** | FSM Transition | Illegal transition `COMPLETED` -> `SCHEDULED` | FSMValidationError (400 Bad Request) |
| **N13** | Release Versioning | Semantic version format violation | CheckConstraint violation (`chk_curriculum_semver_format`) |
| **N14** | Release Approval | Approving curriculum version without reviewer role | 403 Forbidden |
| **N15** | Cohort Schedule | Schedule with `start_date > end_date` | CheckConstraint violation (`chk_cohortschedule_dates_order`) |
| **N16** | Session Occurrence | Session with `actual_start > actual_end` | CheckConstraint violation (`chk_session_timing_order`) |
| **N17** | Mentor Assignment | Assigning mentor outside cohort supervisor list | ValidationError: Mentor not authorized for cohort |
| **N18** | PII Blacklist | Injecting `'email'` into release metadata | CheckConstraint violation / ValidationError |
| **N19** | PII Blacklist | Injecting `'national_id'` into session notes | CheckConstraint violation / ValidationError |
| **N20** | PII Blacklist | Injecting phone number regex pattern in change record | CheckConstraint violation / ValidationError |
| **N21** | Concurrency | Concurrent release approval on same version | Managed via advisory transaction lock |
| **N22** | Concurrency | Concurrent session rescheduling on same occurrence | Managed via advisory transaction lock |
| **N23** | Historical Invariant | Attempt to rebind existing submission to new release | ValidationError / IntegrityError |
| **N24** | Historical Invariant | Attempt to delete course release referenced by active cohort | Protected by `ON DELETE RESTRICT` / `PROTECT` |
| **N25** | Attendance State | Automated punitive action trigger | Prohibited: Zero punitive actions generated |
| **N26** | Audit Log XOR | Audit log with 0 target entities set | CheckConstraint violation (`chk_curriculum_audit_xor`) |
| **N27** | Audit Log XOR | Audit log with >1 target entities set | CheckConstraint violation (`chk_curriculum_audit_xor`) |
| **N28** | Partial Unique Index | Duplicate active cohort schedule in same time window | IntegrityError |
| **N29** | Zero Bare UUID | Foreign key inspection verifying 0 bare UUIDs | Test Assert: 100% composite `(tenant_id, target_id)` |
| **N30** | Role Authorization | Student attempting to trigger curriculum release | 403 Forbidden |
| **N31** | Role Authorization | Student attempting to modify cohort learning session | 403 Forbidden |
| **N32** | Tenant GUC | Empty string `""` in `app.current_tenant` GUC | Fail-closed: 0 rows returned |
| **N33** | Positive Isolation | Valid isolated tenant query | Exact matched rows returned, 0 cross-tenant data leaked |

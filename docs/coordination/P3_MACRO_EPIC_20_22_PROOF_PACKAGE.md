# P3-MACRO-EPIC-20-22 Comprehensive Proof Package & Invariant Verification Matrix (v1.4-CANONICAL)

## 1. Upstream Pinning & Architectural Pre-Conditions (§2.1 Pin)
1. **Upstream Model Integrity & Precise Attribution**:
   - `learning_curriculumversion` pins strictly to `learning_course (tenant_id, course_id)` established in the foundational domain slices (VS1/VS2/VS5).
   - `learning_cohortschedule` pins strictly to `learning_cohort (tenant_id, cohort_id)` established and validated in VS13/VS14.
2. **Snapshot Provenance Exemption Register & Scoping**:
   - **Architectural Decision**: Columns `source_module_id` and `source_lesson_id` on `learning_modulereleasesnapshot` and `learning_lessonreleasesnapshot` are **registered immutable provenance pointers** exempt from dynamic foreign key constraints.
   - **Governance & Authority**: Snapshots strictly include `tenant_id` for tenant scoping. Provenance pointer columns are read-only metadata and strictly forbidden from participating in state machine transition decisions or active runtime authority checks.
   - **Deletion Path Distinction (N7 vs N10)**: Under N10, direct application-role `DELETE` is prohibited via `REVOKE DELETE`. N7 verifies cascading `ON DELETE SET NULL` upon tenant-privileged snapshot decommissioning or tenant wipe operations.
3. **Outbox Strategy**:
   - Outbox event propagation is **service-layer orchestrated via durable transaction outbox (`transaction.atomic()` with `append_outbox_event`)** identical to Macro-17-19; zero runtime external network calls inside database transactions; no standalone outbox table required in DDL.
4. **LearningSession Rescheduling Design Decision**:
   - Rescheduling transition `RESCHEDULED` -> `SCHEDULED` (re-arm) is an intentional operational capability allowing schedule adjustments prior to occurrence creation. Once a `SessionOccurrence` is instantiated, history is preserved via `learning_sessionchangerecord`.

---

## 2. Invariant Negative & Positive Test Matrix (N1 - N34) — 100% Aligned to DDL v1.1

| Test ID | Category | Target Invariant & Assertion Proof | Expected Result / SQL Assertion |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation | Query without `app.current_tenant` GUC set | Fail-closed: 0 rows returned across all 15 tables |
| **N2** | Tenant Isolation | GUC set to empty string `""` | Fail-closed: 0 rows returned |
| **N3** | Positive Isolation | Query with valid matching tenant GUC | Exactly tenant-owned rows returned; 0 cross-tenant leak |
| **N4** | Cross-Tenant Leakage | Cross-tenant UUID lookup in `CurriculumVersion` | Rejection / 0 rows leaked across tenant boundaries |
| **N5** | Cross-Tenant Leakage | Cross-tenant lookup in `LearningSession` & `SessionOccurrence` | Rejection / 0 rows leaked across tenant boundaries |
| **N6** | Composite FK Closure | Attempt to insert composite FK with mismatched `tenant_id` | `IntegrityError` (Violates PostgreSQL composite foreign key) |
| **N7** | Column-List Preservation | Deleting snapshot referenced by session (`ON DELETE SET NULL`) | Column-list preserved: only `(lesson_snapshot_id)` set to NULL |
| **N8** | Column-List Preservation | Deleting learning session referenced by occurrence (`ON DELETE CASCADE`) | Occurrence cascade cleanly removed with parent session |
| **N9** | Immutability Protection | Direct SQL `UPDATE` on `learning_modulereleasesnapshot` | Permission Denied (`REVOKE UPDATE ON learning_modulereleasesnapshot`) |
| **N10** | Immutability Protection | Direct SQL `DELETE` on `learning_lessonreleasesnapshot` | Permission Denied (`REVOKE DELETE ON learning_lessonreleasesnapshot`) |
| **N11** | Immutability Protection | Direct SQL `UPDATE` or `DELETE` on `learning_curriculumreleaseauditlog` | Permission Denied (`REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog`) |
| **N12** | Immutability Protection | Direct SQL `UPDATE` or `DELETE` on `learning_releaseapprovalrecord` | Permission Denied (`REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord`) |
| **N13** | Immutability Protection | Direct SQL `UPDATE` or `DELETE` on `learning_sessionchangerecord` | Permission Denied (`REVOKE UPDATE, DELETE ON learning_sessionchangerecord`) |
| **N14** | Immutability FSM | Consistency check: status != 'PUBLISHED' with published_at set | CheckConstraint Violation (`chk_curriculumversion_published_consistency`) |
| **N15** | Immutability FSM | Attempt to delete `PUBLISHED` CurriculumVersion referenced downstream | `IntegrityError` (`ON DELETE RESTRICT` via downstream releases) |
| **N16** | FSM Illegal Transition | Illegal transition `PUBLISHED` -> `DRAFT` | FSM Guard Rejection (`FSMValidationError`) |
| **N17** | FSM Illegal Transition | Illegal transition `COMPLETED` -> `SCHEDULED` | FSM Guard Rejection (`FSMValidationError`) |
| **N18** | FSM Illegal Transition | Illegal transition `CANCELLED` -> `IN_SESSION` | FSM Guard Rejection (`FSMValidationError`) |
| **N19** | Anti-Ranking Compliance | Query parameter or API attempting learner ranking or scores | 400 Bad Request: `ranking_queries_prohibited` |
| **N20** | Non-Authoritative State | Attempt to persist aggregate with `is_authoritative = TRUE` | CheckConstraint Violation (`chk_deliveryagg_non_authoritative`) |
| **N21** | Semver Non-Negative | Attempt to persist negative integer in semver (`semver_major < 0`) | CheckConstraint Violation (`chk_curriculum_semver_nonnegative`) |
| **N22** | Cohort Schedule Timing | Schedule with `start_date > end_date` | CheckConstraint Violation (`chk_cohortschedule_dates_order`) |
| **N23** | Occurrence Timing | Session occurrence with `actual_start > actual_end` | CheckConstraint Violation (`chk_session_timing_order`) |
| **N24** | Exception Resolution Order | Delivery exception with `resolved_at IS NULL` while status is `RESOLVED` | CheckConstraint Violation (`chk_deliveryexception_resolved_order`) |
| **N25** | PII Blacklist (JSONB) | CurriculumVersion metadata containing blacklisted PII key (e.g. `national_id`) | CheckConstraint Violation (`chk_curriculumversion_metadata_no_pii`) |
| **N26** | PII Free-Text Bound | Delivery exception description containing regex pattern or >4000 chars | CheckConstraint Violation (`chk_deliveryexception_desc_bound`) |
| **N27** | PII Free-Text Bound | Session occurrence notes containing regex pattern or >4000 chars | CheckConstraint Violation (`chk_sessionoccurrence_notes_bound`) |
| **N28** | PII Free-Text Bound | Release approval comments containing regex pattern or >4000 chars | CheckConstraint Violation (`chk_releaseapproval_comments_bound`) |
| **N29** | Audit XOR Integrity | Audit log with zero target entities populated (`num_nonnulls != 1`) | CheckConstraint Violation (`chk_curriculum_audit_xor`) |
| **N30** | Audit XOR Integrity | Audit log with both version and release populated (`num_nonnulls != 1`) | CheckConstraint Violation (`chk_curriculum_audit_xor`) |
| **N31** | Exclusion Constraint | Concurrent active cohort schedules in overlapping windows (`daterange &&`) | `IntegrityError` (Exclusion constraint violation `excl_cohortschedule_no_overlap` via `btree_gist`) |
| **N32** | Zero Bare UUIDs | Database schema introspection across all 15 tables (EXCLUDING registered provenance exemption list `source_module_id`, `source_lesson_id` per §1.2 register) | 100% Assertion Pass: Zero bare foreign key UUIDs |
| **N33** | Tenant Cascade Wipe | Hard deletion of tenant in test environment | Cascades clean across all tables with zero orphaned rows |
| **N34** | Malformed Tenant GUC | GUC set to malformed non-UUID value (e.g. `'malformed-tenant-uuid'`) | Fail-closed: 0 rows returned, safe DB error handling |
| **N35** | FSM Transition Guard | `SessionOccurrence` transition to `CONDUCTED` without `actual_start` / `actual_end` | FSM Guard Rejection (`FSMValidationError` / constraint violation) |
| **N36** | FSM Transition Guard | `SessionOccurrence` transition to `MISSED` with populated `actual_end` | FSM Guard Rejection (`FSMValidationError` / constraint violation) |
| **N37** | FSM Reverse Transition | Illegal reverse transition `CONDUCTED` -> `PENDING` or `RESOLVED` -> `INVESTIGATING` | FSM Guard Rejection (`FSMValidationError`) |
| **N38** | FSM Transition Guard | `DeliveryException` transition to `IGNORED` without `resolved_at` / `resolved_by` | FSM Guard Rejection (`FSMValidationError` / `chk_deliveryexception_resolved_order`) |

---

## 3. Finite State Machine (FSM) Transition Specifications — 100% DDL-Aligned

### 3.1. CurriculumVersion FSM (DDL: status IN ('DRAFT', 'REVIEW', 'APPROVED', 'PUBLISHED', 'RETIRED'))
```
[DRAFT] ──(submit_for_review / Author)──> [REVIEW]
[REVIEW] ──(approve / Reviewer)──────────> [APPROVED]
[REVIEW] ──(reject_to_draft / Reviewer)──> [DRAFT]
[APPROVED] ──(publish / ReleaseManager)──> [PUBLISHED] (IMMUTABLE, published_at NOT NULL)
[PUBLISHED] ──(retire / Admin)───────────> [RETIRED]
```

### 3.2. LearningSession FSM (DDL: status IN ('SCHEDULED', 'IN_SESSION', 'COMPLETED', 'RESCHEDULED', 'CANCELLED'))
```
[SCHEDULED] ──(open_session / Assigned Mentor or Program Ops)──────────> [IN_SESSION]
[IN_SESSION] ──(conclude_session / Assigned Mentor or Program Ops)─────> [COMPLETED]
[SCHEDULED] ──(reschedule / Program Ops; Mentor proposal only)────────> [RESCHEDULED] ──(re-arm / Program Ops)──> [SCHEDULED]
[SCHEDULED / RESCHEDULED] ──(cancel / Program Ops or Tenant Admin)─────> [CANCELLED]
```
*(Note: Initial state on INSERT is `SCHEDULED`. Domain Policy on CANCELLED: All existing child `SessionOccurrence` records in `PENDING` state are atomically transitioned to `MISSED` with cancellation audit event logged; existing historical completed occurrences remain immutable).*

### 3.3. SessionOccurrence FSM (DDL: occurrence_status IN ('PENDING', 'CONDUCTED', 'MISSED', 'SUBSTITUTE_CONDUCTED'))
*(Precondition: Creation permitted strictly when parent `LearningSession` is in `SCHEDULED` status; never from `RESCHEDULED`, `CANCELLED`, or `COMPLETED`).*
```
[PENDING] ──(conduct_primary / Assigned Mentor)────────────────────────> [CONDUCTED] (actual_start & actual_end NOT NULL)
[PENDING] ──(conduct_substitute / Authorized Substitute Mentor)────────> [SUBSTITUTE_CONDUCTED] (actual_start & actual_end NOT NULL)
[PENDING] ──(mark_missed / Assigned Mentor or Program Ops)─────────────> [MISSED] (actual_end IS NULL)
```

### 3.4. DeliveryException FSM (DDL: status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'IGNORED'))
```
[OPEN] ──(investigate / Program Ops or Tenant Admin)────────────────────> [INVESTIGATING] (resolved_at & resolved_by IS NULL)
[INVESTIGATING] ──(resolve / Program Ops or Tenant Admin)───────────────> [RESOLVED] (resolved_at & resolved_by NOT NULL)
[INVESTIGATING] ──(ignore / Program Ops or Tenant Admin)────────────────> [IGNORED] (resolved_at & resolved_by NOT NULL)
```
*(Note: Mentors have Reporter-only authority to create `OPEN` DeliveryExceptions. Domain Policy on Exception Recurrence: Recurring delivery issues instantiate a new deduplicated `DeliveryException` record referencing prior exception correlation ID per VS9 pattern; resolved exceptions remain terminal and immutable).*

---

## 4. Multi-Tenant Role & Domain Access Matrix

| Role / Context | Curriculum Governance | Cohort Scheduling | Session Operations | Operational Analytics | Audit Logs |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Anonymous** | DENY (401) | DENY (401) | DENY (401) | DENY (401) | DENY (401) |
| **Cross-Tenant** | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) |
| **Student / Learner** | READ (Published only) | READ (Assigned cohort) | READ (Attending only) | DENY (403) | DENY (403) |
| **Mentor / Instructor**| READ (Published) | READ (Assigned cohort) | UPDATE (SessionOccurrence notes only per N27) | READ (Assigned cohorts) | DENY (403) |
| **Curriculum Author** | CREATE / UPDATE (Draft) | READ | READ | READ | READ (Own domain via single-path author filter) |
| **Program Operations** | READ / APPROVE | FULL CRUD | FULL CRUD | FULL READ / AGGREGATE | FULL READ |
| **Tenant Admin** | FULL CONTROL | FULL CONTROL | FULL CONTROL | FULL CONTROL | FULL READ (Append-Only) |

---

## 5. Formal Write Manifest & Runtime Target Artefacts

1. **Database Schema & Migrations**:
   - `backend/apps/learning/migrations/0014_p3_macro_epic_20_22_curriculum_delivery.py` (Contains 15 tables, `FORCE ROW LEVEL SECURITY`, `NOBYPASSRLS`, composite FKs, DDL constraints including `excl_cohortschedule_no_overlap` via `btree_gist`, and append-only `REVOKE` statements).
2. **Domain Models**:
   - `backend/apps/learning/models/curriculum.py` (`CurriculumVersion`, `ModuleReleaseSnapshot`, `LessonReleaseSnapshot`, `CurriculumReleaseAuditLog`, `ReleaseApprovalRecord`).
   - `backend/apps/learning/models/delivery.py` (`CohortSchedule`, `LearningSession`, `SessionOccurrence`, `DeliveryException`, `SessionChangeRecord`, `DeliveryAggregate`).
3. **Automated Verification Suites**:
   - `backend/tests/learning/test_p3_macro_epic_20_22_isolation.py` (Tests N1–N6, N33–N34).
   - `backend/tests/learning/test_p3_macro_epic_20_22_fsm_guards.py` (Tests N14–N18, N35–N38).
   - `backend/tests/learning/test_p3_macro_epic_20_22_immutability_constraints.py` (Tests N7–N13, N19–N32).
4. **API Endpoints & Serialization**:
   - `backend/apps/learning/api/v1/curriculum_delivery_views.py` (DRF API views adhering to strict OpenAPI contract and 400 Bad Request on ranking parameters).
   - `backend/apps/learning/api/v1/curriculum_delivery_serializers.py` (Input validation with bounded text limits and regex hygiene).
5. **OpenAPI Schema Contract (G-B)**:
   - `docs/openapi.yaml` (Updated with canonical endpoint contracts for curriculum releases and delivery sessions).
6. **Architecture Decisions & Pins (G-C, G-D)**:
   - **G-C Single-Path Read Scope Pin**: Learner and Mentor access to assigned cohorts and attending sessions is strictly scoped via single-path author/assigned query filters (Pattern A inheritance from VS9-G2).
   - **G-D Closed Boundary Semantic Decision**: Cohort schedule exclusion uses `daterange(start_date, end_date, '[]')` which intentionally treats shared boundary dates as overlapping, preventing same-day handover collisions by design.

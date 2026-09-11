# P3-MACRO-EPIC-20-22 Comprehensive Proof Package & Invariant Verification Matrix (v1.3-ALIGNED)

## 1. Upstream Pinning & Architectural Pre-Conditions (§2.1 Pin)
1. **Upstream Model Integrity & Precise Attribution**:
   - `learning_curriculumversion` pins strictly to `learning_course (tenant_id, course_id)` established in the foundational domain slices (VS1/VS2/VS5).
   - `learning_cohortschedule` pins strictly to `learning_cohort (tenant_id, cohort_id)` established and validated in VS13/VS14.
2. **Snapshot Provenance Exemption Declaration**:
   - **Architectural Decision**: References `source_module_id` and `source_lesson_id` on `learning_modulereleasesnapshot` and `learning_lessonreleasesnapshot` are **intentional immutable provenance pointers** exempt from dynamic foreign key constraints by design.
   - **Rationale**: Post-snapshot, authoring draft modules/lessons may be deleted, updated, or refactored without corrupting immutable historical release artifacts. The frozen JSONB/relational payload of the snapshot is the sole authoritative representation.
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
| **N31** | Partial Unique Constraint | Concurrent active cohort schedules in overlapping windows | `IntegrityError` (Unique index violation) |
| **N32** | Zero Bare UUIDs | Database schema introspection across all 15 tables | 100% Assertion Pass: Zero bare foreign key UUIDs |
| **N33** | Tenant Cascade Wipe | Hard deletion of tenant in test environment | Cascades clean across all tables with zero orphaned rows |
| **N34** | Malformed Tenant GUC | GUC set to malformed non-UUID value (e.g. `'malformed-tenant-uuid'`) | Fail-closed: 0 rows returned, safe DB error handling |

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
[SCHEDULED] ──(open_session)──────────> [IN_SESSION]
[IN_SESSION] ──(conclude_session)─────> [COMPLETED]
[SCHEDULED] ──(reschedule)────────────> [RESCHEDULED] ──(re-arm)──> [SCHEDULED]
[SCHEDULED / RESCHEDULED] ──(cancel)──> [CANCELLED]
```
*(Note: Initial state on INSERT is `SCHEDULED`; no ephemeral 'DRAFT' status in DDL)*

### 3.3. SessionOccurrence FSM (DDL: occurrence_status IN ('PENDING', 'CONDUCTED', 'MISSED', 'SUBSTITUTE_CONDUCTED'))
```
[PENDING] ──(conduct_primary)─────────> [CONDUCTED] (actual_start & actual_end NOT NULL)
[PENDING] ──(conduct_substitute)──────> [SUBSTITUTE_CONDUCTED] (actual_start & actual_end NOT NULL)
[PENDING] ──(mark_missed)─────────────> [MISSED] (actual_end IS NULL)
```

### 3.4. DeliveryException FSM (DDL: status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'IGNORED'))
```
[OPEN] ──(investigate)────────────────> [INVESTIGATING] (resolved_at & resolved_by IS NULL)
[INVESTIGATING] ──(resolve)───────────> [RESOLVED] (resolved_at & resolved_by NOT NULL)
[INVESTIGATING] ──(ignore)────────────> [IGNORED] (resolved_at & resolved_by NOT NULL)
```

---

## 4. Multi-Tenant Role & Domain Access Matrix

| Role / Context | Curriculum Governance | Cohort Scheduling | Session Operations | Operational Analytics | Audit Logs |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Anonymous** | DENY (401) | DENY (401) | DENY (401) | DENY (401) | DENY (401) |
| **Cross-Tenant** | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) | DENY (0 rows / 404) |
| **Student / Learner** | READ (Published only) | READ (Assigned cohort) | READ (Attending only) | DENY (403) | DENY (403) |
| **Mentor / Instructor**| READ (Published) | READ (Assigned cohort) | UPDATE (Session notes) | READ (Assigned cohorts) | DENY (403) |
| **Curriculum Author** | CREATE / UPDATE (Draft) | READ | READ | READ | READ (Own domain) |
| **Program Operations** | READ / APPROVE | FULL CRUD | FULL CRUD | FULL READ / AGGREGATE | FULL READ |
| **Tenant Admin** | FULL CONTROL | FULL CONTROL | FULL CONTROL | FULL CONTROL | FULL READ (Append-Only) |

# P3-MACRO-EPIC-17-19 Boundary Plan & Architecture Specification (v1.2-CANONICAL)

## 1. Epic Overview
- Epic ID: `P3-MACRO-EPIC-17-19-MENTOR-OPERATIONS-AND-PROGRAM-SUCCESS`
- Branch: `codex/phase3-product-platform-foundation`
- Authority: `COMMANDER_P3_VS16_CLOSURE_AND_MACRO_EPIC_17_19_DIRECTIVE`
- Delivery Mode: `MACRO_FAST_ENTERPRISE` (Single Epic Package, Combined Discovery, Parallel Fleet Review)
- Scope: Mentor Caseload Management, Support Queues, Learning Check-ins Orchestration, Program Success Support Analytics, and Shared Append-Only Mentor Operations Audit Log.
- Response-Record Identity: Fully and strictly addresses GLM v1.2 Audit findings (Blocker REVOKE and Majors M-A through M-D).

---

## 2. Integrated Slices Architecture & Domain Boundaries

### 2.1. Prerequisites, Upstream Foundation & Dependencies
- Upstream Task Pin: `P3-VS16-MENTOR-STUDENT-SUCCESS-COACHING-AND-INTERVENTION-WORKFLOW` (Certified with Complete Acceptance: `4992219`, `QWEN_FINAL: PASS`, `GLM_FINAL: PASS`, `GEMINI_UI_FINAL: PASS`).
- Shared Models & Dependencies:
  - `learning_coachingsession`: Target of `fk_supportqueue_session` (VS16 upstream).
  - `learning_supportintervention`: Target of `fk_supportqueue_intervention` (VS16 upstream).
- Tenant Isolation: Strict fail-closed multi-tenancy enforced by PostgreSQL 17 `FORCE ROW LEVEL SECURITY` and `NOBYPASSRLS`.
- Session Isolation: GUC `app.current_tenant` initialized strictly inside `transaction.atomic()`.
- Audit Discipline: Dedicated append-only `learning_mentoroperationsauditlog` with `DEFERRABLE INITIALLY DEFERRED` foreign keys protecting historical audit records from parent deletion, coupled with strict `REVOKE UPDATE, DELETE ON learning_mentoroperationsauditlog FROM PUBLIC, app_role`.

### 2.2. P3-VS17: Mentor Caseload & Support Operations
- **Core Models**:
  - `MentorCaseloadAssignment`: Mapping of student to mentor with active/inactive statuses, capacity weight (`CHECK (capacity_weight >= 0.10 AND capacity_weight <= 5.00)`), and bounded unassignment reasoning.
  - `SupportQueueItem`: Operational queue of mentor actions (due date, urgency level, queue status, bounded resolution notes).
- **Invariants**:
  - ZERO Ranking / Zero Behavioral Scoring: Urgency is strictly operational, never derived from student psychology or opaque algorithms.
  - Active assignment partial unique index: `UNIQUE (tenant_id, student_id) WHERE (is_active = TRUE)`.
  - Mentor Foreign Key: `fk_mentorcaseload_mentor` and `fk_supportqueue_mentor` are strictly `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`.
  - Composite foreign keys with exact column-list `ON DELETE SET NULL`:
    - `fk_supportqueue_intervention`: `ON DELETE SET NULL (source_intervention_id)`
    - `fk_supportqueue_session`: `ON DELETE SET NULL (source_session_id)`
  - Origin semantics: At least one origin required (`chk_supportqueue_origin_at_least_one`).

### 2.3. P3-VS18: Learning Check-ins, Scheduling & Follow-up Orchestration
- **Core Models**:
  - `LearningCheckIn`: Structured check-in sessions with status, scheduled start, actual timing, safe meeting link, and student voluntary acknowledgement.
  - `FollowUpCommitment`: Mutual commitments with owner role (`MENTOR` or `STUDENT`), bounded title, due date, and completion status.
- **FSM State & Transition Matrix**:
  | Current State | Permitted Event / Action | Target State | Authorized Actor | Transition Guard / Preconditions |
  |:---|:---|:---|:---|:---|
  | `SCHEDULED` | `START_CHECKIN` | `IN_PROGRESS` | Assigned Mentor | `clock_timestamp() >= scheduled_start - INTERVAL '15 minutes'`, `actual_start` set |
  | `SCHEDULED` | `RESCHEDULE_CHECKIN` | `RESCHEDULED` | Assigned Mentor | New check-in created referencing `rescheduled_from_id` |
  | `SCHEDULED` | `CANCEL_CHECKIN` | `CANCELLED` | Assigned Mentor / Admin | Cancellation reason logged in audit log |
  | `IN_PROGRESS` | `COMPLETE_CHECKIN` | `COMPLETED` | Assigned Mentor | `actual_end` set, `actual_start <= actual_end`, commitments recorded |
  | `RESCHEDULED` | Final State | — | — | Read-only terminal state |
  | `CANCELLED` | Final State | — | — | Read-only terminal state |
  | `COMPLETED` | Final State | — | — | Read-only terminal state; student acknowledgement optional |
- **Invariants**:
  - Timing Order: `scheduled_start <= actual_start` and `actual_start <= actual_end`.
  - Mentor Foreign Key: `fk_checkin_mentor` is strictly `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`.
  - Student acknowledgement is non-punitive and voluntary.

### 2.4. P3-VS19: Program Success Operations & Support Analytics
- **Core Models / Projections**:
  - `ProgramSupportAggregate`: Periodic aggregate calculations (coverage ratio, response time, completed check-ins).
- **Invariants**:
  - Strict Non-Authoritative Check: `CONSTRAINT chk_supportagg_non_authoritative CHECK (is_authoritative = FALSE)`.
  - Anti-Ranking Invariant: Zero student leaderboards, zero competitive gamification, zero comparative public percentiles.

### 2.5. Actor & Authorization Matrix
| Actor Role | Caseload Management | Support Queue | Check-ins Orchestration | Follow-up Commitments | Program Aggregates | Audit Log |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Platform / Tenant Admin** | View / Reassign | View / Oversee | View All | View All | Generate / View | Read-Only |
| **Assigned Mentor** | Full Management | Resolve / Dismiss | Schedule / Complete | Create / Complete | View Cohort Stats | Read-Only (Self Actions) |
| **Student** | Read-Only (Assigned Mentor) | N/A (Internal Queue) | View / Acknowledge | View / Complete Assigned | N/A | N/A |
| **Anonymous / Cross-Tenant** | REJECT (403/RLS 0) | REJECT (403/RLS 0) | REJECT (403/RLS 0) | REJECT (403/RLS 0) | REJECT (403/RLS 0) | REJECT (403/RLS 0) |

---

## 3. Database Schema & PostgreSQL 17 RLS Specification

1. **FORCE ROW LEVEL SECURITY & DROP POLICY IF EXISTS**:
   - Enforced on all 6 tables (`learning_mentorcaseloadassignment`, `learning_supportqueueitem`, `learning_learningcheckin`, `learning_followupcommitment`, `learning_programsupportaggregate`, `learning_mentoroperationsauditlog`).
2. **Mentor Topology & DEFERRABLE Constraints**:
   - All relations reference `(tenant_id, target_id)`.
   - All three mentor foreign keys are `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` matching platform standard:
     - `fk_mentorcaseload_mentor`
     - `fk_supportqueue_mentor`
     - `fk_checkin_mentor`
3. **Composite Foreign Keys & SET NULL Discipline**:
   - All `ON DELETE SET NULL` clauses specify exact column-lists preserving `tenant_id`:
     - `fk_supportqueue_intervention`: `ON DELETE SET NULL (source_intervention_id)`
     - `fk_supportqueue_session`: `ON DELETE SET NULL (source_session_id)`
     - `fk_checkin_rescheduled_from`: `ON DELETE SET NULL (rescheduled_from_id)`
4. **Append-Only Revocation (Blocker Resolution)**:
   - `REVOKE UPDATE, DELETE ON learning_mentoroperationsauditlog FROM PUBLIC, app_role;`
5. **Partial Indexes for Audit Log Targets**:
   - 5 dedicated partial indexes for fast queries on non-null targets (`target_caseload_id`, `target_queue_item_id`, `target_checkin_id`, `target_commitment_id`, `target_aggregate_id`).
6. **Comprehensive 21-Key PII Blacklist & Regex Filtering**:
   - JSONB `?|` array includes all 21 sensitive keys across metadata/details fields:
     `'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number', 'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card', 'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'`.
   - Free-text fields (`notes`, `resolution_notes`, `unassignment_reason`, `title`, `meeting_link`) bounded by length (<= 4000) and guarded by comprehensive regex anti-PII constraints.

---

## 4. UI/UX Design System & Accessibility Specification

1. **Mentor Workspace**:
   - High visual excellence, low cognitive load, responsive layout across desktop (`1440x900`) and mobile (`390x844`).
   - Clear three-tab operational navigation: Caseload, Check-ins, Program Analytics.
2. **BiDi & RTL Isolation**:
   - Pure CSS logical properties (`margin-inline`, `padding-inline`).
   - Mandatory `<bdi dir="ltr">` wrapping for all synthetic codes, dates, timestamps, and numbers.
3. **WCAG 2.2 AA**:
   - Touch targets $\ge 44 \times 44\text{ px}$.
   - Text contrast $\ge 4.5:1$, UI elements $\ge 3.0:1$.
   - Complete keyboard navigability and high-visibility focus rings.

---

## 5. Negative Test Proof Matrix (N1 - N33)

| ID | Category | Target Invariant | Expected Rejection / Assertion |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation | Unset GUC `app.current_tenant` | Fail-closed: 0 rows visible / returned |
| **N2** | Tenant Isolation | Cross-tenant UUID query | Rejection: 0 rows returned across all 6 tables |
| **N3** | Composite FK | Cross-tenant FK assignment | IntegrityError: Foreign key violation across tenants |
| **N4** | SET NULL Integrity | Parent intervention deletion | Sets `source_intervention_id` to NULL, preserves `tenant_id` |
| **N5** | SET NULL Integrity | Parent session deletion | Sets `source_session_id` to NULL, preserves `tenant_id` |
| **N6** | SET NULL Integrity | Parent checkin deletion on rescheduled | Sets `rescheduled_from_id` to NULL, preserves `tenant_id` |
| **N7** | Non-Authoritative | Attempt to insert aggregate with `is_authoritative = TRUE` | CheckConstraint violation (`chk_supportagg_non_authoritative`) |
| **N8** | Anti-Ranking | Query parameter requesting student leaderboard or ranking | 400 Bad Request: `ranking_queries_prohibited` |
| **N9** | Check-in Timing | Check-in with `actual_start > actual_end` | CheckConstraint violation (`chk_checkin_timing_order`) |
| **N10** | Check-in Timing | Check-in with `actual_start < scheduled_start` | CheckConstraint violation (`chk_checkin_timing_order`) |
| **N11** | Caseload Order | Inactive caseload assignment with `unassigned_at IS NULL` | CheckConstraint violation (`chk_mentorcaseload_unassigned_order`) |
| **N12** | Caseload Order | Caseload with `unassigned_at < assigned_at` | CheckConstraint violation (`chk_mentorcaseload_unassigned_order`) |
| **N13** | Queue Resolution | Queue item `RESOLVED` with `resolved_at IS NULL` | CheckConstraint violation (`chk_supportqueue_resolved_order`) |
| **N14** | Queue Resolution | Queue item `PENDING` with `resolved_at IS NOT NULL` | CheckConstraint violation (`chk_supportqueue_resolved_order`) |
| **N15** | Commitment Order | Completed commitment with `completed_at IS NULL` | CheckConstraint violation (`chk_commitment_completed_order`) |
| **N16** | PII Blacklist | Injecting `'email'` or `'phone'` into Caseload metadata | CheckConstraint violation (`chk_mentorcaseload_metadata_no_pii`) |
| **N17** | PII Blacklist | Injecting `'national_id'` into SupportQueue metadata | CheckConstraint violation (`chk_supportqueue_metadata_no_pii`) |
| **N18** | PII Blacklist | Injecting `'card_number'` into Check-in metadata | CheckConstraint violation (`chk_checkin_metadata_no_pii`) |
| **N19** | PII Blacklist | Injecting phone number regex pattern in Check-in notes | CheckConstraint violation (`chk_checkin_notes_bound`) |
| **N20** | PII Blacklist | Injecting IBAN in Queue resolution notes | CheckConstraint violation (`chk_supportqueue_resolution_notes_bound`) |
| **N21** | Audit Log XOR | Audit log with 0 targets set | CheckConstraint violation (`chk_mentoropsaudit_target_exact_xor`) |
| **N22** | Audit Log XOR | Audit log with >1 targets set | CheckConstraint violation (`chk_mentoropsaudit_target_exact_xor`) |
| **N23** | Audit Protection | Attempt to CASCADE delete audit log on checkin delete | Prevented by `DEFERRABLE INITIALLY DEFERRED` FK |
| **N24** | FSM Transition | Illegal transition `COMPLETED` -> `SCHEDULED` in Check-in | FSMValidationError (400 Bad Request) |
| **N25** | Concurrency | Concurrent status updates on same Queue item | Managed via `pg_advisory_xact_lock(hashtext('queue_item_' \|\| id::text))` |
| **N26** | Authorization | Student attempting to resolve Support Queue item | 403 Forbidden |
| **N27** | Authorization | Unassigned mentor attempting to modify Caseload | 403 Forbidden |
| **N28** | Partial Unique Index | Attempting to create duplicate active caseload for student | IntegrityError (`uq_mentorcaseload_active_student`) |
| **N29** | Aggregate Period | Aggregate record with `period_start > period_end` | CheckConstraint violation (`chk_supportagg_period_order`) |
| **N30** | Zero Bare UUID | Schema inspection test verifying 0 bare UUID foreign keys | Test Assert: 100% composite foreign keys |
| **N31** | Tenant Isolation GUC | GUC set to empty string `""` | Fail-closed: 0 rows returned across all 6 tables |
| **N32** | Tenant Isolation GUC | GUC set to invalid non-UUID string | Fail-closed / PostgreSQL syntax rejection: 0 rows leaked |
| **N33** | Positive Isolation Test | Valid tenant matching GUC `app.current_tenant` | Exact isolated rows returned, zero cross-tenant leakage |

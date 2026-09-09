# P3-VS15 Boundary Plan, DDL & Proof Matrix (v1.2)

## Vertical Slice Identifier
- Task ID: `P3-VS15-LEARNING-CONTINUITY-AND-STUDENT-SUCCESS-PLANNING`
- Branch: `codex/phase3-product-platform-foundation`
- Authority: `COMMANDER_P3_VS15_DISCOVERY_UNLOCK`
- Audit Response: Formally addresses GLM v1.1 findings (B1, M-A, M-B, m1, m3, m4)
- Fleet Standard GUC: `app.current_tenant`
- Session Protocol: `SET LOCAL "app.current_tenant" = %s` strictly inside `transaction.atomic()`

---

## 1. §2.1 Prerequisites & Upstream Dependencies
- P3-VS1 to P3-VS14 Certified:
  - `learning_learningmilestone(tenant_id, id)`: Certified in P3-VS13 with tenant-scoped unique active milestone code index (`learning_learningmilestone_tenant_id_uniq`). Referenced by `fk_timelineevent_target_milestone`.
  - `learning_studentlearninggoal(tenant_id, id)`: Certified with active singleton per domain and max 5 active goals. Referenced by `fk_timelineevent_target_goal`.
  - `learning_learninginsight(tenant_id, id)`: Certified with partial unique singleton index. Referenced by `fk_timelineevent_target_insight`.
  - `learning_learningreflection(tenant_id, id)`: Certified immutable reflection journal. Referenced by `fk_timelineevent_target_reflection`.
  - `learning_successactionstep(tenant_id, id)`: Internal P3-VS15 action step entity referenced by `fk_timelineevent_target_action`.
  - All foreign keys enforce composite tenant scoping `(tenant_id, target_id)`.

---

## 2. Finite State Machines (FSM) & Transition Matrices (M1, m1 Addressed)

### 2.1 StudentSuccessPlan FSM Matrix
| Initial State | Event / Trigger | Target State | Permitted Actors | Guard Conditions & Invariants | Side Effects / Audit Action |
|:---|:---|:---|:---|:---|:---|
| `[INIT]` | `CREATE_SUCCESS_PLAN` | `ACTIVE` | Student, Mentor | `uq_successplan_student_active` (Max 1 active plan per student per tenant); title len 3-255; valid `target_period` | Insert plan; Emit `CREATE_SUCCESS_PLAN` audit log |
| `ACTIVE` | `PAUSE_SUCCESS_PLAN` | `PAUSED` | Student, Mentor | `paused_at` set to `clock_timestamp()`; non-punitive pause | Sets `paused_at`; Emit `PAUSE_SUCCESS_PLAN` audit log |
| `PAUSED` | `RESUME_SUCCESS_PLAN` | `ACTIVE` | Student, Mentor | Verifies no other active plan exists; clears `paused_at` | Sets `status='ACTIVE'`, `paused_at=NULL`; Emit `RESUME_SUCCESS_PLAN` audit log |
| `ACTIVE` | `COMPLETE_SUCCESS_PLAN` | `COMPLETED` | Student, Mentor | Sets `completed_at`; all mandatory action steps completed or skipped | Sets `completed_at`; Emit `COMPLETE_SUCCESS_PLAN` audit log |
| `ACTIVE`, `PAUSED` | `SUPERSEDE_SUCCESS_PLAN` | `SUPERSEDED` | Student, Mentor | Sets `superseded_at`; atomically transitioned when a newer plan is initialized | Releases active singleton; Emit `SUPERSEDE_SUCCESS_PLAN` audit log |
| `ACTIVE`, `PAUSED`, `COMPLETED` | `ARCHIVE_SUCCESS_PLAN` | `ARCHIVED` | Student, Staff | Sets `archived_at`; terminal non-punitive archive (completed plans can be archived) | Sets `archived_at`; Emit `ARCHIVE_SUCCESS_PLAN` audit log |

### 2.2 SuccessActionStep FSM Matrix
| Initial State | Event / Trigger | Target State | Permitted Actors | Guard Conditions & Invariants | Side Effects / Audit Action |
|:---|:---|:---|:---|:---|:---|
| `[INIT]` | `CREATE_ACTION_STEP` | `PENDING` | Student, Mentor | `sequence_order >= 1`; `uq_actionstep_tenant_plan_seq`; `is_authoritative = FALSE` | Inserts step; Emit `CREATE_ACTION_STEP` audit log |
| `PENDING` | `START_ACTION_STEP` | `IN_PROGRESS` | Student | Step belongs to active plan; `is_authoritative = FALSE` | Updates status; Emit `TRANSITION_ACTION_STEP` audit log |
| `PENDING`, `IN_PROGRESS` | `COMPLETE_ACTION_STEP` | `COMPLETED` | Student, Mentor | `completed_at` set to `clock_timestamp()` | Sets `completed_at`; Appends `ACTION_DISPATCHED` timeline event |
| `PENDING`, `IN_PROGRESS` | `SKIP_ACTION_STEP` | `SKIPPED` | Student, Mentor | Non-punitive skip; reason optional in metadata | Updates status; Emit `TRANSITION_ACTION_STEP` audit log |
| `PENDING`, `IN_PROGRESS` | `CANCEL_ACTION_STEP` | `CANCELLED` | Student, Mentor | Step obsoleted; non-punitive | Updates status; Emit `TRANSITION_ACTION_STEP` audit log |

### 2.3 SuccessTimelineEvent Lifecycle & Target Coupling (B1, M2, M3, m4 Addressed)
| Event Type | Permitted Target Column | Referenced Entity | Permitted Actors | Invariant / Coupling Guard |
|:---|:---|:---|:---|:---|
| `GOAL_ANCHORED` | `target_goal_id` | `learning_studentlearninggoal` (P3-VS1) | Student | Exact 1-to-1: `target_goal_id IS NOT NULL` |
| `INSIGHT_CONNECTED` | `target_insight_id` | `learning_learninginsight` (P3-VS13) | System, Mentor | Exact 1-to-1: `target_insight_id IS NOT NULL` |
| `REFLECTION_TIED` | `target_reflection_id` | `learning_learningreflection` (P3-VS12) | Student | Exact 1-to-1: `target_reflection_id IS NOT NULL` |
| `ACTION_DISPATCHED` | `target_action_step_id` | `learning_successactionstep` (P3-VS15) | Student, Mentor | Exact 1-to-1: `target_action_step_id IS NOT NULL` |
| `MILESTONE_PROGRESSION` | `target_milestone_id` | `learning_learningmilestone` (P3-VS13) | Student, Mentor | Exact 1-to-1: `target_milestone_id IS NOT NULL` |
| `TIMELINE_EVENT_AMENDED`| `replaces_event_id` | `learning_successtimelineevent` (P3-VS15)| Student, Mentor | Append-only correction: `replaces_event_id IS NOT NULL` |

### 2.4 Timeline Amendment & Idempotency Semantics (m4 Addressed)
1. **Append-Only Correction Semantics**: Direct `UPDATE` or `DELETE` on timeline events is revoked at the database level (`REVOKE UPDATE, DELETE`). If a narrative entry or link requires factual amendment, an append-only compensating event (`TIMELINE_EVENT_AMENDED`) is inserted with `replaces_event_id` pointing to the prior entry in the same tenant. The audit trail remains fully immutable.
2. **Idempotent Append Discipline**: Every timeline event accepts an optional `client_mutation_id UUID NULL`. The partial unique index `uq_timelineevent_tenant_mutation` guarantees that network retries or duplicate webhook dispatches with the same mutation ID are rejected or de-duplicated without creating ghost timeline entries.

### 2.5 Actor & Authorization Matrix
| Entity / Action | Student (Self) | Student (Peer / Cross-Tenant) | Mentor (Assigned Cohort) | Mentor (Unassigned Cohort) | Admin / Owner |
|:---|:---|:---|:---|:---|:---|
| `StudentSuccessPlan` (Create) | ALLOW | DENY (404/403) | ALLOW (Collaborative planning) | DENY (403 Forbidden) | ALLOW (Tenant ops) |
| `StudentSuccessPlan` (Read) | ALLOW | DENY (404/403) | ALLOW (Assigned cohort only) | DENY (403 Forbidden) | ALLOW |
| `StudentSuccessPlan` (Update / Pause / Archive) | ALLOW | DENY (404/403) | ALLOW (Assigned cohort only) | DENY (403 Forbidden) | ALLOW |
| `SuccessActionStep` (Create / Progress) | ALLOW | DENY (404/403) | ALLOW (Assigned cohort only) | DENY (403 Forbidden) | ALLOW |
| `SuccessTimelineEvent` (Append) | ALLOW (Formative actions) | DENY (404/403) | ALLOW (Formative feedback) | DENY (403 Forbidden) | ALLOW |
| `SuccessTimelineEvent` (Read) | ALLOW | DENY (404/403) | ALLOW (Assigned cohort only) | DENY (403 Forbidden) | ALLOW |
| `SuccessAuditLog` (Read) | DENY | DENY | DENY | DENY | ALLOW (Staff audit) |

---

## 3. Detailed Negative Proof Matrix (N1 – N27) (B1, M-A Addressed)

| Test ID | Test Category | Target Condition | Expected Result & Verification Mechanism |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation GUC | Query `learning_studentsuccessplan` without `SET LOCAL app.current_tenant` | Empty set / 0 rows (Fail-Closed) |
| **N2** | Tenant Isolation GUC | Query `learning_successtimelineevent` with wrong tenant UUID | Empty set / 0 rows (Fail-Closed) |
| **N3** | Cross-Tenant Membership | Insert `StudentSuccessPlan` pointing to `student_id` of Tenant B | Composite FK `fk_studentsuccessplan_student` violation -> DB REJECT |
| **N4** | Cross-Tenant Plan Leakage | Insert `SuccessActionStep` pointing to `plan_id` of Tenant B | Composite FK `fk_successactionstep_plan` violation -> DB REJECT |
| **N5** | Active Singleton Proof | Insert second `ACTIVE` plan for same student in same tenant | Partial unique index `uq_successplan_student_active` violation -> DB REJECT |
| **N6** | Anti-Automated Decider | System generates action step marked `is_authoritative = TRUE` | Constraint `chk_step_non_authoritative` violation -> DB REJECT |
| **N7** | 5-way XOR Continuity | Insert timeline event with zero targets or multiple targets | Constraint `chk_timeline_target_xor` violation -> DB REJECT |
| **N8** | Type-Target Mismatch (M3) | Insert `GOAL_ANCHORED` event linking `target_action_step_id` | Constraint `chk_timeline_type_target_coupling` violation -> DB REJECT |
| **N9** | Append-Only Invariant | Attempt `UPDATE` or `DELETE` on `learning_successtimelineevent` | Permission Denied / DB Revoke -> DB REJECT |
| **N10** | Append-Only Audit Log | Attempt `UPDATE` or `DELETE` on `learning_successauditlog` | Permission Denied / DB Revoke -> DB REJECT |
| **N11** | Plan Deferrable FK (M4) | Delete student success plan with linked timeline events | `ON DELETE NO ACTION DEFERRABLE` blocks silent purge -> DB REJECT |
| **N12** | Sequence Order Positive (M6)| Insert `SuccessActionStep` with `sequence_order = 0` or negative | Constraint `chk_actionstep_seq_positive` violation -> DB REJECT |
| **N13** | Sequence Order Unique (M6) | Insert two `SuccessActionStep` with same `sequence_order` for same plan | Constraint `uq_actionstep_tenant_plan_seq` violation -> DB REJECT |
| **N14** | Milestone FK (B1) | Insert `MILESTONE_PROGRESSION` event with non-existent milestone ID in `learning_learningmilestone` | Composite FK `fk_timelineevent_target_milestone` violation -> DB REJECT |
| **N15** | Headline Length Bounds (M5)| Insert timeline event with `headline = 'ab'` (len < 3) or > 255 chars | Constraint `chk_timeline_headline_len` violation -> DB REJECT |
| **N16** | Headline PII Scrub (M5) | Insert timeline event headline containing phone number or credit card | Constraint `chk_timeline_headline_no_pii` violation -> DB REJECT |
| **N17** | Detail Text Bounds (M5) | Insert timeline event detail text exceeding 4000 characters | Constraint `chk_timeline_detail_len` violation -> DB REJECT |
| **N18** | Notes Text Bounds (M5) | Insert success plan notes exceeding 4000 characters | Constraint `chk_successplan_notes_len` violation -> DB REJECT |
| **N19** | PII Blacklist JSONB | Inject `{"national_id": "0012345678"}` into timeline event metadata | Constraint `chk_timeline_metadata_no_pii` (`?\|`) violation -> DB REJECT |
| **N20** | PII Blacklist Audit Log | Inject `{"iban": "IR123456..."}` into audit log metadata | Constraint `chk_successaudit_metadata_no_pii` (`?\|`) violation -> DB REJECT |
| **N21** | FSM Illegal Direct Transition| Transition `StudentSuccessPlan` from `ARCHIVED` directly to `ACTIVE` | FSM Guard rejects invalid transition -> 400 Bad Request |
| **N22** | Completion Consistency | Set step `status='COMPLETED'` with `completed_at=NULL` | Constraint `chk_step_completion_consistency` violation -> DB REJECT |
| **N23** | Anti-Ranking Policy | Query success plans with `?rank=true` or leaderboard query params | REST API returns 400 Bad Request (Anti-Ranking Policy) |
| **N24** | Cross-Cohort Mentor Guard | Mentor queries success plan of student in unassigned cohort | Service permission check returns 403 Forbidden |
| **N25** | Tenant Wipe Clean Cascade | Delete tenant entity via `platform_tenant_tenant` cascade | Deferrable FK topology cascades cleanly without deadlock -> DB PASS |
| **N26** | Empty String GUC Guard (M-A)| Set GUC `app.current_tenant = ''` (empty string) | `NULLIF` yields NULL -> RLS denies all rows (Fail-Closed, 0 rows) |
| **N27** | Invalid UUID GUC Guard (M-A)| Set GUC `app.current_tenant = 'malicious-non-uuid-string'` | PostgreSQL Cast Exception `::uuid` -> Abort transaction (DB REJECT) |

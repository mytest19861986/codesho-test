# P3-VS14 Boundary Plan, DDL & Proof Matrix (v1.5)

## Vertical Slice Identifier
- Task ID: `P3-VS14-STUDENT-LEARNING-OPERATIONS-AND-AI-ASSISTED-REFLECTION`
- Branch: `codex/phase3-product-platform-foundation`
- Authority: `COMMANDER_P3_VS14_DISCOVERY_UNLOCK`
- Fleet Standard GUC: `app.current_tenant`
- Session Protocol: `SET LOCAL "app.current_tenant" = %s` strictly inside `transaction.atomic()`

---

## 1. §2.1 Prerequisites & Upstream Dependencies
- P3-VS13 Certified:
  - `learning_calculationrun(tenant_id, id)`: Run registry exists with `FORCE RLS` and `NOBYPASSRLS`.
  - `learning_learningmilestone(tenant_id, id)`: Certified with unique active milestone index.
  - `learning_learninginsight(tenant_id, id)`: Certified with partial unique singleton index `uq_insight_singleton_active`.
  - All foreign keys enforce composite tenant scoping `(tenant_id, target_id)`.

---

## 2. Finite State Machines (FSM) & Transition Matrices

### 2.1 StudentLearningGoal FSM Matrix
| Initial State | Event / Trigger | Target State | Actor | Required Guard / Action |
|:---|:---|:---|:---|:---|
| `[INIT]` | Create Draft Goal | `DRAFT` | Student | Title, Domain valid |
| `DRAFT` | Activate Goal | `ACTIVE` | Student | Exactly 1 ACTIVE per domain; Global count <= 5; Acquired `pg_advisory_xact_lock` |
| `ACTIVE` | Complete Goal | `ACHIEVED` | Student / Mentor | `completed_at = clock_timestamp()`; Action plans completed |
| `ACTIVE` | Pause Goal | `PAUSED` | Student | Free active slot in domain |
| `PAUSED` | Resume Goal | `ACTIVE` | Student | Re-check domain active uniqueness & total <= 5 via Advisory Lock |
| `ACTIVE` | Supersede Goal | `SUPERSEDED` | Student | Superseded by newer refined goal in same domain |
| `DRAFT` / `ACTIVE` / `PAUSED` | Abandon / Archive | `ARCHIVED` | Student | Soft-archived, non-punitive |
| *Illegal* | Jump from Draft to Achieved | *REJECTED* | Any | Direct jump `DRAFT -> ACHIEVED` rejected by Service FSM Guard (`verify_goal_transition`) |

### 2.2 AIAssistedGrowthSuggestion FSM Matrix (Moderation Gated)
| Initial State | Event / Trigger | Target State | Actor | Required Guard / Action |
|:---|:---|:---|:---|:---|
| `[INIT]` | AI Generation Service | `PENDING` | System / Celery | `is_authoritative = FALSE`; `evidence_context <> '{}'::jsonb`; Zero PII; Invisible to Student |
| `PENDING` | Mentor Review & Approval | `PRESENTED` | Mentor / Staff | Mentor validates suggestion; Enforces partial unique 1 PRESENTED per type |
| `PRESENTED` | Student Accepts Suggestion | `ACCEPTED` | Student | Creates corresponding `GoalActionPlan` |
| `PRESENTED` | Student Dismisses Suggestion | `DISMISSED` | Student | Marked dismissed with audit log |
| `ACCEPTED` | Revoke / Withdraw | `WITHDRAWN` | Staff / Mentor | Withdrawn after acceptance if invalidated |
| `PENDING` / `PRESENTED` | Regenerate / Supersede | `SUPERSEDED` | System / Mentor | New calculation run supersedes older suggestion |
| `PENDING` / `PRESENTED` | Security / PII Revocation | `WITHDRAWN` | Staff / System | Withdrawn from visibility |

### 2.3 Actor & Authorization Matrix
| Entity / Action | Student (Own Data) | Student (Peer / Cross-Tenant) | Mentor (Assigned Cohort) | Admin / Owner |
|:---|:---|:---|:---|:---|
| `LearningReflection` (Create / Edit) | ALLOW | DENY (404/403) | DENY | DENY |
| `LearningReflection` (Read) | ALLOW | DENY | ALLOW (Scoped to cohort) | ALLOW (Tenant ops only) |
| `MentorReflectionFeedback` (Post / Edit) | DENY | DENY | ALLOW (Assigned student) | ALLOW |
| `StudentLearningGoal` (FSM Transitions) | ALLOW (Subject to FSM) | DENY | ALLOW (Formative guidance) | DENY |
| `AIAssistedGrowthSuggestion` (Trigger Gen) | DENY (Rate-limited service) | DENY | ALLOW (Mentor request) | ALLOW |
| `AIAssistedGrowthSuggestion` (Read PENDING) | DENY (Moderation Gate) | DENY | ALLOW | ALLOW |
| `AIAssistedGrowthSuggestion` (Read PRESENTED)| ALLOW | DENY | ALLOW | ALLOW |
| `ReflectionAuditLog` (Read / Append) | DENY (Forensic internal) | DENY | READ-ONLY (Audit trail) | READ-ONLY |

---

## 3. Detailed Negative Proof Matrix (N1 – N26)

| Test ID | Test Category | Target Condition | Expected Result & Verification Mechanism |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation GUC | Query `learning_learningreflection` without `SET LOCAL app.current_tenant` | Empty set / 0 rows (Fail-Closed) |
| **N2** | Tenant Isolation GUC | Query `learning_studentlearninggoal` with wrong tenant UUID | Empty set / 0 rows (Fail-Closed) |
| **N3** | Tenant Isolation GUC | Query `learning_aiassistedgrowthsuggestion` with empty string GUC | `NULLIF` evaluation returns NULL -> 0 rows |
| **N4** | Tenant Isolation GUC | Query `learning_mentorreflectionfeedback` with invalid UUID format | Catch cast error -> Safe 403 Forbidden / 0 rows |
| **N5** | Cross-Tenant Leakage | Insert `LearningReflection` with student belonging to Tenant B into Tenant A | Composite FK `(tenant_id, student_id)` violation -> DB REJECT |
| **N6** | Cross-Tenant Leakage | Insert `GoalActionPlan` pointing to `goal_id` of Tenant B | Composite FK `(tenant_id, goal_id)` violation -> DB REJECT |
| **N7** | B1 Invariant Proof | Delete parent milestone in `learning_learningmilestone` | `target_milestone_id` set to NULL; `tenant_id` remains intact & non-null (DB PASS) |
| **N8** | B1 Invariant Proof | Delete parent insight in `learning_learninginsight` | `source_insight_id` set to NULL; `tenant_id` remains intact & non-null (DB PASS) |
| **N9** | B1 Invariant Proof | Delete parent calculation run in `learning_calculationrun` | `generation_run_id` set to NULL; `tenant_id` remains intact & non-null (DB PASS) |
| **N10** | B3 Invariant Proof | Insert `ReflectionAuditLog` with multiple targets or 0 targets | Constraint `chk_audit_target_xor` violation -> DB REJECT |
| **N11** | B3 Invariant Proof | Insert `ReflectionAuditLog` pointing to `target_reflection_id` from Tenant B | Composite FK `(tenant_id, target_reflection_id)` violation -> DB REJECT |
| **N12** | B4 / SA-2 Proof | Delete `platform_tenant_tenant` (Tenant Wipe) | Deferrable target FKs cascade cleanly without ordering lockup (DB PASS) |
| **N13** | M1 Invariant Proof | Attempt `UPDATE` or `DELETE` on `learning_reflectionauditlog` by `app_role` | PostgreSQL `PERMISSION DENIED` -> Append-Only strictly enforced |
| **N14** | F1 / FSM Jump Proof| Transition `StudentLearningGoal` directly from `DRAFT` to `ACHIEVED` | Service FSM Guard `verify_goal_transition` rejects -> 400 Bad Request |
| **N15** | M2 Domain Uniqueness | Insert 2nd `ACTIVE` goal in same domain (`PYTHON_BASICS`) for same student | Partial unique index `uq_goal_student_domain_active` violation -> DB REJECT |
| **N16** | F3 Max 5 Goals Proof | Activate 6th goal concurrently across domains | Advisory lock + service counter rejects 6th active goal (400 Bad Request) |
| **N17** | F3 Concurrency Race | Fire 2 concurrent goal activations across domains simultaneously | `pg_advisory_xact_lock(tenant_id, student_id)` serializes; 2nd fails if count > 5 |
| **N18** | F2 Moderation Gate | Student queries `AIAssistedGrowthSuggestion` in `PENDING` state | Student API filters out `PENDING`; returns 0 items (Moderation Gate PASS) |
| **N19** | F2 Singleton Proof | Insert 2nd `PRESENTED` suggestion for same `suggestion_type` for student | Partial unique index `uq_suggestion_presented_singleton` violation -> DB REJECT |
| **N20** | M3 AI Advisory Proof | Update `is_authoritative = TRUE` on `learning_aiassistedgrowthsuggestion` | Constraint `chk_suggestion_advisory_invariant` violation -> DB REJECT |
| **N21** | D1 Differential Proof| Inject `{"name": "Alice", "email": "a@b.com"}` into `evidence_context` | Constraint `chk_suggestion_evidence_no_pii` (`?\|`) violation -> DB REJECT |
| **N22** | F5 / M3 PII Text | Submit reflection content containing phone number or national ID | Constraint `chk_reflection_no_pii` violation -> DB REJECT |
| **N23** | F4 Retraction Consistency | Set `is_retracted = TRUE` without providing `retraction_reason` or `retracted_at` | Constraint `chk_reflection_retraction_consistency` violation -> DB REJECT |
| **N24** | Idempotency Proof | Insert duplicate suggestion with identical `(tenant_id, idempotency_key)` | Unique constraint `uq_growthsuggestion_idempotency` violation -> DB REJECT |
| **N25** | Anti-Ranking Proof | Request student goals or reflection dashboard with peer ranking params | API rejects query params (`rank`, `percentile`, `leaderboard`) -> 400 Bad Request |
| **N26** | F2 Role Authorization | Student attempts to trigger AI suggestion generation endpoint | Role permission check rejects request -> 403 Forbidden |

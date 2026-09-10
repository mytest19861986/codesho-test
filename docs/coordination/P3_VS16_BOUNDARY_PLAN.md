# P3-VS16 Boundary Plan, DDL & Proof Matrix (v1.1-CANONICAL)

## Vertical Slice Identifier
- Task ID: `P3-VS16-MENTOR-STUDENT-SUCCESS-COACHING-AND-INTERVENTION-WORKFLOW`
- Branch: `codex/phase3-product-platform-foundation`
- Authority: `COMMANDER_P3_VS16_DISCOVERY_UNLOCK`
- Response-Record Identity: Addressed GLM v1.0 Audit Findings (B1–B5, M1–M6)
- Certified Commit: `c058eff`
- Fleet Standard GUC: `app.current_tenant`
- Session Protocol: `SET LOCAL "app.current_tenant" = %s` strictly inside `transaction.atomic()`

---

## 1. §2.1 Prerequisites & Upstream Dependencies
- P3-VS1 to P3-VS15 Certified:
  - `platform_tenant_tenant(id)`: Certified multi-tenant root.
  - `platform_tenant_tenantmembership(tenant_id, user_id)`: Certified composite tenant membership for student, mentor, and author scoping.
  - `learning_studentsuccessplan(tenant_id, id)`: Certified in P3-VS15 with active singleton (`uq_successplan_student_active`). Referenced by `fk_coachingsession_plan` and `fk_supportintervention_plan` via `ON DELETE SET NULL`.
  - `learning_learninginsight(tenant_id, id)`: Certified in P3-VS13 with partial unique singleton index. Referenced by `fk_coachingsession_insight` via `ON DELETE SET NULL`.
  - All foreign keys strictly enforce composite tenant scoping `(tenant_id, target_id)`. Exactly zero bare UUID foreign keys.

---

## 2. Finite State Machines (FSM) & Transition Matrices

### 2.1 CoachingSession FSM Matrix
| Initial State | Event / Trigger | Target State | Permitted Actors | Guard Conditions & Invariants | Side Effects / Audit Action |
|:---|:---|:---|:---|:---|:---|
| `[INIT]` | `SCHEDULE_SESSION` | `SCHEDULED` | Mentor, Student | Valid `scheduled_at > clock_timestamp()`; mentor assigned to student cohort | Inserts session; Emits `SCHEDULE_SESSION` audit log |
| `SCHEDULED` | `START_SESSION` | `IN_PROGRESS` | Mentor | Current time within grace window; mentor authenticated | Sets `started_at = clock_timestamp()`; Emits `START_SESSION` audit log |
| `SCHEDULED` | `RESCHEDULE_SESSION` | `SCHEDULED` | Mentor, Student | New `scheduled_at > clock_timestamp()`; reason non-punitive | Updates `scheduled_at`; Emits `RESCHEDULE_SESSION` audit log |
| `SCHEDULED` | `CANCEL_SESSION` | `CANCELLED` | Mentor, Student | Non-punitive cancellation; reason logged | Sets `cancelled_at`; Emits `CANCEL_SESSION` audit log |
| `IN_PROGRESS` | `COMPLETE_SESSION` | `COMPLETED` | Mentor | `completed_at = clock_timestamp()`; mandatory coaching summary present | Sets `completed_at`; Appends timeline progression |

### 2.2 SupportIntervention FSM Matrix (Learner Agency First)
| Initial State | Event / Trigger | Target State | Permitted Actors | Guard Conditions & Invariants | Side Effects / Audit Action |
|:---|:---|:---|:---|:---|:---|
| `[INIT]` | `PROPOSE_INTERVENTION` | `PROPOSED` | Mentor, Staff | Non-punitive supportive rationale; `is_authoritative = FALSE`; no disciplinary actions | Inserts intervention; Emits `PROPOSE_INTERVENTION` audit log |
| `PROPOSED` | `ACCEPT_INTERVENTION` | `ACCEPTED` | Student (Learner Agency) | Student explicitly acknowledges and adopts supportive measures | Sets `acknowledged_at = clock_timestamp()`; Emits `ACCEPT_INTERVENTION` |
| `PROPOSED` | `DECLINE_INTERVENTION`| `DECLINED` | Student (Learner Agency) | Non-punitive decline; zero academic penalty; optional feedback | Sets `declined_at = clock_timestamp()`; Emits `DECLINE_INTERVENTION` |
| `ACCEPTED` | `START_INTERVENTION` | `ACTIVE` | Mentor, Student | Intervention active; linked resources accessible | Sets `started_at = clock_timestamp()`; Emits `START_INTERVENTION` |
| `ACTIVE` | `COMPLETE_INTERVENTION`| `COMPLETED` | Mentor, Student | Formative review completed; success markers documented | Sets `completed_at = clock_timestamp()`; Emits `COMPLETE_INTERVENTION` |
| `ACTIVE` | `PAUSE_INTERVENTION` | `PAUSED` | Student, Mentor | Non-punitive pause requested by learner | Sets `paused_at = clock_timestamp()`; Emits `PAUSE_INTERVENTION` |
| `PAUSED` | `RESUME_INTERVENTION`| `ACTIVE` | Student, Mentor | Resumes active support; clears `paused_at` | Clears `paused_at`; Emits `RESUME_INTERVENTION` |

### 2.3 FollowUpAction FSM Matrix
| Initial State | Event / Trigger | Target State | Permitted Actors | Guard Conditions & Invariants | Side Effects / Audit Action |
|:---|:---|:---|:---|:---|:---|
| `[INIT]` | `ASSIGN_ACTION` | `PENDING` | Mentor, Student | Target due date valid; non-punitive task | Inserts action; Emits `ASSIGN_ACTION` audit log |
| `PENDING` | `START_ACTION` | `IN_PROGRESS` | Student | Action initiated | Updates status; Emits `START_ACTION` |
| `PENDING`, `IN_PROGRESS` | `COMPLETE_ACTION` | `COMPLETED` | Student, Mentor | `completed_at = clock_timestamp()` | Sets `completed_at`; Appends formative progress |
| `PENDING`, `IN_PROGRESS` | `SKIP_ACTION` | `SKIPPED` | Student | Non-punitive skip; agency preserved | Sets `skipped_at`; Emits `SKIP_ACTION` |

---

## 3. Actor & Authorization Matrix
| Entity / Action | Student (Self) | Student (Peer / Cross-Tenant) | Mentor (Assigned Cohort) | Mentor (Unassigned Cohort) | Admin / Owner |
|:---|:---|:---|:---|:---|:---|
| `CoachingSession` (Read/Join) | ALLOW | DENY (404/403) | ALLOW | DENY (403 Forbidden) | ALLOW |
| `CoachingSession` (Manage/Schedule) | ALLOW (Request) | DENY (404/403) | ALLOW | DENY (403 Forbidden) | ALLOW |
| `SupportIntervention` (Accept/Decline) | ALLOW (100% Agency) | DENY (404/403) | DENY (Cannot force) | DENY (403 Forbidden) | DENY |
| `SupportIntervention` (Propose) | DENY | DENY (404/403) | ALLOW | DENY (403 Forbidden) | ALLOW |
| `CoachingAuditLog` (Read) | DENY | DENY | DENY | DENY | ALLOW (Audit Only) |

---

## 4. Negative Proof Matrix (N1 – N28)

| Test ID | Test Category | Target Condition | Expected Result & Verification Mechanism |
|:---|:---|:---|:---|
| **N1** | Tenant Isolation GUC | Query `learning_coachingsession` without `SET LOCAL app.current_tenant` | Empty set / 0 rows (Fail-Closed) |
| **N2** | Tenant Isolation GUC | Query `learning_supportintervention` with wrong tenant UUID | Empty set / 0 rows (Fail-Closed) |
| **N3** | Cross-Tenant Mentor Linkage | Insert coaching session pointing to mentor from Tenant B | Composite FK violation -> DB REJECT |
| **N4** | Cross-Tenant Student Linkage| Insert coaching session pointing to student from Tenant B | Composite FK violation -> DB REJECT |
| **N5** | Cross-Tenant Plan Leakage | Insert intervention pointing to success plan from Tenant B | Composite FK violation -> DB REJECT |
| **N6** | Anti-Automated Decider | Create intervention marked `is_authoritative = TRUE` | Constraint `chk_intervention_non_authoritative` -> DB REJECT |
| **N7** | Anti-Punitive Rationale | Insert intervention with punitive category | Constraint `chk_intervention_category_supportive` -> DB REJECT |
| **N8** | Mandatory Agency Invariant | System or mentor attempts to force `ACCEPTED` state without student | Service FSM permission check -> 403 Forbidden / DB REJECT |
| **N9** | Append-Only Audit Log | Attempt `UPDATE` or `DELETE` on `learning_coachingauditlog` | Permission Denied / DB Revoke -> DB REJECT |
| **N10** | Append-Only Note Invariant | Attempt `UPDATE` or `DELETE` on finalized `learning_coachingnote` | Permission Denied / DB Revoke -> DB REJECT |
| **N11** | Deferrable FK Topology | Delete coaching session with child audit records | `ON DELETE NO ACTION DEFERRABLE` blocks purge -> DB REJECT |
| **N12** | Text Length Bounds | Insert coaching note exceeding 4000 characters | Constraint `chk_coachingnote_content_len` -> DB REJECT |
| **N13** | Headline Bounds | Insert intervention title < 3 or > 255 chars | Constraint `chk_intervention_title_len` -> DB REJECT |
| **N14** | PII Blacklist Regex | Insert coaching note or summary containing phone number or credit card | Constraint `chk_coachingnote_content_no_pii` -> DB REJECT |
| **N15** | PII Blacklist JSONB | Inject `{"national_id": "0012345678"}` into intervention metadata | Constraint `chk_intervention_metadata_no_pii` (`?\|`) -> DB REJECT |
| **N16** | PII Blacklist Audit Log | Inject `{"iban": "IR123456..."}` into coaching audit metadata | Constraint `chk_coachingaudit_metadata_no_pii` (`?\|`) -> DB REJECT |
| **N17** | FSM Illegal Direct Jump | Transition intervention from `PROPOSED` directly to `COMPLETED` | FSM Guard rejects invalid transition -> 400 Bad Request |
| **N18** | Completion Consistency | Set intervention `status='COMPLETED'` with `completed_at=NULL` | Constraint `chk_intervention_status_time_consistency` -> DB REJECT |
| **N19** | Anti-Ranking Policy | Query coaching sessions with `?rank=true` or leaderboard params | REST API returns 400 Bad Request (Anti-Ranking Policy) |
| **N20** | Cross-Cohort Mentor Guard | Mentor queries coaching session of student in unassigned cohort | Service permission check returns 403 Forbidden |
| **N21** | Concurrency Advisory Lock | Concurrent conflicting state updates on same intervention | `pg_advisory_xact_lock(hashtext('intervention' \|\| id::text))` -> PASS |
| **N22** | Session Time Consistency | `started_at > completed_at` in coaching session | Constraint `chk_coachingsession_status_time_consistency` -> DB REJECT |
| **N23** | Action Origin Exact XOR | Insert follow-up action with both intervention_id AND session_id set | Constraint `chk_followupaction_origin_exact_xor` -> DB REJECT |
| **N24** | Tenant Wipe Clean Cascade | Delete tenant entity via `platform_tenant_tenant` cascade | FK `ON DELETE CASCADE` cascades cleanly -> DB PASS |
| **N25** | Empty String GUC Fail-Closed| Query tables with `SET LOCAL app.current_tenant = ''` | Empty set / 0 rows (Fail-Closed) |
| **N26** | Malformed GUC String | Query tables with malicious string in `app.current_tenant` | Safe type cast error or fail-closed -> DB PASS |
| **N27** | Zero Bare UUIDs | Inspect all foreign keys across all 5 new tables | Zero foreign keys with single column UUID -> 100% PASS |
| **N28** | BiDi Isolation UI | Inspect frontend coaching dashboard elements | All mixed text wrapped in `<bdi dir="ltr">` -> UI PASS |

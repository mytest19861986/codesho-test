# P3-VS14 Boundary Plan & Write Manifest (v1.1)

## Vertical Slice Identifier
- Task ID: `P3-VS14-STUDENT-LEARNING-OPERATIONS-AND-AI-ASSISTED-REFLECTION`
- Branch: `codex/phase3-product-platform-foundation`

---

## 1. Domain & Architecture Boundaries

### 1.1 Tenant Session Protocol (Mandatory Invariant)
- All database queries and operations enforce:
  `SET LOCAL "app.current_tenant_id" = %s;` strictly inside an active `transaction.atomic()` block before any tenant entity read or write.

### 1.2 Core Entities & Complete Schema Definitions

1. **`LearningReflection`**:
   - `id`: UUID primary key
   - `tenant_id`: UUID (NOT NULL)
   - `student_id`: UUID (FK to `identity_user(id)`, NOT NULL)
   - `prompt_type`: VARCHAR(32) (Choices: `WEEKLY_REVIEW`, `MILESTONE_RETROSPECTIVE`, `OBSTACLE_ANALYSIS`, `FREE_REFLECTION`)
   - `content`: TEXT (NOT NULL, check constraint: `length(trim(content)) > 0`)
   - `mood_sentiment`: VARCHAR(32) (`GROWTH_MINDSET`, `CONFIDENT`, `CHALLENGED`, `CURIOUS`, `NEUTRAL`)
   - `is_retracted`: BOOLEAN (Default: False)
   - `retracted_at`: TIMESTAMPTZ (NULLable)
   - `created_at`: TIMESTAMPTZ (NOT NULL, auto_now_add=True)
   - `updated_at`: TIMESTAMPTZ (NOT NULL, auto_now=True)
   - Constraints:
     - Composite FK: `(tenant_id, student_id)`
     - CHECK `length(content) <= 10000`
     - CHECK `no_pii`: Regex check denying phone numbers, national IDs, email addresses in reflection content.

2. **`StudentLearningGoal`**:
   - `id`: UUID primary key
   - `tenant_id`: UUID (NOT NULL)
   - `student_id`: UUID (NOT NULL)
   - `title`: VARCHAR(255) (NOT NULL)
   - `domain`: VARCHAR(64) (NOT NULL, e.g., `PYTHON_BASICS`, `ALGORITHMS`, `WEB_DEV`)
   - `target_milestone_id`: UUID (NULLable, Composite FK to `LearningMilestone(tenant_id, id)`)
   - `status`: VARCHAR(32) (`DRAFT`, `ACTIVE`, `ACHIEVED`, `PAUSED`, `ARCHIVED`, `SUPERSEDED`)
   - `target_date`: DATE (NULLable)
   - `completed_at`: TIMESTAMPTZ (NULLable)
   - `created_at`: TIMESTAMPTZ (auto_now_add=True)
   - `updated_at`: TIMESTAMPTZ (auto_now=True)
   - Constraints & Cardinality:
     - Composite FK: `(tenant_id, student_id)`
     - Partial Unique Index: `UNIQUE (tenant_id, student_id, domain) WHERE (status = 'ACTIVE')` -> Exactly 1 ACTIVE goal per domain per student!
     - Global constraint: At most 5 concurrent `ACTIVE` goals per student across all domains.
     - Strict FSM transitions:
       - `DRAFT -> ACTIVE`
       - `ACTIVE -> ACHIEVED | PAUSED | ARCHIVED`
       - `PAUSED -> ACTIVE | ARCHIVED`
       - No direct jump from `DRAFT -> ACHIEVED`.

3. **`GoalActionPlan`**:
   - `id`: UUID primary key
   - `tenant_id`: UUID (NOT NULL)
   - `goal_id`: UUID (NOT NULL)
   - `step_order`: INTEGER (NOT NULL, >= 1)
   - `description`: VARCHAR(500) (NOT NULL)
   - `status`: VARCHAR(32) (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`)
   - `due_date`: DATE (NULLable)
   - `completed_at`: TIMESTAMPTZ (NULLable)
   - Constraints:
     - Composite FK: `FOREIGN KEY (tenant_id, goal_id) REFERENCES learning_studentlearninggoal(tenant_id, id) ON DELETE CASCADE`
     - Unique together: `(tenant_id, goal_id, step_order)`

4. **`AIAssistedGrowthSuggestion` (Non-Authoritative AI Invariant)**:
   - `id`: UUID primary key
   - `tenant_id`: UUID (NOT NULL)
   - `student_id`: UUID (NOT NULL)
   - `source_insight_id`: UUID (NULLable, Composite FK to `LearningInsight(tenant_id, id)`)
   - `suggestion_type`: VARCHAR(32) (`EXPLORATION`, `RECOVERY_STRATEGY`, `GOAL_STEP`)
   - `recommended_action`: VARCHAR(500) (NOT NULL)
   - `rationale`: TEXT (NOT NULL)
   - `evidence_context`: JSONB (NOT NULL, check constraint: `evidence_context <> '{}'::jsonb`)
   - `model_identifier`: VARCHAR(64) (NOT NULL, e.g., `gemini-1.5-pro`, `qwen-2.5-coder`)
   - `provenance_digest`: VARCHAR(64) (NOT NULL, SHA-256 hash of input context)
   - `idempotency_key`: VARCHAR(128) (NOT NULL, UNIQUE within tenant)
   - `status`: VARCHAR(32) (`PRESENTED`, `ACCEPTED`, `DISMISSED`, `WITHDRAWN`)
   - `is_authoritative`: BOOLEAN (DEFAULT FALSE, immutable CHECK constraint: `is_authoritative = FALSE`)
   - Invariant: AI never alters Goal/Milestone states directly. Requires explicit student acceptance or mentor confirmation.

5. **`MentorReflectionFeedback` (Distinct Educational Content)**:
   - `id`: UUID primary key
   - `tenant_id`: UUID (NOT NULL)
   - `reflection_id`: UUID (NOT NULL, Composite FK to `LearningReflection(tenant_id, id)`)
   - `mentor_id`: UUID (NOT NULL, Composite FK to `identity_user(id)`)
   - `feedback_text`: TEXT (NOT NULL, Zero PII, formative guidance only)
   - `is_retracted`: BOOLEAN (DEFAULT FALSE)
   - `created_at`: TIMESTAMPTZ (auto_now_add=True)
   - `updated_at`: TIMESTAMPTZ (auto_now=True)

6. **`ReflectionAuditLog` (Forensic Append-Only Trail)**:
   - `id`: UUID primary key
   - `tenant_id`: UUID (NOT NULL)
   - `actor_id`: UUID (NOT NULL)
   - `target_type`: VARCHAR(64) (e.g., `GOAL_TRANSITION`, `REFLECTION_ACCESS`, `FEEDBACK_POSTED`)
   - `target_id`: UUID (NOT NULL)
   - `action`: VARCHAR(64) (NOT NULL)
   - `metadata`: JSONB (DEFAULT '{}')
   - `created_at`: TIMESTAMPTZ (auto_now_add=True)
   - Invariant: `REVOKE UPDATE, DELETE ON learning_reflectionauditlog FROM app_role;`

---

## 2. PostgreSQL 17 RLS & DDL Matrix

- `FORCE ROW LEVEL SECURITY with NOBYPASSRLS` applied to all 6 tables.
- Zero bare UUID foreign keys.
- Composite primary/foreign keys enforce `(tenant_id, id)`.
- Advisory locking (`pg_advisory_xact_lock`) for concurrent goal transitions.

---

## 3. Write Manifest (Zero Wildcards)

### Backend:
- `backend/modules/learning/models.py` (Add 6 VS14 models)
- `backend/modules/learning/reflection_service.py` (Goal FSM & Non-authoritative AI service)
- `backend/modules/learning/serializers.py` (Serializers for reflection, goals, suggestions, feedback)
- `backend/modules/learning/views.py` (Endpoints: Reflection CRUD, Goal FSM transitions, AI suggestions, Mentor review)
- `backend/modules/learning/urls.py` (Register endpoints under `/api/v1/learning/operations/...`)
- `backend/modules/learning/migrations/0034_phase3_vs14_learning_operations.py` (Schema migration)
- `backend/modules/learning/migrations/0035_phase3_vs14_learning_operations_rls.py` (RLS migration)
- `backend/tests/test_p3_vs14_learning_operations.py` (N1-N35 tests)
- `docs/openapi.yaml` (Document 6 new endpoints)

### Frontend:
- `frontend/src/components/learning/ReflectionJournal.tsx`
- `frontend/src/components/learning/LearningGoalTracker.tsx`
- `frontend/src/components/learning/learning_ops.module.css`
- `frontend/src/app/dashboard/student/reflection/page.tsx`
- `frontend/src/app/dashboard/student/page.tsx`

### Coordination:
- `docs/coordination/CURRENT_TASK.md`
- `docs/coordination/P3_VS14_BOUNDARY_PLAN.md`

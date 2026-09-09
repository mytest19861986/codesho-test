# P3-VS14 Boundary Plan & Write Manifest

## Vertical Slice Identifier
- Task ID: `P3-VS14-STUDENT-LEARNING-OPERATIONS-AND-AI-ASSISTED-REFLECTION`
- Branch: `codex/phase3-product-platform-foundation`

---

## 1. Domain & Architecture Boundaries

### 1.1 Core Entities & Life Cycles
1. **`LearningReflection`**:
   - Fields: `id`, `tenant_id`, `student_id`, `prompt_type` (weekly_review, milestone_retrospective, obstacle_analysis, free_reflection), `content` (student qualitative input), `mood_sentiment` (growth_mindset, confident, challenged, curious), `mentor_feedback_status` (pending, reviewed, acknowledged), `created_at`, `updated_at`.
   - Immutable historical entries; student owns reflection, mentor may provide formative comment.

2. **`StudentLearningGoal`**:
   - Fields: `id`, `tenant_id`, `student_id`, `title`, `domain` (skill domain), `target_milestone_id` (optional composite FK to LearningMilestone), `status` (`DRAFT`, `ACTIVE`, `ACHIEVED`, `PAUSED`, `ABANDONED`), `target_date`, `completed_at`, `created_at`, `updated_at`.
   - Strict FSM transitions: `DRAFT -> ACTIVE -> ACHIEVED/PAUSED/ABANDONED`. No jumps from `DRAFT -> ACHIEVED`.

3. **`GoalActionPlan`**:
   - Fields: `id`, `tenant_id`, `goal_id` (composite FK), `step_order`, `description`, `status` (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `SKIPPED`), `due_date`, `completed_at`.

4. **`AIAssistedGrowthSuggestion`**:
   - Fields: `id`, `tenant_id`, `student_id`, `source_insight_id` (optional composite FK), `suggestion_type` (`EXPLORATION`, `RECOVERY_STRATEGY`, `GOAL_STEP`), `recommended_action`, `rationale`, `status` (`PRESENTED`, `ACCEPTED`, `DISMISSED`, `EXPIRED`), `is_authoritative=False` (enforced invariant: AI cannot alter student grade, milestone, or official record).

5. **`ReflectionAuditLog`**:
   - Append-only audit record of mentor reviews, goal state changes, and reflection visibility accesses.

---

## 2. Multi-Tenancy, Database & RLS Invariants

1. **PostgreSQL 17 FORCE RLS with NOBYPASSRLS**:
   - `ALTER TABLE learning_reflection ENABLE ROW LEVEL SECURITY;`
   - `ALTER TABLE learning_reflection FORCE ROW LEVEL SECURITY;`
   - Applied to all 5 new tables.
2. **Zero Bare UUIDs & Composite Foreign Keys**:
   - All relations enforce `FOREIGN KEY (tenant_id, foreign_id) REFERENCES parent_table(tenant_id, id) ON DELETE CASCADE`.
3. **Partial Unique Indexes**:
   - At most 5 concurrent `ACTIVE` goals per student to prevent cognitive overload.
4. **Zero-PII Storage**:
   - Prompt templates and suggestions must never ingest or persist sensitive demographic, parent financial, or biometric student data.

---

## 3. Child Safety & Anti-Ranking Policy
- **No Comparative Metrics**: Goals are strictly self-referential (`Self-Paced Formative Mastery`).
- **Zero Leaderboards & Percentiles**: AI assistant never produces sentences like "You are in top 10%" or "You are behind your peers".
- **Psychological Safety**: Non-punitive states (`PAUSED` instead of `FAILED`).

---

## 4. Write Manifest (Zero Wildcards)

### Backend:
- `backend/modules/learning/models.py` (Add 5 VS14 models)
- `backend/modules/learning/reflection_service.py` (New: Goal FSM & Reflection Service)
- `backend/modules/learning/serializers.py` (Add VS14 serializers)
- `backend/modules/learning/views.py` (Add reflection & goal views)
- `backend/modules/learning/urls.py` (Add endpoint routing)
- `backend/modules/learning/migrations/0034_phase3_vs14_learning_operations.py` (Schema migration)
- `backend/modules/learning/migrations/0035_phase3_vs14_learning_operations_rls.py` (RLS migration)
- `backend/tests/test_p3_vs14_learning_operations.py` (New test suite, N1-N30 matrix)
- `docs/openapi.yaml` (Document new endpoints)

### Frontend:
- `frontend/src/components/learning/ReflectionJournal.tsx` (New component)
- `frontend/src/components/learning/LearningGoalTracker.tsx` (New component)
- `frontend/src/components/learning/learning_ops.module.css` (Accessible BiDi CSS)
- `frontend/src/app/dashboard/student/reflection/page.tsx` (New route)
- `frontend/src/app/dashboard/student/page.tsx` (Integrate reflection & goal widgets)

### Coordination:
- `docs/coordination/CURRENT_TASK.md`

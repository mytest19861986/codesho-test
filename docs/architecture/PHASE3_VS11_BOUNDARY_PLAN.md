# Phase 3 Vertical Slice 11 Boundary Plan (P3-VS11) - Version 1.2

## 1. Context and Authority
- **Authority**: `COMMANDER_P3_VS11_DISCOVERY_DIRECTIVE` (Official Commander Directive Issued)
- **Task ID**: `P3-VS11-LEARNING-PERSONALIZATION-AND-ADAPTIVE-PROGRESSION-ENGINE`
- **Scope Title (Farsi)**: موتور شخصی‌سازی یادگیری، تحلیل مسیر رشد دانش‌آموز و سیستم پیشنهاد مسیر آموزشی تطبیقی
- **Status**: `DISCOVERY_ACTIVE / RUNTIME_LOCKED` (Strictly No Code Changes until Triple Fleet Approval & Commander Runtime Unlock)
- **Target Branch**: `codex/phase3-product-platform-foundation`
- **Working Tree**: `G:\project\codesho\codesho\worktrees\phase1-engineering-readiness`
- **Architecture Principle**:
  ```text
  Canonical Learning Events (Progress, Submission, Feedback, AssessmentResult, CourseCertificate)
          ↓
  Derived State (StudentSkillProgress & ProcessedLearningEvent Deduplication)
          ↓
  Materialized Projection (StudentLearningProfile)
          ↓
  Explainable Recommendation (LearningRecommendation with Evidence Reason & RecommendationTransitionLog)
          ↓
  Human / Role Controlled Action (Learner Accept/Dismiss/Complete, Mentor Guide)
  ```
- **Fundamental Invariants**:
  * **Runtime Locked**: Zero runtime code modification before triple fleet PASS (Qwen, GLM, Gemini) and Commander Runtime Unlock.
  * **Not an Autonomous Decision Maker**: This system does NOT make unilateral academic determinations; it creates an explainable analysis, recommendation, and progression guidance layer.
  * **Explainability First**: Every single recommendation MUST be backed by deterministic, verifiable learning evidence (`recommendation_reason`, `evidence_context <> '{}'::jsonb`). Zero black-box scores, zero opaque heuristics.
  * **Source of Truth Hierarchy (M2 Clarification & Qwen Invariant 1)**:
    ```text
    Canonical Learning Events (Progress, Submission, Feedback, AssessmentResult, CourseCertificate)
            >
    Derived State (StudentSkillProgress & ProcessedLearningEvent - strictly idempotent event processing)
            >
    Materialized Projection (StudentLearningProfile - 100% deterministically rebuildable)
            >
    Recommendation Artifacts (LearningRecommendation with RecommendationTransitionLog auditing)
    ```
  * **Zero PII**: Strictly synthetic student UUIDs, skill tokens, and pedagogical attributes. No sensitive personal profiling.
  * **Fail-Closed Multi-Tenancy & NOBYPASSRLS (M4 Requirement)**: PostgreSQL 17 `FORCE ROW LEVEL SECURITY` on all tenant-scoped tables with tenant isolation policy:
    ```sql
    CREATE POLICY p3_vs11_tenant_isolation ON <table>
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);
    ALTER TABLE <table> FORCE ROW LEVEL SECURITY;
    ```
  * **Tenant Session Protocol (SET LOCAL - M4 Requirement)**:
    `SET LOCAL app.current_tenant = %s` handled exclusively inside `transaction.atomic()`. Any out-of-transaction setting or non-UUID value fails closed immediately.
  * **Complete Composite Foreign Key Integrity (Zero Bare UUIDs - B2 Enforced)**: All relational columns (`tenant_id`, `student_id`, `skill_id`, `source_skill_id`, `target_skill_id`, `course_id`, `lesson_id`, `target_course_id`, `target_lesson_id`, `target_skill_id`) are strictly bound by DB-level Composite Foreign Keys `(tenant_id, target_id)`.
  * **DAG Invariant (Directed Acyclic Graph - B1 Enforced)**:
    Skill dependencies must form a strict DAG. Enforced at both Application Layer (`clean()`) AND Database Trigger level via PostgreSQL Recursive CTE with transactional advisory lock to prevent phantom-cycle race conditions.
  * **Strict Target Single-Choice XOR (B3 Enforced)**:
    Each recommendation must target exactly one learning artifact:
    `CHECK (num_nonnulls(target_course_id, target_lesson_id, target_skill_id) = 1)`.
  * **Active Target Policy (Qwen Invariant 5)**:
    Recommendations may only target active learning artifacts (`is_active=True` / published). Deactivation of an artifact immediately transitions pending recommendations targeting it to `SUPERSEDED`. New dependencies cannot target inactive skills.

---

## 2. Core Domain Architecture & Data Models (Zero Bare UUIDs & Complete DB CHECKs)

### 2.1 Prerequisite Unique Constraints Verification (From Previous Slices)
- `learning_course (tenant_id, id)`: Guaranteed by `UNIQUE (tenant_id, id)`
- `learning_lesson (tenant_id, id)`: Guaranteed by `UNIQUE (tenant_id, id)`
- `platform_tenant_tenantmembership (tenant_id, user_id)`: Guaranteed by `UNIQUE (tenant_id, user_id)`

### 2.2 `SkillDefinition` (تعریف مهارت و نقشه مفاهیم آموزشی)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `slug`: SlugField(max_length=64)  # e.g. "python-recursion", "loops-and-iterations"
- `title`: CharField(max_length=160)  # e.g. "توابع بازگشتی در پایتون"
- `description`: TextField(blank=True, default="")
- `category`: CharField(max_length=64, choices=[('ALGORITHMS', 'Algorithms'), ('SYNTAX', 'Syntax & Core'), ('DATA_STRUCTURES', 'Data Structures'), ('OOP', 'Object Oriented Programming'), ('PROBLEM_SOLVING', 'Problem Solving')])
- `difficulty_level`: PositiveSmallIntegerField(default=1)  # 1 to 5
- `is_active`: BooleanField(default=True)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- **Unique Constraints for Referencing**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, slug)`
- **DB Check Constraints (M1)**:
  * `CHECK (difficulty_level >= 1 AND difficulty_level <= 5)`
  * `CHECK (length(slug) >= 3)`
  * `CHECK (category IN ('ALGORITHMS', 'SYNTAX', 'DATA_STRUCTURES', 'OOP', 'PROBLEM_SOLVING'))`
- **Soft Deletion & Cascade Policy (m3 & Qwen Invariant 5)**:
  * Skills with historical student records are deactivated via `is_active=False` rather than hard deleted.
  * Trigger / Application validation forbids creating new dependencies or recommendations targeting inactive skills.

### 2.3 `SkillDependency` (وابستگی‌های سلسله‌مراتبی مهارت‌ها - DAG Enforcement)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `source_skill`: ForeignKey(`SkillDefinition`, on_delete=CASCADE, related_name="prerequisites")
- `target_skill`: ForeignKey(`SkillDefinition`, on_delete=CASCADE, related_name="dependents")
- `is_strict`: BooleanField(default=True)  # True = Hard prerequisite, False = Advisory / Recommended
- `created_at`: DateTimeField(auto_now_add=True)
- **Composite Foreign Keys (Zero Bare UUIDs)**:
  * `FOREIGN KEY (tenant_id, source_skill_id) REFERENCES learning_skilldefinition(tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, target_skill_id) REFERENCES learning_skilldefinition(tenant_id, id) ON DELETE CASCADE`
- **Unique Constraints**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, source_skill_id, target_skill_id)`
- **DB Check Constraints & Graph Invariants (B1 Resolution)**:
  * `CHECK (source_skill_id <> target_skill_id)` (Self-dependency strictly forbidden).
  * **Database Trigger & Recursive CTE Enforcement (B1 DDL)**:
    ```sql
    CREATE OR REPLACE FUNCTION learning_fn_skill_dag_guard()
    RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      -- Serialize edge mutations within tenant graph (Prevents phantom-cycle race):
      PERFORM pg_advisory_xact_lock(hashtextextended(NEW.tenant_id::text, 42));

      -- Qwen Invariant 5: Forbid linking to inactive skills
      IF EXISTS (
        SELECT 1 FROM learning_skilldefinition 
        WHERE tenant_id = NEW.tenant_id AND id IN (NEW.source_skill_id, NEW.target_skill_id) AND is_active = FALSE
      ) THEN
        RAISE EXCEPTION 'Dependency cannot be established on an inactive skill';
      END IF;

      IF EXISTS (
        WITH RECURSIVE walk AS (
          SELECT target_skill_id AS node
          FROM learning_skilldependency
          WHERE tenant_id = NEW.tenant_id
            AND source_skill_id = NEW.target_skill_id
            AND (TG_OP = 'INSERT' OR id <> NEW.id)
          UNION
          SELECT d.target_skill_id
          FROM learning_skilldependency d
          JOIN walk w ON d.tenant_id = NEW.tenant_id
                     AND d.source_skill_id = w.node
                     AND (TG_OP = 'INSERT' OR d.id <> NEW.id)
        )
        SELECT 1 FROM walk WHERE node = NEW.source_skill_id
      ) THEN
        RAISE EXCEPTION 'DAG invariant violated: % -> % creates a cyclic dependency',
          NEW.source_skill_id, NEW.target_skill_id;
      END IF;
      RETURN NEW;
    END $$;

    CREATE TRIGGER trg_skill_dag_guard
      BEFORE INSERT OR UPDATE OF source_skill_id, target_skill_id
      ON learning_skilldependency
      FOR EACH ROW EXECUTE FUNCTION learning_fn_skill_dag_guard();
    ```

### 2.4 `LessonSkillMapping` (نگاشت درس به مهارت‌های هدف)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `lesson`: ForeignKey(`learning.Lesson`, on_delete=CASCADE, related_name="skill_mappings")
- `skill`: ForeignKey(`SkillDefinition`, on_delete=CASCADE, related_name="lesson_mappings")
- `mastery_weight`: DecimalField(max_digits=4, decimal_places=2, default=1.00)
- **Composite Foreign Keys (Zero Bare UUIDs)**:
  * `FOREIGN KEY (tenant_id, lesson_id) REFERENCES learning_lesson(tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, skill_id) REFERENCES learning_skilldefinition(tenant_id, id) ON DELETE CASCADE`
- **Unique Constraints**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, lesson_id, skill_id)`
- **DB Check Constraints (M1)**:
  * `CHECK (mastery_weight > 0.00 AND mastery_weight <= 1.00)`

### 2.5 `ProcessedLearningEvent` (ثبت ایدمپوتنت رویدادهای پردازش‌شده آموزشی - Qwen Invariant 1)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `event_id`: UUIDField(db_index=True)  # Canonical event UUID (e.g. AssessmentResult.id or Progress.id)
- `event_type`: CharField(max_length=64)  # e.g. 'ASSESSMENT_EVALUATED', 'LESSON_COMPLETED'
- `student_id`: UUIDField(db_index=True)
- `processed_at`: DateTimeField(auto_now_add=True)
- **Composite Foreign Keys**:
  * `FOREIGN KEY (tenant_id, student_id) REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE`
- **Unique Constraints**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, event_id, event_type)`  # Guarantees strictly once processing (Zero duplicate practice_count increments)

### 2.6 `StudentSkillProgress` (وضعیت تسلط مهارتی دانش‌آموز - Derived State)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `student_id`: UUIDField(db_index=True)
- `skill`: ForeignKey(`SkillDefinition`, on_delete=CASCADE, related_name="student_progresses")
- `mastery_level`: CharField(max_length=16, choices=[
    ('NOT_STARTED', 'Not Started'),
    ('BEGINNER', 'Beginner'),
    ('DEVELOPING', 'Developing'),
    ('PROFICIENT', 'Proficient'),
    ('MASTERED', 'Mastered')
  ], default='NOT_STARTED')
- `mastery_score`: DecimalField(max_digits=5, decimal_places=2, default=0.00)  # 0.00 to 100.00
- `practice_count`: PositiveIntegerField(default=0)
- `last_evaluated_at`: DateTimeField()  # Set explicitly by evaluation service, not auto_now (m4)
- **Composite Foreign Keys (Zero Bare UUIDs)**:
  * `FOREIGN KEY (tenant_id, skill_id) REFERENCES learning_skilldefinition(tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, student_id) REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE`
- **Unique Constraints**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, student_id, skill_id)`
- **DB Check Constraints (M1)**:
  * `CHECK (mastery_score >= 0.00 AND mastery_score <= 100.00)`
  * `CHECK (mastery_level IN ('NOT_STARTED', 'BEGINNER', 'DEVELOPING', 'PROFICIENT', 'MASTERED'))`
- **Deterministic Mastery Progression & Monotonicity (Qwen Invariant 4)**:
  * Late-arriving events or duplicate webhooks CANNOT regress established mastery levels (`MASTERED` or `PROFICIENT`).
  * Explicit mathematical evaluation formula:
    - `BEGINNER -> DEVELOPING`: `completed_lesson_count >= 1 AND latest_valid_assessment_score >= 60.00`
    - `DEVELOPING -> PROFICIENT`: `all_core_mapped_lessons_completed = True AND weighted_assessment_score >= 75.00`
    - `PROFICIENT -> MASTERED`: `last_3_assessments_min_score >= 85.00 AND active_learning_gap_count = 0`
  * Atomic insertion/update with event check:
    ```sql
    -- Atomic evaluation using ProcessedLearningEvent guard:
    INSERT INTO learning_processedlearningevent (id, tenant_id, event_id, event_type, student_id, processed_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    ON CONFLICT (tenant_id, event_id, event_type) DO NOTHING;
    ```

### 2.7 `StudentLearningProfile` (پروجکشن تجمعی یادگیری دانش‌آموز - Rebuildable Materialized Projection)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `student_id`: UUIDField(db_index=True)
- `total_skills_tracked`: PositiveIntegerField(default=0)
- `mastered_skills_count`: PositiveIntegerField(default=0)
- `developing_skills_count`: PositiveIntegerField(default=0)
- `overall_competency_index`: DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Aggregate score 0-100
- `identified_learning_gaps`: JSONField(default=list)  # Serialized Evidence Snapshot: [{skill_id, skill_title, gap_reason, severity: 'LOW'|'MEDIUM'|'HIGH'}]
- `last_rebuilt_at`: DateTimeField()  # Explicitly set by Rebuild Service (m4)
- `rebuild_version`: PositiveIntegerField(default=1)
- **Source of Truth & Rebuild Invariant (Qwen Invariant 1)**:
  * Presentation projection only. 100% deterministically rebuildable from canonical tables and `StudentSkillProgress` via `rebuild_student_profile(tenant_id, student_id)`.
- **Composite Foreign Keys**:
  * `FOREIGN KEY (tenant_id, student_id) REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE`
- **Unique Constraints**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, student_id)`
- **DB Check Constraints (M1)**:
  * `CHECK (overall_competency_index >= 0.00 AND overall_competency_index <= 100.00)`
  * `CHECK (total_skills_tracked >= mastered_skills_count AND total_skills_tracked >= developing_skills_count)`

### 2.8 `LearningRecommendation` (پیشنهاد مسیر آموزشی تطبیقی و توضیح‌پذیر)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `student_id`: UUIDField(db_index=True)
- `target_course`: ForeignKey(`learning.Course`, on_delete=CASCADE, null=True, blank=True, related_name="recommendations")
- `target_lesson`: ForeignKey(`learning.Lesson`, on_delete=CASCADE, null=True, blank=True, related_name="recommendations")
- `target_skill`: ForeignKey(`SkillDefinition`, on_delete=CASCADE, null=True, blank=True, related_name="recommendations")
- `recommendation_type`: CharField(max_length=32, choices=[
    ('REMEDIAL_PRACTICE', 'Remedial Practice'),
    ('NEXT_CHALLENGE', 'Next Milestone Challenge'),
    ('SKILL_EXPANSION', 'Skill Expansion'),
    ('REVISION', 'Spaced Revision')
  ])
- `status`: CharField(max_length=16, choices=[
    ('GENERATED', 'Generated'),
    ('VIEWED', 'Viewed'),
    ('ACCEPTED', 'Accepted'),
    ('COMPLETED', 'Completed'),
    ('DISMISSED', 'Dismissed'),
    ('SUPERSEDED', 'Superseded')
  ], default='GENERATED')
- `priority`: PositiveSmallIntegerField(default=1)  # 1 (Highest) to 5 (Lowest)
- `recommendation_reason`: CharField(max_length=500)  # Farsi pedagogical explanation (>= 10 chars)
- `evidence_context`: JSONField(default=dict)  # Serialized Evidence Snapshot: {assessment_id: ..., score: ..., gap_skill_slug: ...}
- `idempotency_key`: CharField(max_length=255, db_index=True)
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)
- **Composite Foreign Keys (Zero Bare UUIDs - B2 Enforced)**:
  * `FOREIGN KEY (tenant_id, student_id) REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, target_course_id) REFERENCES learning_course(tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, target_lesson_id) REFERENCES learning_lesson(tenant_id, id) ON DELETE CASCADE`
  * `FOREIGN KEY (tenant_id, target_skill_id) REFERENCES learning_skilldefinition(tenant_id, id) ON DELETE CASCADE`
- **Unique Constraints**:
  * `UNIQUE (tenant_id, id)`
  * `UNIQUE (tenant_id, idempotency_key)`
- **DB Check Constraints (B3, M1, M3 Enforced)**:
  * `CHECK (priority >= 1 AND priority <= 5)`
  * `CHECK (length(recommendation_reason) >= 10)`
  * `CHECK (num_nonnulls(target_course_id, target_lesson_id, target_skill_id) = 1)`  -- (Strict XOR B3 Fixed!)
  * `CHECK (recommendation_type IN ('REMEDIAL_PRACTICE', 'NEXT_CHALLENGE', 'SKILL_EXPANSION', 'REVISION'))`
  * `CHECK (status IN ('GENERATED', 'VIEWED', 'ACCEPTED', 'COMPLETED', 'DISMISSED', 'SUPERSEDED'))`
  * `CHECK (evidence_context <> '{}'::jsonb)`  -- (M3 Explainability First enforced at DB level!)

### 2.9 `RecommendationTransitionLog` (حساب‌رسی تغییر وضعیت پیشنهادها - Qwen Invariant 3)
- `id`: UUID (PK)
- `tenant`: ForeignKey(`platform_tenant.Tenant`, on_delete=CASCADE)
- `recommendation`: ForeignKey(`LearningRecommendation`, on_delete=CASCADE, related_name="transition_logs")
- `from_status`: CharField(max_length=16)
- `to_status`: CharField(max_length=16)
- `actor_id`: UUIDField()  # Student user_id or System worker UUID
- `actor_type`: CharField(max_length=16, choices=[('STUDENT', 'Student'), ('SYSTEM', 'System Worker'), ('STAFF', 'Staff/Mentor')])
- `transition_reason`: CharField(max_length=255, blank=True, default="")
- `created_at`: DateTimeField(auto_now_add=True)
- **Composite Foreign Keys**:
  * `FOREIGN KEY (tenant_id, recommendation_id) REFERENCES learning_learningrecommendation(tenant_id, id) ON DELETE CASCADE`
- **Immutability Invariant**:
  * `REVOKE UPDATE, DELETE ON learning_recommendationtransitionlog FROM app_role;`
  * Guarantees complete non-repudiation audit trail of every recommendation life-cycle step.

---

## 3. State Machine & Event-Driven Progression Lifecycle (M5 & Qwen Invariant 2 Formalization)

### 3.1 `LearningRecommendation` Transition Matrix
| Current Status | Target Status | Permitted Actor | Trigger / Event | Note |
| :--- | :--- | :--- | :--- | :--- |
| `GENERATED` | `VIEWED` | Student | User opens dashboard card | Transient state |
| `GENERATED` | `ACCEPTED` | Student | User clicks "شروع تمرین" directly | Direct action |
| `GENERATED` | `DISMISSED` | Student | User dismisses recommendation | Terminal state |
| `GENERATED` | `SUPERSEDED` | System | Target deactivated OR new evidence replaces recommendation | Terminal state |
| `VIEWED` | `ACCEPTED` | Student | User clicks "شروع تمرین" | Active commitment |
| `VIEWED` | `DISMISSED` | Student | User dismisses recommendation | Terminal state |
| `VIEWED` | `SUPERSEDED` | System | Target deactivated OR newer assessment evidence replaces card | Terminal state |
| `ACCEPTED` | `COMPLETED` | System | Target Course/Lesson/Skill Completion criteria satisfied | **Terminal Closure (Qwen Invariant 2)** |
| `ACCEPTED` | `SUPERSEDED` | System | Target deactivated OR curriculum shift | Terminal override |

### 3.2 Target Skill Completion Definition (Qwen Invariant 2 Resolved)
When a recommendation targets a skill (`target_skill_id IS NOT NULL`), it transitions from `ACCEPTED` to `COMPLETED` when:
- The student achieves `mastery_level IN ('PROFICIENT', 'MASTERED')` on that specific skill, OR
- The student completes at least 2 recommended practice exercises mapped to that skill with score $\ge 70\%$.
- Handled automatically by the event-driven completion listener.

---

## 4. Indexing & Query Optimization
- `SkillDefinition`: Composite index on `(tenant_id, category, is_active)`
- `StudentSkillProgress`: Composite index on `(tenant_id, student_id, mastery_level)`
- `LearningRecommendation`: Composite index on `(tenant_id, student_id, status, priority)`
- `LessonSkillMapping`: Composite index on `(tenant_id, skill_id, mastery_weight)`
- `ProcessedLearningEvent`: Composite index on `(tenant_id, student_id, event_type)`
- `RecommendationTransitionLog`: Composite index on `(tenant_id, recommendation_id, created_at)`

---

## 5. Comprehensive Negative Isolation & Fail-Closed Test Matrix (N1-N33 - Expanded)
- `N1`: Cross-tenant query on `StudentLearningProfile` fails closed (404 / 0 rows).
- `N2`: Cross-tenant creation of `LearningRecommendation` violates Composite FK `(tenant_id, student_id)`.
- `N3`: Cyclic skill dependency (`Skill A -> Skill B -> Skill A`) rejected by PostgreSQL Trigger CTE (B1).
- `N4`: Self-dependency (`source_skill_id == target_skill_id`) rejected by DB CHECK.
- `N5`: Duplicate recommendation generation with same `idempotency_key` fails closed (UniqueConstraint).
- `N6`: Profile rebuild without valid `app.current_tenant` fails closed.
- `N7`: Recommendation with empty reason string rejected by DB CHECK (`length >= 10`).
- `N8`: Unauthorized student attempting to dismiss another student's recommendation denied with 403/404.
- `N9`: Recommendation targeting an inactive or non-existent course fails composite FK constraint.
- `N10`: Mastery score exceeding 100.00 rejected by DB CHECK.
- `N11`: Mastery score below 0.00 rejected by DB CHECK.
- `N12`: Corrupted projection rebuilds cleanly from canonical `Progress` and `AssessmentResult`.
- `N13`: Transition `DISMISSED -> ACCEPTED` rejected by FSM validator.
- `N14`: Transition `SUPERSEDED -> ACCEPTED` rejected by FSM validator.
- `N15`: Unenrolled student profile query returns empty uninitialized state without leakage.
- `N16`: Cross-tenant skill mapping insertion rejected by composite FK `(tenant_id, lesson_id, skill_id)`.
- `N17`: Concurrent progress update safely updates mastery level using atomic transactions (`INSERT ... ON CONFLICT DO UPDATE`).
- `N18`: GUC configuration attempt with empty string returns 0 rows via `NULLIF`.
- `N19`: Difficulty level out of bounds (`0` or `6`) rejected by DB CHECK.
- `N20`: Tenant deletion cleanly purges personalized projections and recommendation ledgers (CASCADE).
- `N21`: Session without `app.current_tenant` fails closed (0 rows / INSERT rejected - M6).
- `N22`: Non-UUID GUC value (`not-a-uuid`) raises fatal DB ERROR (fail-closed - M6).
- `N23`: Setting GUC outside `transaction.atomic()` rejected by session protocol (M4/M6).
- `N24`: Recommendation with cross-tenant `target_lesson_id` rejected by Composite FK (B2 Fixed).
- `N25`: `mastery_weight` outside valid range (`<= 0.00` or `> 1.00`) rejected by DB CHECK (M1).
- `N26`: `evidence_context = '{}'::jsonb` rejected by DB CHECK (M3 Explainability First).
- `N27`: Recommendation targeting multiple targets simultaneously (`course + skill`) rejected by `num_nonnulls = 1` (B3 Fixed).
- `N28`: Reprocessing duplicate learning event rejected by `ProcessedLearningEvent` unique constraint without inflating `practice_count` (Qwen Invariant 1).
- `N29`: `ACCEPTED` recommendation with `target_skill_id` transitions to `COMPLETED` upon achieving `PROFICIENT` level (Qwen Invariant 2).
- `N30`: State transition on `LearningRecommendation` automatically generates immutable audit log row in `RecommendationTransitionLog` (Qwen Invariant 3).
- `N31`: Late-arriving low assessment score cannot regress already established `MASTERED` state (Monotonic Mastery - Qwen Invariant 4).
- `N32`: Creating recommendation targeting inactive skill (`is_active=False`) rejected (Qwen Invariant 5).
- `N33`: Target artifact deactivation transitions active recommendations to `SUPERSEDED` (Qwen Invariant 5).

---

## 6. Frontend & Accessibility Requirements (Gemini Approved)
- **Guide, Don't Judge**: The UI must NEVER display demotivating labels like "ضعیف" (Weak) or "شکست‌خورده" (Failed). Use positive growth indicators like "مهارت‌های در حال شکوفایی" (Growing Skills) and "گام پیشنهادی بعدی" (Next Recommended Step).
- **Explainability Card UI**: Recommendation cards must clearly show *Why* this was recommended with an intuitive tag: "چرا این تمرین؟" (Why this practice?).
- **BiDi / RTL Isolation**: Skill slugs and code identifiers wrapped in `<bdi dir="ltr">`.
- **WCAG 2.2 AA Conformance**: High contrast (>4.5:1), touch targets $\ge 44\text{px}$, color-independent mastery badges.

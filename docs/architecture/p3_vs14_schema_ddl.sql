-- ============================================================================
-- P3-VS14: STUDENT LEARNING OPERATIONS, REFLECTION & AI-ASSISTED GROWTH
-- POSTGRESQL 17 DDL, FORCE RLS, NOBYPASSRLS & AUDIT DISCIPLINE SPECIFICATION
-- Version: v1.6-CANONICAL
-- Authority: COMMANDER_P3_VS14_DISCOVERY_UNLOCK
-- Fleet Standard GUC: app.current_tenant
-- Session Protocol: SET LOCAL "app.current_tenant" = %s strictly inside transaction.atomic()
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. LEARNING REFLECTION
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_learningreflection (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    prompt_type VARCHAR(32) NOT NULL,
    content TEXT NOT NULL,
    mood_sentiment VARCHAR(32) NOT NULL DEFAULT 'NEUTRAL',
    is_retracted BOOLEAN NOT NULL DEFAULT FALSE,
    retracted_at TIMESTAMPTZ NULL,
    retraction_reason VARCHAR(255) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_learningreflection PRIMARY KEY (id),
    CONSTRAINT uq_learning_learningreflection_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_learningreflection_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_learningreflection_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT chk_reflection_content_len CHECK (length(trim(content)) > 0 AND length(content) <= 10000),
    CONSTRAINT chk_reflection_prompt_type CHECK (prompt_type IN ('WEEKLY_REVIEW', 'MILESTONE_RETROSPECTIVE', 'OBSTACLE_ANALYSIS', 'FREE_REFLECTION')),
    CONSTRAINT chk_reflection_mood CHECK (mood_sentiment IN ('GROWTH_MINDSET', 'CONFIDENT', 'CHALLENGED', 'CURIOUS', 'NEUTRAL')),
    CONSTRAINT chk_reflection_retraction_consistency CHECK (
        (is_retracted = FALSE AND retracted_at IS NULL AND retraction_reason IS NULL) OR
        (is_retracted = TRUE AND retracted_at IS NOT NULL AND retraction_reason IS NOT NULL)
    ),
    CONSTRAINT chk_reflection_no_pii CHECK (
        content !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_reflection_tenant_student ON learning_learningreflection (tenant_id, student_id, created_at DESC);

-- ----------------------------------------------------------------------------
-- 2. STUDENT LEARNING GOAL
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_studentlearninggoal (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    domain VARCHAR(64) NOT NULL,
    target_milestone_id UUID NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    target_date DATE NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_studentlearninggoal PRIMARY KEY (id),
    CONSTRAINT uq_learning_studentlearninggoal_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_studentlearninggoal_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_studentlearninggoal_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_studentlearninggoal_milestone FOREIGN KEY (tenant_id, target_milestone_id)
        REFERENCES learning_learningmilestone(tenant_id, id) ON DELETE SET NULL (target_milestone_id),
    CONSTRAINT chk_goal_status CHECK (status IN ('DRAFT', 'ACTIVE', 'ACHIEVED', 'PAUSED', 'ARCHIVED', 'SUPERSEDED')),
    CONSTRAINT chk_goal_completion_consistency CHECK (
        (status = 'ACHIEVED' AND completed_at IS NOT NULL) OR
        (status <> 'ACHIEVED' AND completed_at IS NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_goal_student_domain_active 
ON learning_studentlearninggoal (tenant_id, student_id, domain) 
WHERE (status = 'ACTIVE');

CREATE INDEX IF NOT EXISTS idx_goal_tenant_student_status ON learning_studentlearninggoal (tenant_id, student_id, status);

-- ----------------------------------------------------------------------------
-- 3. GOAL ACTION PLAN
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_goalactionplan (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    goal_id UUID NOT NULL,
    step_order INTEGER NOT NULL,
    description VARCHAR(500) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    due_date DATE NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_goalactionplan PRIMARY KEY (id),
    CONSTRAINT uq_learning_goalactionplan_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_goalactionplan_goal FOREIGN KEY (tenant_id, goal_id)
        REFERENCES learning_studentlearninggoal(tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_goalactionplan_step UNIQUE (tenant_id, goal_id, step_order),
    CONSTRAINT chk_action_step_order CHECK (step_order >= 1),
    CONSTRAINT chk_action_status CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED')),
    CONSTRAINT chk_action_completed_consistency CHECK (
        (status = 'COMPLETED' AND completed_at IS NOT NULL) OR
        (status <> 'COMPLETED' AND completed_at IS NULL)
    )
);

-- ----------------------------------------------------------------------------
-- 4. AI-ASSISTED GROWTH SUGGESTION (Non-Authoritative & Moderation Gated)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_aiassistedgrowthsuggestion (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    source_insight_id UUID NULL,
    generation_run_id UUID NULL,
    suggestion_type VARCHAR(32) NOT NULL,
    recommended_action VARCHAR(500) NOT NULL,
    rationale TEXT NOT NULL,
    evidence_context JSONB NOT NULL,
    model_identifier VARCHAR(64) NOT NULL,
    provenance_digest VARCHAR(64) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    is_authoritative BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_aiassistedgrowthsuggestion PRIMARY KEY (id),
    CONSTRAINT uq_learning_aiassistedgrowthsuggestion_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_growthsuggestion_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_growthsuggestion_insight FOREIGN KEY (tenant_id, source_insight_id)
        REFERENCES learning_learninginsight(tenant_id, id) ON DELETE SET NULL (source_insight_id),
    CONSTRAINT fk_growthsuggestion_run FOREIGN KEY (tenant_id, generation_run_id)
        REFERENCES learning_calculationrun(tenant_id, id) ON DELETE SET NULL (generation_run_id),
    CONSTRAINT uq_growthsuggestion_idempotency UNIQUE (tenant_id, idempotency_key),
    CONSTRAINT chk_suggestion_status CHECK (status IN ('PENDING', 'PRESENTED', 'ACCEPTED', 'DISMISSED', 'WITHDRAWN', 'SUPERSEDED')),
    CONSTRAINT chk_suggestion_advisory_invariant CHECK (is_authoritative = FALSE),
    CONSTRAINT chk_suggestion_evidence_context CHECK (evidence_context <> '{}'::jsonb),
    CONSTRAINT chk_suggestion_rationale_len CHECK (length(trim(rationale)) >= 15),
    -- D1 Fix: Full union blacklist array on evidence_context
    CONSTRAINT chk_suggestion_evidence_no_pii CHECK (
        jsonb_typeof(evidence_context) = 'object'
        AND NOT (evidence_context ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
        ])
    ),
    CONSTRAINT chk_suggestion_provenance_digest CHECK (provenance_digest ~ '^[0-9a-f]{64}$'),
    CONSTRAINT chk_suggestion_no_pii CHECK (
        recommended_action !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
        AND
        rationale !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_suggestion_presented_singleton
ON learning_aiassistedgrowthsuggestion (tenant_id, student_id, suggestion_type)
WHERE (status = 'PRESENTED');

CREATE INDEX IF NOT EXISTS idx_suggestion_student_status ON learning_aiassistedgrowthsuggestion (tenant_id, student_id, status);

-- ----------------------------------------------------------------------------
-- 5. MENTOR REFLECTION FEEDBACK (Interactive Educational Content)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_mentorreflectionfeedback (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    reflection_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    feedback_text TEXT NOT NULL,
    is_retracted BOOLEAN NOT NULL DEFAULT FALSE,
    retracted_at TIMESTAMPTZ NULL,
    retraction_reason VARCHAR(255) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_mentorreflectionfeedback PRIMARY KEY (id),
    CONSTRAINT uq_learning_mentorreflectionfeedback_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_feedback_reflection FOREIGN KEY (tenant_id, reflection_id)
        REFERENCES learning_learningreflection(tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_mentor FOREIGN KEY (tenant_id, mentor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_feedback_content CHECK (length(trim(feedback_text)) > 0 AND length(feedback_text) <= 5000),
    CONSTRAINT chk_feedback_retraction_consistency CHECK (
        (is_retracted = FALSE AND retracted_at IS NULL AND retraction_reason IS NULL) OR
        (is_retracted = TRUE AND retracted_at IS NOT NULL AND retraction_reason IS NOT NULL)
    ),
    CONSTRAINT chk_feedback_no_pii CHECK (
        feedback_text !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

-- ----------------------------------------------------------------------------
-- 6. REFLECTION AUDIT LOG (Forensic Append-Only Trail - SA-2 & F3 Fix)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_reflectionauditlog (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    target_reflection_id UUID NULL,
    target_goal_id UUID NULL,
    target_feedback_id UUID NULL,
    target_suggestion_id UUID NULL,
    action VARCHAR(64) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_reflectionauditlog PRIMARY KEY (id),
    CONSTRAINT uq_learning_reflectionauditlog_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_auditlog_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_auditlog_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE RESTRICT,
    -- SA-2 Fix: DEFERRABLE INITIALLY DEFERRED eliminates tenant wipe cascade ordering sensitivity
    CONSTRAINT fk_auditlog_target_reflection FOREIGN KEY (tenant_id, target_reflection_id)
        REFERENCES learning_learningreflection(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_auditlog_target_goal FOREIGN KEY (tenant_id, target_goal_id)
        REFERENCES learning_studentlearninggoal(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_auditlog_target_feedback FOREIGN KEY (tenant_id, target_feedback_id)
        REFERENCES learning_mentorreflectionfeedback(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_auditlog_target_suggestion FOREIGN KEY (tenant_id, target_suggestion_id)
        REFERENCES learning_aiassistedgrowthsuggestion(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_audit_target_xor CHECK (
        num_nonnulls(target_reflection_id, target_goal_id, target_feedback_id, target_suggestion_id) = 1
    ),
    -- F3 Fix: Synchronize audit action enum with FSM transitions
    CONSTRAINT chk_audit_action CHECK (
        action IN (
            'CREATE_REFLECTION', 'RETRACT_REFLECTION', 'RESTORE_REFLECTION',
            'CREATE_GOAL', 'TRANSITION_GOAL_STATUS',
            'CREATE_ACTION_PLAN', 'UPDATE_ACTION_PLAN',
            'GENERATE_AI_SUGGESTION', 'MODERATE_AI_SUGGESTION',
            'ACCEPT_AI_SUGGESTION', 'DISMISS_AI_SUGGESTION',
            'SUPERSEDE_AI_SUGGESTION', 'WITHDRAW_AI_SUGGESTION',
            'POST_MENTOR_FEEDBACK', 'RETRACT_MENTOR_FEEDBACK'
        )
    ),
    -- D1 Fix: Full union blacklist array on metadata
    CONSTRAINT chk_audit_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant_actor_time ON learning_reflectionauditlog (tenant_id, actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_refl ON learning_reflectionauditlog (tenant_id, target_reflection_id) WHERE target_reflection_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_tenant_goal ON learning_reflectionauditlog (tenant_id, target_goal_id) WHERE target_goal_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_tenant_feedback ON learning_reflectionauditlog (tenant_id, target_feedback_id) WHERE target_feedback_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_tenant_sugg ON learning_reflectionauditlog (tenant_id, target_suggestion_id) WHERE target_suggestion_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 7. POSTGRESQL 17 FORCE RLS & NOBYPASSRLS MATRIX
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_learningreflection',
        'learning_studentlearninggoal',
        'learning_goalactionplan',
        'learning_aiassistedgrowthsuggestion',
        'learning_mentorreflectionfeedback',
        'learning_reflectionauditlog'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);

        EXECUTE format('DROP POLICY IF EXISTS p3_vs14_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p3_vs14_tenant_isolation_policy ON %I
             FOR ALL
             USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid)
             WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

REVOKE UPDATE, DELETE ON learning_reflectionauditlog FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_reflectionauditlog FROM app_role;

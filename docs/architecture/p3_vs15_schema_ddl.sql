-- ============================================================================
-- P3-VS15: LEARNING CONTINUITY & STUDENT SUCCESS PLANNING
-- POSTGRESQL 17 DDL, FORCE RLS, NOBYPASSRLS & AUDIT DISCIPLINE SPECIFICATION
-- Version: v1.1-CANONICAL
-- Authority: COMMANDER_P3_VS15_DISCOVERY_UNLOCK
-- Response-Record Identity: Addressed GLM v1.0 Audit (B1, M1-M6, m1-m5)
-- Fleet Standard GUC: app.current_tenant
-- Session Protocol: SET LOCAL "app.current_tenant" = %s strictly inside transaction.atomic()
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. STUDENT SUCCESS PLAN
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_studentsuccessplan (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    target_period VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    notes TEXT NULL,
    completed_at TIMESTAMPTZ NULL,
    paused_at TIMESTAMPTZ NULL,
    archived_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_studentsuccessplan PRIMARY KEY (id),
    CONSTRAINT uq_learning_studentsuccessplan_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_studentsuccessplan_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_studentsuccessplan_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT chk_successplan_title_len CHECK (length(trim(title)) >= 3 AND length(title) <= 255),
    CONSTRAINT chk_successplan_status CHECK (status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'SUPERSEDED', 'ARCHIVED')),
    CONSTRAINT chk_successplan_status_consistency CHECK (
        (status = 'ACTIVE' AND completed_at IS NULL AND paused_at IS NULL AND archived_at IS NULL) OR
        (status = 'PAUSED' AND paused_at IS NOT NULL AND completed_at IS NULL) OR
        (status = 'COMPLETED' AND completed_at IS NOT NULL) OR
        (status = 'SUPERSEDED') OR
        (status = 'ARCHIVED' AND archived_at IS NOT NULL)
    ),
    -- M5 Fix: Strict length bounds and 13-key regex PII filter on notes
    CONSTRAINT chk_successplan_notes_len CHECK (notes IS NULL OR length(notes) <= 4000),
    CONSTRAINT chk_successplan_notes_no_pii CHECK (
        notes IS NULL OR
        notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

-- Invariant: Exactly 1 ACTIVE SuccessPlan per student per tenant (Active Singleton)
CREATE UNIQUE INDEX IF NOT EXISTS uq_successplan_student_active
    ON learning_studentsuccessplan (tenant_id, student_id)
    WHERE status = 'ACTIVE';

CREATE INDEX IF NOT EXISTS idx_successplan_tenant_student_time
    ON learning_studentsuccessplan (tenant_id, student_id, created_at DESC);

-- ----------------------------------------------------------------------------
-- 2. SUCCESS ACTION STEP
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_successactionstep (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    sequence_order INT NOT NULL DEFAULT 1,
    is_authoritative BOOLEAN NOT NULL DEFAULT FALSE,
    target_date DATE NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_successactionstep PRIMARY KEY (id),
    CONSTRAINT uq_learning_successactionstep_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_successactionstep_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_successactionstep_plan FOREIGN KEY (tenant_id, plan_id)
        REFERENCES learning_studentsuccessplan(tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_actionstep_title_len CHECK (length(trim(title)) >= 3 AND length(title) <= 255),
    CONSTRAINT chk_actionstep_status CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED')),
    -- M6 Fix: sequence_order must be positive and unique per plan
    CONSTRAINT chk_actionstep_seq_positive CHECK (sequence_order >= 1),
    CONSTRAINT uq_actionstep_tenant_plan_seq UNIQUE (tenant_id, plan_id, sequence_order),
    -- Non-automated decision boundary invariant: Systems/agents can never issue authoritative mandates
    CONSTRAINT chk_step_non_authoritative CHECK (is_authoritative = FALSE),
    CONSTRAINT chk_step_completion_consistency CHECK (
        (status = 'COMPLETED' AND completed_at IS NOT NULL) OR
        (status <> 'COMPLETED' AND completed_at IS NULL)
    ),
    -- M5 Fix: Strict length bounds and regex PII filter on description
    CONSTRAINT chk_actionstep_desc_len CHECK (description IS NULL OR length(description) <= 4000),
    CONSTRAINT chk_actionstep_no_pii CHECK (
        description IS NULL OR
        description !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_actionstep_tenant_plan_seq
    ON learning_successactionstep (tenant_id, plan_id, sequence_order ASC);

-- ----------------------------------------------------------------------------
-- 3. SUCCESS TIMELINE EVENT (Append-Only Continuity Trail)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_successtimelineevent (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    headline VARCHAR(255) NOT NULL,
    detail TEXT NULL,
    target_goal_id UUID NULL,
    target_insight_id UUID NULL,
    target_reflection_id UUID NULL,
    target_action_step_id UUID NULL,
    target_milestone_id UUID NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_successtimelineevent PRIMARY KEY (id),
    CONSTRAINT uq_learning_successtimelineevent_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_timelineevent_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    -- M4 Fix: ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED prevents silent timeline purge
    CONSTRAINT fk_timelineevent_plan FOREIGN KEY (tenant_id, plan_id)
        REFERENCES learning_studentsuccessplan(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_timelineevent_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE RESTRICT,
    -- SA-2 Fix: DEFERRABLE INITIALLY DEFERRED eliminates tenant wipe cascade ordering deadlocks
    CONSTRAINT fk_timelineevent_target_goal FOREIGN KEY (tenant_id, target_goal_id)
        REFERENCES learning_studentlearninggoal(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_timelineevent_target_insight FOREIGN KEY (tenant_id, target_insight_id)
        REFERENCES learning_learninginsight(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_timelineevent_target_reflection FOREIGN KEY (tenant_id, target_reflection_id)
        REFERENCES learning_learningreflection(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_timelineevent_target_action FOREIGN KEY (tenant_id, target_action_step_id)
        REFERENCES learning_successactionstep(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    -- M2 Fix: target_milestone_id connected to learning_successactionstep with DEFERRABLE FK
    CONSTRAINT fk_timelineevent_target_milestone FOREIGN KEY (tenant_id, target_milestone_id)
        REFERENCES learning_successactionstep(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    -- M2 Fix: 5-way XOR Continuity Invariant: Exactly one target entity must be linked
    CONSTRAINT chk_timeline_target_xor CHECK (
        num_nonnulls(target_goal_id, target_insight_id, target_reflection_id, target_action_step_id, target_milestone_id) = 1
    ),
    CONSTRAINT chk_timeline_event_type CHECK (
        event_type IN (
            'GOAL_ANCHORED',
            'INSIGHT_CONNECTED',
            'REFLECTION_TIED',
            'ACTION_DISPATCHED',
            'MILESTONE_PROGRESSION'
        )
    ),
    -- M3 Fix: Exact 1-to-1 coupling between event_type and linked target
    CONSTRAINT chk_timeline_type_target_coupling CHECK (
        (event_type = 'GOAL_ANCHORED' AND target_goal_id IS NOT NULL) OR
        (event_type = 'INSIGHT_CONNECTED' AND target_insight_id IS NOT NULL) OR
        (event_type = 'REFLECTION_TIED' AND target_reflection_id IS NOT NULL) OR
        (event_type = 'ACTION_DISPATCHED' AND target_action_step_id IS NOT NULL) OR
        (event_type = 'MILESTONE_PROGRESSION' AND target_milestone_id IS NOT NULL)
    ),
    -- M5 Fix: Headline length bounds and regex PII scrubber
    CONSTRAINT chk_timeline_headline_len CHECK (length(trim(headline)) >= 3 AND length(headline) <= 255),
    CONSTRAINT chk_timeline_headline_no_pii CHECK (
        headline !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    -- M5 Fix: Detail length bounds and regex PII scrubber
    CONSTRAINT chk_timeline_detail_len CHECK (detail IS NULL OR length(detail) <= 4000),
    CONSTRAINT chk_timeline_detail_no_pii CHECK (
        detail IS NULL OR
        detail !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    -- D1 Fix: Full union blacklist array on metadata JSONB
    CONSTRAINT chk_timeline_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_timeline_tenant_plan_time
    ON learning_successtimelineevent (tenant_id, plan_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_timeline_tenant_goal
    ON learning_successtimelineevent (tenant_id, target_goal_id) WHERE target_goal_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_timeline_tenant_insight
    ON learning_successtimelineevent (tenant_id, target_insight_id) WHERE target_insight_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_timeline_tenant_reflection
    ON learning_successtimelineevent (tenant_id, target_reflection_id) WHERE target_reflection_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_timeline_tenant_action
    ON learning_successtimelineevent (tenant_id, target_action_step_id) WHERE target_action_step_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_timeline_tenant_milestone
    ON learning_successtimelineevent (tenant_id, target_milestone_id) WHERE target_milestone_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 4. SUCCESS AUDIT LOG
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_successauditlog (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    target_plan_id UUID NULL,
    target_action_step_id UUID NULL,
    target_timeline_event_id UUID NULL,
    action VARCHAR(64) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_successauditlog PRIMARY KEY (id),
    CONSTRAINT uq_learning_successauditlog_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_successaudit_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_successaudit_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_successaudit_target_plan FOREIGN KEY (tenant_id, target_plan_id)
        REFERENCES learning_studentsuccessplan(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_successaudit_target_action FOREIGN KEY (tenant_id, target_action_step_id)
        REFERENCES learning_successactionstep(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_successaudit_target_timeline FOREIGN KEY (tenant_id, target_timeline_event_id)
        REFERENCES learning_successtimelineevent(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_successaudit_target_xor CHECK (
        num_nonnulls(target_plan_id, target_action_step_id, target_timeline_event_id) = 1
    ),
    CONSTRAINT chk_successaudit_action CHECK (
        action IN (
            'CREATE_SUCCESS_PLAN', 'PAUSE_SUCCESS_PLAN', 'RESUME_SUCCESS_PLAN',
            'COMPLETE_SUCCESS_PLAN', 'SUPERSEDE_SUCCESS_PLAN', 'ARCHIVE_SUCCESS_PLAN',
            'CREATE_ACTION_STEP', 'UPDATE_ACTION_STEP', 'TRANSITION_ACTION_STEP',
            'APPEND_TIMELINE_EVENT'
        )
    ),
    CONSTRAINT chk_successaudit_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_successaudit_tenant_actor_time
    ON learning_successauditlog (tenant_id, actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_successaudit_tenant_plan
    ON learning_successauditlog (tenant_id, target_plan_id) WHERE target_plan_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_successaudit_tenant_action
    ON learning_successauditlog (tenant_id, target_action_step_id) WHERE target_action_step_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_successaudit_tenant_timeline
    ON learning_successauditlog (tenant_id, target_timeline_event_id) WHERE target_timeline_event_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 5. POSTGRESQL 17 FORCE RLS & NOBYPASSRLS ENFORCEMENT
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_studentsuccessplan',
        'learning_successactionstep',
        'learning_successtimelineevent',
        'learning_successauditlog'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);

        EXECUTE format('DROP POLICY IF EXISTS p3_vs15_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p3_vs15_tenant_isolation_policy ON %I
             FOR ALL
             USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid)
             WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Enforce Append-Only Discipline on Timeline Events and Audit Log
REVOKE UPDATE, DELETE ON learning_successtimelineevent FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_successtimelineevent FROM app_role;
REVOKE UPDATE, DELETE ON learning_successauditlog FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_successauditlog FROM app_role;

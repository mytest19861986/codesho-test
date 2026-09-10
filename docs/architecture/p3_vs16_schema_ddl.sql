-- ============================================================================
-- P3-VS16: MENTOR-STUDENT SUCCESS COACHING & INTERVENTION WORKFLOW
-- POSTGRESQL 17 DDL, FORCE RLS, NOBYPASSRLS & AUDIT DISCIPLINE SPECIFICATION
-- Version: v1.1-CANONICAL
-- Authority: COMMANDER_P3_VS16_DISCOVERY_UNLOCK
-- Response-Record Identity: Addressed GLM v1.0 Audit (B1-B5, M1-M6)
-- Fleet Standard GUC: app.current_tenant
-- Session Protocol: SET LOCAL "app.current_tenant" = %s strictly inside transaction.atomic()
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. COACHING SESSION
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_coachingsession (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    success_plan_id UUID NULL,
    learning_insight_id UUID NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    cancelled_at TIMESTAMPTZ NULL,
    cancellation_reason VARCHAR(1000) NULL,
    summary TEXT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_coachingsession PRIMARY KEY (id),
    CONSTRAINT uq_learning_coachingsession_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_coachingsession_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_coachingsession_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_coachingsession_mentor FOREIGN KEY (tenant_id, mentor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_coachingsession_plan FOREIGN KEY (tenant_id, success_plan_id)
        REFERENCES learning_studentsuccessplan(tenant_id, id) ON DELETE SET NULL (success_plan_id),
    CONSTRAINT fk_coachingsession_insight FOREIGN KEY (tenant_id, learning_insight_id)
        REFERENCES learning_learninginsight(tenant_id, id) ON DELETE SET NULL (learning_insight_id),
    CONSTRAINT chk_coachingsession_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_coachingsession_status CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_coachingsession_status_time_consistency CHECK (
        (status = 'SCHEDULED' AND started_at IS NULL AND completed_at IS NULL AND cancelled_at IS NULL AND cancellation_reason IS NULL) OR
        (status = 'IN_PROGRESS' AND started_at IS NOT NULL AND completed_at IS NULL AND cancelled_at IS NULL) OR
        (status = 'COMPLETED' AND started_at IS NOT NULL AND completed_at IS NOT NULL AND started_at <= completed_at AND cancelled_at IS NULL) OR
        (status = 'CANCELLED' AND cancelled_at IS NOT NULL AND cancellation_reason IS NOT NULL AND completed_at IS NULL)
    ),
    CONSTRAINT chk_coachingsession_summary_len CHECK (summary IS NULL OR (char_length(trim(summary)) >= 5 AND char_length(summary) <= 4000)),
    CONSTRAINT chk_coachingsession_summary_no_pii CHECK (
        summary IS NULL OR
        summary !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_coachingsession_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_coachingsession_tenant_student_time
    ON learning_coachingsession (tenant_id, student_id, scheduled_at DESC);
CREATE INDEX IF NOT EXISTS idx_coachingsession_tenant_mentor_time
    ON learning_coachingsession (tenant_id, mentor_id, scheduled_at DESC);

-- ----------------------------------------------------------------------------
-- 2. COACHING NOTE (Immutable / Append-Only Once Finalized)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_coachingnote (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    session_id UUID NOT NULL,
    author_id UUID NOT NULL,
    note_type VARCHAR(32) NOT NULL DEFAULT 'OBSERVATION',
    content TEXT NOT NULL,
    is_shared_with_student BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_coachingnote PRIMARY KEY (id),
    CONSTRAINT uq_learning_coachingnote_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_coachingnote_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_coachingnote_session FOREIGN KEY (tenant_id, session_id)
        REFERENCES learning_coachingsession(tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_coachingnote_author FOREIGN KEY (tenant_id, author_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT chk_coachingnote_type CHECK (note_type IN ('OBSERVATION', 'STRENGTH', 'GROWTH_OPPORTUNITY', 'ACTION_ITEM', 'SUMMARY')),
    CONSTRAINT chk_coachingnote_content_len CHECK (char_length(trim(content)) >= 3 AND char_length(content) <= 4000),
    CONSTRAINT chk_coachingnote_content_no_pii CHECK (
        content !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_coachingnote_tenant_session_time
    ON learning_coachingnote (tenant_id, session_id, created_at ASC);

-- ----------------------------------------------------------------------------
-- 3. SUPPORT INTERVENTION (Learner Agency First)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_supportintervention (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    student_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    success_plan_id UUID NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL DEFAULT 'ACADEMIC_SCAFFOLDING',
    status VARCHAR(32) NOT NULL DEFAULT 'PROPOSED',
    is_authoritative BOOLEAN NOT NULL DEFAULT FALSE,
    rationale TEXT NOT NULL,
    student_feedback TEXT NULL,
    proposed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    acknowledged_at TIMESTAMPTZ NULL,
    declined_at TIMESTAMPTZ NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    paused_at TIMESTAMPTZ NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_supportintervention PRIMARY KEY (id),
    CONSTRAINT uq_learning_supportintervention_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_supportintervention_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_supportintervention_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_supportintervention_mentor FOREIGN KEY (tenant_id, mentor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_supportintervention_plan FOREIGN KEY (tenant_id, success_plan_id)
        REFERENCES learning_studentsuccessplan(tenant_id, id) ON DELETE SET NULL (success_plan_id),
    CONSTRAINT chk_intervention_status CHECK (status IN ('PROPOSED', 'ACCEPTED', 'DECLINED', 'ACTIVE', 'PAUSED', 'COMPLETED')),
    CONSTRAINT chk_intervention_category_supportive CHECK (category IN (
        'ACADEMIC_SCAFFOLDING', 'RESOURCE_RECOMMENDATION', 'STUDY_STRATEGY', 'PACING_ADJUSTMENT', 'PEER_STUDY_CONNECTION'
    )),
    CONSTRAINT chk_intervention_non_authoritative CHECK (is_authoritative = FALSE),
    CONSTRAINT chk_intervention_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_intervention_rationale_len CHECK (char_length(trim(rationale)) >= 10 AND char_length(rationale) <= 4000),
    CONSTRAINT chk_intervention_feedback_len CHECK (student_feedback IS NULL OR (char_length(trim(student_feedback)) >= 2 AND char_length(student_feedback) <= 2000)),
    CONSTRAINT chk_intervention_status_time_consistency CHECK (
        (status = 'PROPOSED' AND acknowledged_at IS NULL AND declined_at IS NULL AND started_at IS NULL AND completed_at IS NULL AND paused_at IS NULL) OR
        (status = 'ACCEPTED' AND acknowledged_at IS NOT NULL AND declined_at IS NULL AND completed_at IS NULL) OR
        (status = 'DECLINED' AND declined_at IS NOT NULL AND acknowledged_at IS NULL AND started_at IS NULL AND completed_at IS NULL) OR
        (status = 'ACTIVE' AND acknowledged_at IS NOT NULL AND started_at IS NOT NULL AND declined_at IS NULL AND completed_at IS NULL AND paused_at IS NULL) OR
        (status = 'PAUSED' AND acknowledged_at IS NOT NULL AND started_at IS NOT NULL AND paused_at IS NOT NULL AND completed_at IS NULL) OR
        (status = 'COMPLETED' AND acknowledged_at IS NOT NULL AND started_at IS NOT NULL AND completed_at IS NOT NULL AND started_at <= completed_at)
    ),
    CONSTRAINT chk_intervention_rationale_no_pii CHECK (
        rationale !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_intervention_feedback_no_pii CHECK (
        student_feedback IS NULL OR
        student_feedback !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_intervention_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_intervention_tenant_student_status
    ON learning_supportintervention (tenant_id, student_id, status);

-- ----------------------------------------------------------------------------
-- 4. FOLLOW-UP ACTION
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_followupaction (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    intervention_id UUID NULL,
    session_id UUID NULL,
    student_id UUID NOT NULL,
    assigned_by_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    due_date TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    skipped_at TIMESTAMPTZ NULL,
    skip_reason VARCHAR(1000) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_followupaction PRIMARY KEY (id),
    CONSTRAINT uq_learning_followupaction_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_followupaction_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_followupaction_intervention FOREIGN KEY (tenant_id, intervention_id)
        REFERENCES learning_supportintervention(tenant_id, id) ON DELETE SET NULL (intervention_id),
    CONSTRAINT fk_followupaction_session FOREIGN KEY (tenant_id, session_id)
        REFERENCES learning_coachingsession(tenant_id, id) ON DELETE SET NULL (session_id),
    CONSTRAINT fk_followupaction_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_followupaction_assigned_by FOREIGN KEY (tenant_id, assigned_by_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT chk_followupaction_status CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED')),
    CONSTRAINT chk_followupaction_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_followupaction_origin_exact_xor CHECK (
        num_nonnulls(intervention_id, session_id) = 1
    ),
    CONSTRAINT chk_followupaction_status_time_consistency CHECK (
        (status = 'PENDING' AND completed_at IS NULL AND skipped_at IS NULL AND skip_reason IS NULL) OR
        (status = 'IN_PROGRESS' AND completed_at IS NULL AND skipped_at IS NULL AND skip_reason IS NULL) OR
        (status = 'COMPLETED' AND completed_at IS NOT NULL AND skipped_at IS NULL) OR
        (status = 'SKIPPED' AND skipped_at IS NOT NULL AND skip_reason IS NOT NULL AND completed_at IS NULL)
    ),
    CONSTRAINT chk_followupaction_skip_reason_len CHECK (skip_reason IS NULL OR (char_length(trim(skip_reason)) >= 3 AND char_length(skip_reason) <= 1000)),
    CONSTRAINT chk_followupaction_skip_reason_no_pii CHECK (
        skip_reason IS NULL OR
        skip_reason !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_followupaction_tenant_student_due
    ON learning_followupaction (tenant_id, student_id, due_date ASC);

-- ----------------------------------------------------------------------------
-- 5. COACHING AUDIT LOG (Immutable / Append-Only)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_coachingauditlog (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    actor_id UUID NOT NULL,
    target_session_id UUID NULL,
    target_intervention_id UUID NULL,
    target_action_id UUID NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_coachingauditlog PRIMARY KEY (id),
    CONSTRAINT uq_learning_coachingauditlog_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_coachingaudit_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant(id) ON DELETE CASCADE,
    CONSTRAINT fk_coachingaudit_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership(tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_coachingaudit_target_session FOREIGN KEY (tenant_id, target_session_id)
        REFERENCES learning_coachingsession(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_coachingaudit_target_intervention FOREIGN KEY (tenant_id, target_intervention_id)
        REFERENCES learning_supportintervention(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_coachingaudit_target_action FOREIGN KEY (tenant_id, target_action_id)
        REFERENCES learning_followupaction(tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_coachingaudit_target_xor CHECK (
        num_nonnulls(target_session_id, target_intervention_id, target_action_id) = 1
    ),
    CONSTRAINT chk_coachingaudit_action_type CHECK (
        action_type IN (
            'SCHEDULE_SESSION', 'START_SESSION', 'RESCHEDULE_SESSION', 'CANCEL_SESSION', 'COMPLETE_SESSION',
            'CREATE_NOTE', 'PROPOSE_INTERVENTION', 'ACCEPT_INTERVENTION', 'DECLINE_INTERVENTION',
            'START_INTERVENTION', 'PAUSE_INTERVENTION', 'RESUME_INTERVENTION', 'COMPLETE_INTERVENTION',
            'ASSIGN_ACTION', 'START_ACTION', 'COMPLETE_ACTION', 'SKIP_ACTION'
        )
    ),
    CONSTRAINT chk_coachingaudit_metadata_no_pii CHECK (
        jsonb_typeof(details) = 'object'
        AND NOT (details ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_coachingaudit_tenant_actor_time
    ON learning_coachingauditlog (tenant_id, actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_coachingaudit_tenant_session
    ON learning_coachingauditlog (tenant_id, target_session_id) WHERE target_session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_coachingaudit_tenant_intervention
    ON learning_coachingauditlog (tenant_id, target_intervention_id) WHERE target_intervention_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_coachingaudit_tenant_action
    ON learning_coachingauditlog (tenant_id, target_action_id) WHERE target_action_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- 6. POSTGRESQL 17 FORCE RLS & NOBYPASSRLS ENFORCEMENT
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_coachingsession',
        'learning_coachingnote',
        'learning_supportintervention',
        'learning_followupaction',
        'learning_coachingauditlog'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);

        EXECUTE format('DROP POLICY IF EXISTS p3_vs16_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p3_vs16_tenant_isolation_policy ON %I
             FOR ALL
             USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid)
             WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Enforce Append-Only Discipline on Notes and Audit Log
REVOKE UPDATE, DELETE ON learning_coachingnote FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_coachingnote FROM app_role;
REVOKE UPDATE, DELETE ON learning_coachingauditlog FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_coachingauditlog FROM app_role;

COMMIT;

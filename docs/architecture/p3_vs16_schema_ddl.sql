-- PostgreSQL 17 Schema DDL for P3-VS16
-- Slice: P3-VS16-MENTOR-STUDENT-SUCCESS-COACHING-AND-INTERVENTION-WORKFLOW
-- Certified Multi-Tenant Isolation via GUC "app.current_tenant"

BEGIN;

-- 1. CoachingSession Table
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
    CONSTRAINT pk_learning_coachingsession PRIMARY KEY (tenant_id, id),
    CONSTRAINT chk_coachingsession_status CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_coachingsession_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_coachingsession_time_consistency CHECK (
        (started_at IS NULL OR completed_at IS NULL OR started_at <= completed_at)
    ),
    CONSTRAINT chk_coachingsession_metadata_no_pii CHECK (
        NOT (metadata ?| ARRAY[
            'national_id', 'ssn', 'phone_number', 'mobile', 'email', 'card_number',
            'credit_card', 'cvv', 'password', 'token', 'secret', 'iban', 'address'
        ])
    )
);

-- 2. CoachingNote Table (Immutable / Append-Only Once Finalized)
CREATE TABLE IF NOT EXISTS learning_coachingnote (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    session_id UUID NOT NULL,
    author_id UUID NOT NULL,
    note_type VARCHAR(32) NOT NULL DEFAULT 'OBSERVATION',
    content TEXT NOT NULL,
    is_shared_with_student BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT pk_learning_coachingnote PRIMARY KEY (tenant_id, id),
    CONSTRAINT chk_coachingnote_type CHECK (note_type IN ('OBSERVATION', 'STRENGTH', 'GROWTH_OPPORTUNITY', 'ACTION_ITEM', 'SUMMARY')),
    CONSTRAINT chk_coachingnote_content_len CHECK (char_length(trim(content)) >= 3 AND char_length(content) <= 4000),
    CONSTRAINT fk_coachingnote_session FOREIGN KEY (tenant_id, session_id)
        REFERENCES learning_coachingsession(tenant_id, id) ON DELETE CASCADE
);

-- 3. SupportIntervention Table (Learner Agency First)
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
    CONSTRAINT pk_learning_supportintervention PRIMARY KEY (tenant_id, id),
    CONSTRAINT chk_intervention_status CHECK (status IN ('PROPOSED', 'ACCEPTED', 'DECLINED', 'ACTIVE', 'PAUSED', 'COMPLETED')),
    CONSTRAINT chk_intervention_category_supportive CHECK (category IN (
        'ACADEMIC_SCAFFOLDING', 'RESOURCE_RECOMMENDATION', 'STUDY_STRATEGY', 'PACING_ADJUSTMENT', 'PEER_STUDY_CONNECTION'
    )),
    CONSTRAINT chk_intervention_non_authoritative CHECK (is_authoritative = FALSE),
    CONSTRAINT chk_intervention_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_intervention_rationale_len CHECK (char_length(trim(rationale)) >= 10 AND char_length(rationale) <= 4000),
    CONSTRAINT chk_intervention_completion_consistency CHECK (
        (status <> 'COMPLETED' OR completed_at IS NOT NULL)
    ),
    CONSTRAINT chk_intervention_metadata_no_pii CHECK (
        NOT (metadata ?| ARRAY[
            'national_id', 'ssn', 'phone_number', 'mobile', 'email', 'card_number',
            'credit_card', 'cvv', 'password', 'token', 'secret', 'iban', 'address'
        ])
    )
);

-- 4. FollowUpAction Table
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
    CONSTRAINT pk_learning_followupaction PRIMARY KEY (tenant_id, id),
    CONSTRAINT chk_followupaction_status CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED')),
    CONSTRAINT chk_followupaction_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_followupaction_origin_xor CHECK (
        (intervention_id IS NOT NULL AND session_id IS NULL) OR
        (intervention_id IS NULL AND session_id IS NOT NULL) OR
        (intervention_id IS NOT NULL AND session_id IS NOT NULL)
    )
);

-- 5. CoachingAuditLog Table (Immutable / Append-Only)
CREATE TABLE IF NOT EXISTS learning_coachingauditlog (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    actor_id UUID NOT NULL,
    target_entity VARCHAR(64) NOT NULL,
    target_id UUID NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT pk_learning_coachingauditlog PRIMARY KEY (tenant_id, id),
    CONSTRAINT chk_coachingaudit_metadata_no_pii CHECK (
        NOT (details ?| ARRAY[
            'national_id', 'ssn', 'phone_number', 'mobile', 'email', 'card_number',
            'credit_card', 'cvv', 'password', 'token', 'secret', 'iban', 'address'
        ])
    )
);

-- RLS Enablement & Enforcement
ALTER TABLE learning_coachingsession ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingsession FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_coachingnote ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingnote FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_supportintervention ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_supportintervention FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_followupaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_followupaction FORCE ROW LEVEL SECURITY;

ALTER TABLE learning_coachingauditlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_coachingauditlog FORCE ROW LEVEL SECURITY;

-- Standard GUC Policy: Fail-Closed on NULL or Mismatch
DO $$
DECLARE
    tbl text;
BEGIN
    FOR tbl IN SELECT unnest(ARRAY[
        'learning_coachingsession',
        'learning_coachingnote',
        'learning_supportintervention',
        'learning_followupaction',
        'learning_coachingauditlog'
    ]) LOOP
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_policy ON %I;', tbl);
        EXECUTE format('
            CREATE POLICY tenant_isolation_policy ON %I
            AS RESTRICTIVE
            USING (
                tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid
            )
            WITH CHECK (
                tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid
            );
        ', tbl);
    END LOOP;
END $$;

COMMIT;

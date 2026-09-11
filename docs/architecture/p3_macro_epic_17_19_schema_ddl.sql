-- ============================================================================
-- P3-MACRO-EPIC-17-19: MENTOR OPERATIONS, LEARNING CONTINUITY & PROGRAM SUCCESS
-- POSTGRESQL 17 DDL, FORCE RLS, NOBYPASSRLS & COMPOSITE FK SPECIFICATION
-- Version: v1.2-CANONICAL
-- Authority: COMMANDER_P3_VS16_CLOSURE_AND_MACRO_EPIC_17_19_DIRECTIVE
-- Fleet Review: GLM v1.2 Audit Remediation (B1 Blocker & M-A through M-D Addressed)
-- Fleet Standard GUC: app.current_tenant
-- Session Protocol: SET LOCAL "app.current_tenant" = %s strictly inside transaction.atomic()
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. MENTOR CASELOAD ASSIGNMENT (P3-VS17)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_mentorcaseloadassignment (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    student_id UUID NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    capacity_weight NUMERIC(3,2) NOT NULL DEFAULT 1.00,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    unassigned_at TIMESTAMPTZ NULL,
    unassignment_reason VARCHAR(1000) NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_mentorcaseload PRIMARY KEY (id),
    CONSTRAINT uq_learning_mentorcaseload_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_mentorcaseload_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_mentorcaseload_mentor FOREIGN KEY (tenant_id, mentor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_mentorcaseload_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT chk_mentorcaseload_weight CHECK (capacity_weight >= 0.10 AND capacity_weight <= 5.00),
    CONSTRAINT chk_mentorcaseload_unassigned_order CHECK (
        (is_active = TRUE AND unassigned_at IS NULL AND unassignment_reason IS NULL) OR
        (is_active = FALSE AND unassigned_at IS NOT NULL AND assigned_at <= unassigned_at)
    ),
    CONSTRAINT chk_mentorcaseload_unassignment_reason_no_pii CHECK (
        unassignment_reason IS NULL OR (
            char_length(trim(unassignment_reason)) >= 3 AND char_length(unassignment_reason) <= 1000 AND
            unassignment_reason !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
        )
    ),
    CONSTRAINT chk_mentorcaseload_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_mentorcaseload_active_student
    ON learning_mentorcaseloadassignment (tenant_id, student_id)
    WHERE (is_active = TRUE);

CREATE INDEX IF NOT EXISTS idx_mentorcaseload_tenant_mentor_active
    ON learning_mentorcaseloadassignment (tenant_id, mentor_id, is_active);

-- ----------------------------------------------------------------------------
-- 2. SUPPORT QUEUE ITEM (P3-VS17)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_supportqueueitem (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    student_id UUID NOT NULL,
    source_intervention_id UUID NULL,
    source_session_id UUID NULL,
    urgency_level VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
    queue_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    due_date TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ NULL,
    resolution_notes TEXT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_supportqueueitem PRIMARY KEY (id),
    CONSTRAINT uq_learning_supportqueueitem_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_supportqueue_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_supportqueue_mentor FOREIGN KEY (tenant_id, mentor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_supportqueue_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_supportqueue_intervention FOREIGN KEY (tenant_id, source_intervention_id)
        REFERENCES learning_supportintervention (tenant_id, id) ON DELETE SET NULL (source_intervention_id),
    CONSTRAINT fk_supportqueue_session FOREIGN KEY (tenant_id, source_session_id)
        REFERENCES learning_coachingsession (tenant_id, id) ON DELETE SET NULL (source_session_id),
    CONSTRAINT chk_supportqueue_origin_at_least_one CHECK (
        source_intervention_id IS NOT NULL OR source_session_id IS NOT NULL
    ),
    CONSTRAINT chk_supportqueue_urgency CHECK (urgency_level IN ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')),
    CONSTRAINT chk_supportqueue_status CHECK (queue_status IN ('PENDING', 'IN_REVIEW', 'RESOLVED', 'DISMISSED')),
    CONSTRAINT chk_supportqueue_resolved_order CHECK (
        (queue_status IN ('PENDING', 'IN_REVIEW') AND resolved_at IS NULL AND resolution_notes IS NULL) OR
        (queue_status IN ('RESOLVED', 'DISMISSED') AND resolved_at IS NOT NULL)
    ),
    CONSTRAINT chk_supportqueue_resolution_notes_bound CHECK (
        resolution_notes IS NULL OR (
            char_length(trim(resolution_notes)) >= 5 AND char_length(resolution_notes) <= 4000 AND
            resolution_notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
        )
    ),
    CONSTRAINT chk_supportqueue_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_supportqueue_tenant_mentor_status
    ON learning_supportqueueitem (tenant_id, mentor_id, queue_status, due_date ASC);

CREATE INDEX IF NOT EXISTS idx_supportqueue_tenant_student
    ON learning_supportqueueitem (tenant_id, student_id);

-- ----------------------------------------------------------------------------
-- 3. LEARNING CHECK-IN (P3-VS18)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_learningcheckin (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    mentor_id UUID NOT NULL,
    student_id UUID NOT NULL,
    caseload_assignment_id UUID NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    scheduled_start TIMESTAMPTZ NOT NULL,
    actual_start TIMESTAMPTZ NULL,
    actual_end TIMESTAMPTZ NULL,
    rescheduled_from_id UUID NULL,
    meeting_link VARCHAR(500) NULL,
    notes TEXT NULL,
    student_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_learningcheckin PRIMARY KEY (id),
    CONSTRAINT uq_learning_learningcheckin_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_checkin_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_checkin_mentor FOREIGN KEY (tenant_id, mentor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_checkin_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT fk_checkin_caseload FOREIGN KEY (tenant_id, caseload_assignment_id)
        REFERENCES learning_mentorcaseloadassignment (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_checkin_rescheduled_from FOREIGN KEY (tenant_id, rescheduled_from_id)
        REFERENCES learning_learningcheckin (tenant_id, id) ON DELETE SET NULL (rescheduled_from_id),
    CONSTRAINT chk_checkin_status CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'RESCHEDULED', 'CANCELLED')),
    CONSTRAINT chk_checkin_timing_order CHECK (
        (actual_start IS NULL OR actual_end IS NULL OR actual_start <= actual_end)
        AND (actual_start IS NULL OR scheduled_start <= actual_start)
    ),
    CONSTRAINT chk_checkin_status_time_consistency CHECK (
        (status = 'SCHEDULED' AND actual_start IS NULL AND actual_end IS NULL) OR
        (status = 'IN_PROGRESS' AND actual_start IS NOT NULL AND actual_end IS NULL) OR
        (status = 'COMPLETED' AND actual_start IS NOT NULL AND actual_end IS NOT NULL AND actual_start <= actual_end) OR
        (status = 'RESCHEDULED' AND actual_end IS NULL) OR
        (status = 'CANCELLED' AND actual_end IS NULL)
    ),
    CONSTRAINT chk_checkin_meeting_link_safe CHECK (
        meeting_link IS NULL OR (
            meeting_link ~* '^https?://[a-zA-Z0-9.-]+' AND
            meeting_link !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
        )
    ),
    CONSTRAINT chk_checkin_notes_bound CHECK (
        notes IS NULL OR (
            char_length(trim(notes)) >= 5 AND char_length(notes) <= 4000 AND
            notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
        )
    ),
    CONSTRAINT chk_checkin_acknowledgement CHECK (
        (student_acknowledged = FALSE AND acknowledged_at IS NULL) OR
        (student_acknowledged = TRUE AND acknowledged_at IS NOT NULL)
    ),
    CONSTRAINT chk_checkin_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_checkin_tenant_mentor_sched
    ON learning_learningcheckin (tenant_id, mentor_id, scheduled_start ASC);

CREATE INDEX IF NOT EXISTS idx_checkin_tenant_student_sched
    ON learning_learningcheckin (tenant_id, student_id, scheduled_start ASC);

-- ----------------------------------------------------------------------------
-- 4. FOLLOW-UP COMMITMENT (P3-VS18)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_followupcommitment (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    checkin_id UUID NOT NULL,
    owner_role VARCHAR(16) NOT NULL,
    title VARCHAR(255) NOT NULL,
    due_date TIMESTAMPTZ NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_followupcommitment PRIMARY KEY (id),
    CONSTRAINT uq_learning_followupcommitment_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_commitment_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_commitment_checkin FOREIGN KEY (tenant_id, checkin_id)
        REFERENCES learning_learningcheckin (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_commitment_owner CHECK (owner_role IN ('MENTOR', 'STUDENT')),
    CONSTRAINT chk_commitment_title_len CHECK (char_length(trim(title)) >= 3 AND char_length(title) <= 255),
    CONSTRAINT chk_commitment_title_no_pii CHECK (
        title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_commitment_completed_order CHECK (
        (is_completed = FALSE AND completed_at IS NULL) OR
        (is_completed = TRUE AND completed_at IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_commitment_tenant_checkin_due
    ON learning_followupcommitment (tenant_id, checkin_id, due_date ASC);

-- ----------------------------------------------------------------------------
-- 5. PROGRAM SUPPORT AGGREGATE (P3-VS19)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_programsupportaggregate (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    total_assigned_students INTEGER NOT NULL DEFAULT 0,
    total_active_interventions INTEGER NOT NULL DEFAULT 0,
    total_completed_checkins INTEGER NOT NULL DEFAULT 0,
    average_response_time_hours NUMERIC(6,2) NOT NULL DEFAULT 0.00,
    support_coverage_ratio NUMERIC(4,3) NOT NULL DEFAULT 0.000,
    is_authoritative BOOLEAN NOT NULL DEFAULT FALSE,
    aggregated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_programsupportaggregate PRIMARY KEY (id),
    CONSTRAINT uq_learning_programsupportaggregate_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_supportagg_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT chk_supportagg_non_authoritative CHECK (is_authoritative = FALSE),
    CONSTRAINT chk_supportagg_period_order CHECK (period_start <= period_end)
);

CREATE INDEX IF NOT EXISTS idx_programsupportagg_tenant_period
    ON learning_programsupportaggregate (tenant_id, period_start DESC, period_end DESC);

-- ----------------------------------------------------------------------------
-- 6. MENTOR OPERATIONS AUDIT LOG (P3-MACRO-EPIC-17-19 Shared / Append-Only)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_mentoroperationsauditlog (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    actor_id UUID NOT NULL,
    target_caseload_id UUID NULL,
    target_queue_item_id UUID NULL,
    target_checkin_id UUID NULL,
    target_commitment_id UUID NULL,
    target_aggregate_id UUID NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_mentoropsaudit PRIMARY KEY (id),
    CONSTRAINT uq_learning_mentoropsaudit_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_mentoropsaudit_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_mentoropsaudit_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_mentoropsaudit_caseload FOREIGN KEY (tenant_id, target_caseload_id)
        REFERENCES learning_mentorcaseloadassignment (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_mentoropsaudit_queue FOREIGN KEY (tenant_id, target_queue_item_id)
        REFERENCES learning_supportqueueitem (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_mentoropsaudit_checkin FOREIGN KEY (tenant_id, target_checkin_id)
        REFERENCES learning_learningcheckin (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_mentoropsaudit_commitment FOREIGN KEY (tenant_id, target_commitment_id)
        REFERENCES learning_followupcommitment (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_mentoropsaudit_aggregate FOREIGN KEY (tenant_id, target_aggregate_id)
        REFERENCES learning_programsupportaggregate (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_mentoropsaudit_target_exact_xor CHECK (
        num_nonnulls(target_caseload_id, target_queue_item_id, target_checkin_id, target_commitment_id, target_aggregate_id) = 1
    ),
    CONSTRAINT chk_mentoropsaudit_action_type CHECK (
        action_type IN (
            'ASSIGN_CASELOAD', 'UNASSIGN_CASELOAD',
            'QUEUE_ITEM_PENDING', 'QUEUE_ITEM_IN_REVIEW', 'QUEUE_ITEM_RESOLVED', 'QUEUE_ITEM_DISMISSED',
            'SCHEDULE_CHECKIN', 'START_CHECKIN', 'COMPLETE_CHECKIN', 'RESCHEDULE_CHECKIN', 'CANCEL_CHECKIN',
            'CREATE_COMMITMENT', 'COMPLETE_COMMITMENT',
            'GENERATE_SUPPORT_AGGREGATE'
        )
    ),
    CONSTRAINT chk_mentoropsaudit_metadata_no_pii CHECK (
        jsonb_typeof(details) = 'object'
        AND NOT (details ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_mentoropsaudit_tenant_actor_time
    ON learning_mentoroperationsauditlog (tenant_id, actor_id, created_at DESC);

-- Partial indexes for audit log targets (M-D item 6)
CREATE INDEX IF NOT EXISTS idx_mentoropsaudit_target_caseload
    ON learning_mentoroperationsauditlog (tenant_id, target_caseload_id)
    WHERE (target_caseload_id IS NOT NULL);

CREATE INDEX IF NOT EXISTS idx_mentoropsaudit_target_queue
    ON learning_mentoroperationsauditlog (tenant_id, target_queue_item_id)
    WHERE (target_queue_item_id IS NOT NULL);

CREATE INDEX IF NOT EXISTS idx_mentoropsaudit_target_checkin
    ON learning_mentoroperationsauditlog (tenant_id, target_checkin_id)
    WHERE (target_checkin_id IS NOT NULL);

CREATE INDEX IF NOT EXISTS idx_mentoropsaudit_target_commitment
    ON learning_mentoroperationsauditlog (tenant_id, target_commitment_id)
    WHERE (target_commitment_id IS NOT NULL);

CREATE INDEX IF NOT EXISTS idx_mentoropsaudit_target_aggregate
    ON learning_mentoroperationsauditlog (tenant_id, target_aggregate_id)
    WHERE (target_aggregate_id IS NOT NULL);

-- ----------------------------------------------------------------------------
-- POSTGRESQL 17 FORCE ROW LEVEL SECURITY POLICIES
-- ----------------------------------------------------------------------------
ALTER TABLE learning_mentorcaseloadassignment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_mentorcaseloadassignment FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mentorcaseload_tenant_isolation ON learning_mentorcaseloadassignment;
CREATE POLICY mentorcaseload_tenant_isolation ON learning_mentorcaseloadassignment
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

ALTER TABLE learning_supportqueueitem ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_supportqueueitem FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS supportqueue_tenant_isolation ON learning_supportqueueitem;
CREATE POLICY supportqueue_tenant_isolation ON learning_supportqueueitem
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

ALTER TABLE learning_learningcheckin ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_learningcheckin FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS learningcheckin_tenant_isolation ON learning_learningcheckin;
CREATE POLICY learningcheckin_tenant_isolation ON learning_learningcheckin
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

ALTER TABLE learning_followupcommitment ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_followupcommitment FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS followupcommitment_tenant_isolation ON learning_followupcommitment;
CREATE POLICY followupcommitment_tenant_isolation ON learning_followupcommitment
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

ALTER TABLE learning_programsupportaggregate ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_programsupportaggregate FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS programsupportaggregate_tenant_isolation ON learning_programsupportaggregate;
CREATE POLICY programsupportaggregate_tenant_isolation ON learning_programsupportaggregate
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

ALTER TABLE learning_mentoroperationsauditlog ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_mentoroperationsauditlog FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mentoropsaudit_tenant_isolation ON learning_mentoroperationsauditlog;
CREATE POLICY mentoropsaudit_tenant_isolation ON learning_mentoroperationsauditlog
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);

-- ----------------------------------------------------------------------------
-- STRICT APPEND-ONLY DISCIPLINE: REVOKE MUTATION PERMISSIONS (BLOCKER RESOLUTION)
-- ----------------------------------------------------------------------------
REVOKE UPDATE, DELETE ON learning_mentoroperationsauditlog FROM PUBLIC;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_mentoroperationsauditlog FROM app_role;
    END IF;
END $$;

COMMIT;

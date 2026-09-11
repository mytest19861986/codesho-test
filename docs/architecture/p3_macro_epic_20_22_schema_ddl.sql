-- ============================================================================
-- P3-MACRO-EPIC-20-22: CURRICULUM DELIVERY & PROGRAM OPERATIONS
-- POSTGRESQL 17 DDL, FORCE RLS, NOBYPASSRLS & COMPOSITE FK SPECIFICATION
-- Version: v1.1-CANONICAL
-- Authority: COMMANDER_P3_MACRO_EPIC_20_22_DIRECTIVE
-- Fleet Review: GLM v1.1 Audit Remediation (B1-B4 Blockers, M1-M7 Addressed)
-- Fleet Standard GUC: app.current_tenant
-- Session Protocol: SET LOCAL "app.current_tenant" = %s strictly inside transaction.atomic()
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. P3-VS20: CURRICULUM VERSIONING & RELEASE GOVERNANCE
-- ----------------------------------------------------------------------------

-- Curriculum Version
CREATE TABLE IF NOT EXISTS learning_curriculumversion (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    course_id UUID NOT NULL,
    semver_major INT NOT NULL,
    semver_minor INT NOT NULL,
    semver_patch INT NOT NULL,
    version_tag VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    created_by_id UUID NULL,
    approved_by_id UUID NULL,
    published_at TIMESTAMPTZ NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_curriculumversion PRIMARY KEY (id),
    CONSTRAINT uq_learning_curriculumversion_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_curriculum_version_tenant_semver UNIQUE (tenant_id, course_id, semver_major, semver_minor, semver_patch),
    CONSTRAINT fk_curriculumversion_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_curriculumversion_course FOREIGN KEY (tenant_id, course_id)
        REFERENCES learning_course (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_curriculumversion_created_by FOREIGN KEY (tenant_id, created_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_curriculumversion_approved_by FOREIGN KEY (tenant_id, approved_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_curriculum_version_status CHECK (status IN ('DRAFT', 'REVIEW', 'APPROVED', 'PUBLISHED', 'RETIRED')),
    CONSTRAINT chk_curriculum_semver_nonnegative CHECK (semver_major >= 0 AND semver_minor >= 0 AND semver_patch >= 0),
    CONSTRAINT chk_curriculumversion_published_consistency CHECK (
        (status = 'PUBLISHED' AND published_at IS NOT NULL) OR
        (status != 'PUBLISHED' AND published_at IS NULL)
    ),
    CONSTRAINT chk_curriculumversion_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_curriculumversion_tenant_course_status
    ON learning_curriculumversion (tenant_id, course_id, status);

-- Course Release Mapping
CREATE TABLE IF NOT EXISTS learning_courserelease (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    course_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    release_title VARCHAR(255) NOT NULL,
    release_notes TEXT NOT NULL DEFAULT '',
    is_active_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_courserelease PRIMARY KEY (id),
    CONSTRAINT uq_learning_courserelease_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_courserelease_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_courserelease_course FOREIGN KEY (tenant_id, course_id)
        REFERENCES learning_course (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_courserelease_curriculumversion FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_courserelease_title_no_pii CHECK (
        char_length(trim(release_title)) >= 3 AND char_length(release_title) <= 255 AND
        release_title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_courserelease_notes_bound CHECK (
        char_length(release_notes) <= 4000 AND
        release_notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_courserelease_tenant_course_active
    ON learning_courserelease (tenant_id, course_id, is_active_default);

-- Module Release Snapshot (Immutable Snapshot)
CREATE TABLE IF NOT EXISTS learning_modulereleasesnapshot (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    source_module_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    snapshot_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_modulereleasesnapshot PRIMARY KEY (id),
    CONSTRAINT uq_learning_modulereleasesnapshot_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_modulereleasesnapshot_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_modulereleasesnapshot_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_modulereleasesnapshot_title_no_pii CHECK (
        char_length(trim(title)) >= 1 AND char_length(title) <= 255 AND
        title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_modulereleasesnapshot_payload_no_pii CHECK (
        jsonb_typeof(snapshot_payload) = 'object'
        AND NOT (snapshot_payload ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_modulereleasesnapshot_version_order
    ON learning_modulereleasesnapshot (tenant_id, curriculum_version_id, order_index);

-- Lesson Release Snapshot (Immutable Snapshot)
CREATE TABLE IF NOT EXISTS learning_lessonreleasesnapshot (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    module_snapshot_id UUID NOT NULL,
    source_lesson_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    content_hash VARCHAR(64) NOT NULL,
    snapshot_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_lessonreleasesnapshot PRIMARY KEY (id),
    CONSTRAINT uq_learning_lessonreleasesnapshot_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_lessonreleasesnapshot_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_lessonreleasesnapshot_module FOREIGN KEY (tenant_id, module_snapshot_id)
        REFERENCES learning_modulereleasesnapshot (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_lessonreleasesnapshot_title_no_pii CHECK (
        char_length(trim(title)) >= 1 AND char_length(title) <= 255 AND
        title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    ),
    CONSTRAINT chk_lessonreleasesnapshot_payload_no_pii CHECK (
        jsonb_typeof(snapshot_payload) = 'object'
        AND NOT (snapshot_payload ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_lessonreleasesnapshot_module_order
    ON learning_lessonreleasesnapshot (tenant_id, module_snapshot_id, order_index);

-- Release Approval Record (Append-Only)
CREATE TABLE IF NOT EXISTS learning_releaseapprovalrecord (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    reviewer_id UUID NOT NULL,
    decision VARCHAR(32) NOT NULL,
    review_comments TEXT NOT NULL DEFAULT '',
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_releaseapprovalrecord PRIMARY KEY (id),
    CONSTRAINT uq_learning_releaseapprovalrecord_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_releaseapproval_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_releaseapproval_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_releaseapproval_reviewer FOREIGN KEY (tenant_id, reviewer_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_releaseapproval_decision CHECK (decision IN ('APPROVED', 'REJECTED', 'CHANGES_REQUESTED')),
    CONSTRAINT chk_releaseapproval_comments_bound CHECK (
        char_length(review_comments) <= 4000 AND
        review_comments !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_releaseapproval_tenant_version_time
    ON learning_releaseapprovalrecord (tenant_id, curriculum_version_id, reviewed_at DESC);

-- Curriculum Release Audit Log (Append-Only)
CREATE TABLE IF NOT EXISTS learning_curriculumreleaseauditlog (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NULL,
    course_release_id UUID NULL,
    actor_id UUID NOT NULL,
    action VARCHAR(64) NOT NULL,
    previous_state VARCHAR(32) NULL,
    new_state VARCHAR(32) NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_curriculumreleaseauditlog PRIMARY KEY (id),
    CONSTRAINT uq_learning_curriculumreleaseauditlog_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_curriculumreleaseauditlog_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_curriculumreleaseauditlog_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_curriculumreleaseauditlog_release FOREIGN KEY (tenant_id, course_release_id)
        REFERENCES learning_courserelease (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_curriculumreleaseauditlog_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_curriculum_audit_xor CHECK (
        num_nonnulls(curriculum_version_id, course_release_id) = 1
    ),
    CONSTRAINT chk_curriculumreleaseauditlog_details_no_pii CHECK (
        jsonb_typeof(details) = 'object'
        AND NOT (details ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_curriculumreleaseauditlog_tenant_actor_time
    ON learning_curriculumreleaseauditlog (tenant_id, actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_curriculumreleaseauditlog_target_version
    ON learning_curriculumreleaseauditlog (tenant_id, curriculum_version_id)
    WHERE (curriculum_version_id IS NOT NULL);
CREATE INDEX IF NOT EXISTS idx_curriculumreleaseauditlog_target_release
    ON learning_curriculumreleaseauditlog (tenant_id, course_release_id)
    WHERE (course_release_id IS NOT NULL);

-- ----------------------------------------------------------------------------
-- 2. P3-VS21: COHORT SCHEDULE & LEARNING SESSION ORCHESTRATION
-- ----------------------------------------------------------------------------

-- Cohort Schedule
CREATE TABLE IF NOT EXISTS learning_cohortschedule (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cohort_id UUID NOT NULL,
    course_release_id UUID NOT NULL,
    schedule_title VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    recurrence_rule VARCHAR(128) NOT NULL DEFAULT 'WEEKLY',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_cohortschedule PRIMARY KEY (id),
    CONSTRAINT uq_learning_cohortschedule_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_cohortschedule_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_cohortschedule_cohort FOREIGN KEY (tenant_id, cohort_id)
        REFERENCES learning_cohort (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_cohortschedule_release FOREIGN KEY (tenant_id, course_release_id)
        REFERENCES learning_courserelease (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_cohortschedule_dates_order CHECK (start_date <= end_date),
    CONSTRAINT chk_cohortschedule_title_no_pii CHECK (
        char_length(trim(schedule_title)) >= 3 AND char_length(schedule_title) <= 255 AND
        schedule_title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_cohortschedule_tenant_cohort_active
    ON learning_cohortschedule (tenant_id, cohort_id, is_active);

-- Learning Session
CREATE TABLE IF NOT EXISTS learning_learningsession (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cohort_schedule_id UUID NOT NULL,
    session_title VARCHAR(255) NOT NULL,
    session_order INT NOT NULL DEFAULT 1,
    lesson_snapshot_id UUID NULL,
    assigned_mentor_id UUID NULL,
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_learningsession PRIMARY KEY (id),
    CONSTRAINT uq_learning_learningsession_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_learningsession_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_learningsession_cohortschedule FOREIGN KEY (tenant_id, cohort_schedule_id)
        REFERENCES learning_cohortschedule (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_learningsession_lessonsnapshot FOREIGN KEY (tenant_id, lesson_snapshot_id)
        REFERENCES learning_lessonreleasesnapshot (tenant_id, id) ON DELETE SET NULL (lesson_snapshot_id),
    CONSTRAINT fk_learningsession_mentor FOREIGN KEY (tenant_id, assigned_mentor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_learningsession_status CHECK (status IN ('SCHEDULED', 'IN_SESSION', 'COMPLETED', 'RESCHEDULED', 'CANCELLED')),
    CONSTRAINT chk_learningsession_timing_order CHECK (scheduled_start < scheduled_end),
    CONSTRAINT chk_learningsession_title_no_pii CHECK (
        char_length(trim(session_title)) >= 3 AND char_length(session_title) <= 255 AND
        session_title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_learningsession_tenant_schedule_time
    ON learning_learningsession (tenant_id, cohort_schedule_id, scheduled_start ASC);
CREATE INDEX IF NOT EXISTS idx_learningsession_tenant_mentor_status
    ON learning_learningsession (tenant_id, assigned_mentor_id, status);

-- Session Occurrence
CREATE TABLE IF NOT EXISTS learning_sessionoccurrence (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    learning_session_id UUID NOT NULL,
    actual_start TIMESTAMPTZ NULL,
    actual_end TIMESTAMPTZ NULL,
    occurrence_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    attendance_count INT NOT NULL DEFAULT 0,
    operational_notes TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_sessionoccurrence PRIMARY KEY (id),
    CONSTRAINT uq_learning_sessionoccurrence_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_sessionoccurrence_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_sessionoccurrence_session FOREIGN KEY (tenant_id, learning_session_id)
        REFERENCES learning_learningsession (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_sessionoccurrence_status CHECK (occurrence_status IN ('PENDING', 'CONDUCTED', 'MISSED', 'SUBSTITUTE_CONDUCTED')),
    CONSTRAINT chk_session_timing_order CHECK (actual_start IS NULL OR actual_end IS NULL OR actual_start <= actual_end),
    CONSTRAINT chk_sessionoccurrence_status_time_consistency CHECK (
        (occurrence_status = 'PENDING' AND actual_start IS NULL AND actual_end IS NULL) OR
        (occurrence_status = 'CONDUCTED' AND actual_start IS NOT NULL AND actual_end IS NOT NULL) OR
        (occurrence_status = 'SUBSTITUTE_CONDUCTED' AND actual_start IS NOT NULL AND actual_end IS NOT NULL) OR
        (occurrence_status = 'MISSED' AND actual_end IS NULL)
    ),
    CONSTRAINT chk_sessionoccurrence_notes_bound CHECK (
        char_length(operational_notes) <= 4000 AND
        operational_notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_sessionoccurrence_tenant_session_time
    ON learning_sessionoccurrence (tenant_id, learning_session_id, actual_start ASC);

-- Session Attendance State (Synthetic records only, strictly non-punitive)
CREATE TABLE IF NOT EXISTS learning_sessionattendancestate (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    session_occurrence_id UUID NOT NULL,
    student_id UUID NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PRESENT',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_sessionattendancestate PRIMARY KEY (id),
    CONSTRAINT uq_learning_sessionattendancestate_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_sessionattendancestate_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_sessionattendancestate_occurrence FOREIGN KEY (tenant_id, session_occurrence_id)
        REFERENCES learning_sessionoccurrence (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_sessionattendancestate_student FOREIGN KEY (tenant_id, student_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE CASCADE,
    CONSTRAINT uq_session_attendance_student UNIQUE (tenant_id, session_occurrence_id, student_id),
    CONSTRAINT chk_sessionattendance_status CHECK (status IN ('PRESENT', 'ABSENT', 'EXCUSED', 'LATE'))
);

CREATE INDEX IF NOT EXISTS idx_sessionattendancestate_tenant_student
    ON learning_sessionattendancestate (tenant_id, student_id, status);

-- Session Change Record (Audit trail for rescheduling/cancellation, Append-Only)
CREATE TABLE IF NOT EXISTS learning_sessionchangerecord (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    learning_session_id UUID NOT NULL,
    changed_by_id UUID NOT NULL,
    change_type VARCHAR(32) NOT NULL,
    original_start TIMESTAMPTZ NULL,
    new_start TIMESTAMPTZ NULL,
    reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_sessionchangerecord PRIMARY KEY (id),
    CONSTRAINT uq_learning_sessionchangerecord_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_sessionchangerecord_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_sessionchangerecord_session FOREIGN KEY (tenant_id, learning_session_id)
        REFERENCES learning_learningsession (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_sessionchangerecord_changed_by FOREIGN KEY (tenant_id, changed_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_sessionchange_type CHECK (change_type IN ('RESCHEDULED', 'CANCELLED', 'MENTOR_REASSIGNED', 'TOPIC_UPDATED')),
    CONSTRAINT chk_sessionchangerecord_reason_bound CHECK (
        char_length(reason) <= 2000 AND
        reason !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_sessionchangerecord_tenant_session_time
    ON learning_sessionchangerecord (tenant_id, learning_session_id, created_at DESC);

-- ----------------------------------------------------------------------------
-- 3. P3-VS22: PROGRAM DELIVERY QUALITY & OPERATIONS CONTROL CENTER
-- ----------------------------------------------------------------------------

-- Program Delivery Aggregate (Derived, Non-Authoritative Projection)
CREATE TABLE IF NOT EXISTS learning_programdeliveryaggregate (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cohort_id UUID NOT NULL,
    total_sessions INT NOT NULL DEFAULT 0,
    completed_sessions INT NOT NULL DEFAULT 0,
    cancelled_sessions INT NOT NULL DEFAULT 0,
    rescheduled_sessions INT NOT NULL DEFAULT 0,
    active_release_version VARCHAR(32) NOT NULL DEFAULT '',
    is_authoritative BOOLEAN NOT NULL DEFAULT FALSE,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT pk_learning_programdeliveryaggregate PRIMARY KEY (id),
    CONSTRAINT uq_learning_programdeliveryaggregate_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_programdeliveryagg_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_programdeliveryagg_cohort FOREIGN KEY (tenant_id, cohort_id)
        REFERENCES learning_cohort (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_deliveryagg_cohort UNIQUE (tenant_id, cohort_id),
    CONSTRAINT chk_deliveryagg_non_authoritative CHECK (is_authoritative = FALSE),
    CONSTRAINT chk_deliveryagg_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_programdeliveryagg_tenant_computed
    ON learning_programdeliveryaggregate (tenant_id, computed_at DESC);

-- Curriculum Release Coverage Projection
CREATE TABLE IF NOT EXISTS learning_curriculumreleasecoverage (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    course_id UUID NOT NULL,
    cohorts_adopted_count INT NOT NULL DEFAULT 0,
    active_learners_count INT NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_curriculumreleasecoverage PRIMARY KEY (id),
    CONSTRAINT uq_learning_curriculumreleasecoverage_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_curriculumreleasecoverage_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_curriculumreleasecoverage_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_curriculumreleasecoverage_course FOREIGN KEY (tenant_id, course_id)
        REFERENCES learning_course (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_releasecoverage_version UNIQUE (tenant_id, curriculum_version_id)
);

CREATE INDEX IF NOT EXISTS idx_curriculumreleasecoverage_tenant_course
    ON learning_curriculumreleasecoverage (tenant_id, course_id);

-- Cohort Schedule Health Projection
CREATE TABLE IF NOT EXISTS learning_cohortschedulehealth (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cohort_schedule_id UUID NOT NULL,
    health_status VARCHAR(32) NOT NULL DEFAULT 'ON_TRACK',
    pending_sessions_count INT NOT NULL DEFAULT 0,
    delayed_sessions_count INT NOT NULL DEFAULT 0,
    missed_occurrences_count INT NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_cohortschedulehealth PRIMARY KEY (id),
    CONSTRAINT uq_learning_cohortschedulehealth_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_cohortschedulehealth_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_cohortschedulehealth_schedule FOREIGN KEY (tenant_id, cohort_schedule_id)
        REFERENCES learning_cohortschedule (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_cohortschedulehealth_schedule UNIQUE (tenant_id, cohort_schedule_id),
    CONSTRAINT chk_cohortschedulehealth_status CHECK (health_status IN ('ON_TRACK', 'ATTENTION_NEEDED', 'AT_RISK', 'CRITICAL_DELAY'))
);

CREATE INDEX IF NOT EXISTS idx_cohortschedulehealth_tenant_status
    ON learning_cohortschedulehealth (tenant_id, health_status);

-- Delivery Exception Queue
CREATE TABLE IF NOT EXISTS learning_deliveryexceptionqueue (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cohort_id UUID NOT NULL,
    learning_session_id UUID NULL,
    exception_type VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    description TEXT NOT NULL,
    resolved_by_id UUID NULL,
    resolved_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_deliveryexceptionqueue PRIMARY KEY (id),
    CONSTRAINT uq_learning_deliveryexceptionqueue_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_deliveryexception_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_deliveryexception_cohort FOREIGN KEY (tenant_id, cohort_id)
        REFERENCES learning_cohort (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_deliveryexception_session FOREIGN KEY (tenant_id, learning_session_id)
        REFERENCES learning_learningsession (tenant_id, id) ON DELETE SET NULL (learning_session_id),
    CONSTRAINT fk_deliveryexception_resolved_by FOREIGN KEY (tenant_id, resolved_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_deliveryexception_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    CONSTRAINT chk_deliveryexception_status CHECK (status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'IGNORED')),
    CONSTRAINT chk_deliveryexception_resolved_order CHECK (
        (status IN ('OPEN', 'INVESTIGATING') AND resolved_at IS NULL AND resolved_by_id IS NULL) OR
        (status IN ('RESOLVED', 'IGNORED') AND resolved_at IS NOT NULL)
    ),
    CONSTRAINT chk_deliveryexception_desc_bound CHECK (
        char_length(trim(description)) >= 5 AND char_length(description) <= 4000 AND
        description !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_deliveryexception_tenant_status_severity
    ON learning_deliveryexceptionqueue (tenant_id, status, severity, created_at DESC);

-- ----------------------------------------------------------------------------
-- 4. POSTGRESQL 17 FORCE ROW LEVEL SECURITY POLICIES
-- ----------------------------------------------------------------------------

DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'learning_curriculumversion',
        'learning_courserelease',
        'learning_modulereleasesnapshot',
        'learning_lessonreleasesnapshot',
        'learning_releaseapprovalrecord',
        'learning_curriculumreleaseauditlog',
        'learning_cohortschedule',
        'learning_learningsession',
        'learning_sessionoccurrence',
        'learning_sessionattendancestate',
        'learning_sessionchangerecord',
        'learning_programdeliveryaggregate',
        'learning_curriculumreleasecoverage',
        'learning_cohortschedulehealth',
        'learning_deliveryexceptionqueue'
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', t);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', t);
        EXECUTE format('DROP POLICY IF EXISTS p3_tenant_isolation_policy ON %I;', t);
        EXECUTE format(
            'CREATE POLICY p3_tenant_isolation_policy ON %I ' ||
            'FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
            'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            t
        );
    END LOOP;
END $$;

-- ----------------------------------------------------------------------------
-- 5. STRICT APPEND-ONLY DISCIPLINE: REVOKE MUTATION PERMISSIONS
-- ----------------------------------------------------------------------------
REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM app_role;
        REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM app_role;
        REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM app_role;
        REVOKE UPDATE, DELETE ON learning_releaseapprovalrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_sessionchangerecord FROM app_role;
    END IF;
END $$;

COMMIT;

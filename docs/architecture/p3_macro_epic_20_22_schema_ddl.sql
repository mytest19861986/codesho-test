-- ==============================================================================
-- P3-MACRO-EPIC-20-22 Canonical PostgreSQL 17 DDL Schema
-- Slices: P3-VS20, P3-VS21, P3-VS22
-- Standard: PostgreSQL 17, FORCE RLS, NOBYPASSRLS, Composite FKs (Zero Bare UUIDs)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. P3-VS20: Curriculum Versioning & Release Governance
-- ------------------------------------------------------------------------------

-- Curriculum Version
CREATE TABLE IF NOT EXISTS learning_curriculumversion (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    course_id UUID NOT NULL,
    semver_major INT NOT NULL,
    semver_minor INT NOT NULL,
    semver_patch INT NOT NULL,
    version_tag VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    created_by_id UUID,
    approved_by_id UUID,
    published_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_curriculumversion PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_curriculumversion_id UNIQUE (id),
    CONSTRAINT uq_curriculum_version_tenant_semver UNIQUE (tenant_id, course_id, semver_major, semver_minor, semver_patch),
    CONSTRAINT chk_curriculum_version_status CHECK (status IN ('DRAFT', 'REVIEW', 'APPROVED', 'PUBLISHED', 'RETIRED')),
    CONSTRAINT chk_curriculum_semver_nonnegative CHECK (semver_major >= 0 AND semver_minor >= 0 AND semver_patch >= 0)
);

-- Course Release Mapping
CREATE TABLE IF NOT EXISTS learning_courserelease (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    course_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    release_title VARCHAR(255) NOT NULL,
    release_notes TEXT NOT NULL DEFAULT '',
    is_active_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_courserelease PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_courserelease_id UNIQUE (id),
    CONSTRAINT fk_courserelease_curriculumversion FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT
);

-- Module Release Snapshot (Immutable)
CREATE TABLE IF NOT EXISTS learning_modulereleasesnapshot (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    source_module_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    snapshot_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_modulereleasesnapshot PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_modulereleasesnapshot_id UNIQUE (id),
    CONSTRAINT fk_modulereleasesnapshot_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT
);

-- Lesson Release Snapshot (Immutable)
CREATE TABLE IF NOT EXISTS learning_lessonreleasesnapshot (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    module_snapshot_id UUID NOT NULL,
    source_lesson_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    content_hash VARCHAR(64) NOT NULL,
    snapshot_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_lessonreleasesnapshot PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_lessonreleasesnapshot_id UNIQUE (id),
    CONSTRAINT fk_lessonreleasesnapshot_module FOREIGN KEY (tenant_id, module_snapshot_id)
        REFERENCES learning_modulereleasesnapshot (tenant_id, id) ON DELETE RESTRICT
);

-- Release Approval Record
CREATE TABLE IF NOT EXISTS learning_releaseapprovalrecord (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    reviewer_id UUID NOT NULL,
    decision VARCHAR(32) NOT NULL,
    review_comments TEXT NOT NULL DEFAULT '',
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_releaseapprovalrecord PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_releaseapprovalrecord_id UNIQUE (id),
    CONSTRAINT fk_releaseapproval_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_releaseapproval_decision CHECK (decision IN ('APPROVED', 'REJECTED', 'CHANGES_REQUESTED'))
);

-- Curriculum Release Audit Log (Append-Only)
CREATE TABLE IF NOT EXISTS learning_curriculumreleaseauditlog (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID,
    course_release_id UUID,
    actor_id UUID,
    action VARCHAR(64) NOT NULL,
    previous_state VARCHAR(32),
    new_state VARCHAR(32),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_curriculumreleaseauditlog PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_curriculumreleaseauditlog_id UNIQUE (id),
    CONSTRAINT chk_curriculum_audit_xor CHECK (
        (curriculum_version_id IS NOT NULL AND course_release_id IS NULL) OR
        (curriculum_version_id IS NULL AND course_release_id IS NOT NULL)
    )
);

-- ------------------------------------------------------------------------------
-- 2. P3-VS21: Cohort Schedule & Learning Session Orchestration
-- ------------------------------------------------------------------------------

-- Cohort Schedule
CREATE TABLE IF NOT EXISTS learning_cohortschedule (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    cohort_id UUID NOT NULL,
    course_release_id UUID NOT NULL,
    schedule_title VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    recurrence_rule VARCHAR(128) NOT NULL DEFAULT 'WEEKLY',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_cohortschedule PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_cohortschedule_id UNIQUE (id),
    CONSTRAINT fk_cohortschedule_release FOREIGN KEY (tenant_id, course_release_id)
        REFERENCES learning_courserelease (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_cohortschedule_dates_order CHECK (start_date <= end_date)
);

-- Learning Session
CREATE TABLE IF NOT EXISTS learning_learningsession (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    cohort_schedule_id UUID NOT NULL,
    session_title VARCHAR(255) NOT NULL,
    session_order INT NOT NULL DEFAULT 1,
    lesson_snapshot_id UUID,
    assigned_mentor_id UUID,
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_learningsession PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_learningsession_id UNIQUE (id),
    CONSTRAINT fk_learningsession_cohortschedule FOREIGN KEY (tenant_id, cohort_schedule_id)
        REFERENCES learning_cohortschedule (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_learningsession_lessonsnapshot FOREIGN KEY (tenant_id, lesson_snapshot_id)
        REFERENCES learning_lessonreleasesnapshot (tenant_id, id) ON DELETE SET NULL,
    CONSTRAINT chk_learningsession_status CHECK (status IN ('SCHEDULED', 'IN_SESSION', 'COMPLETED', 'RESCHEDULED', 'CANCELLED')),
    CONSTRAINT chk_learningsession_timing_order CHECK (scheduled_start < scheduled_end)
);

-- Session Occurrence
CREATE TABLE IF NOT EXISTS learning_sessionoccurrence (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    learning_session_id UUID NOT NULL,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,
    occurrence_status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    attendance_count INT NOT NULL DEFAULT 0,
    operational_notes TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_sessionoccurrence PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_sessionoccurrence_id UNIQUE (id),
    CONSTRAINT fk_sessionoccurrence_session FOREIGN KEY (tenant_id, learning_session_id)
        REFERENCES learning_learningsession (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_sessionoccurrence_status CHECK (occurrence_status IN ('PENDING', 'CONDUCTED', 'MISSED', 'SUBSTITUTE_CONDUCTED')),
    CONSTRAINT chk_session_timing_order CHECK (actual_start IS NULL OR actual_end IS NULL OR actual_start <= actual_end)
);

-- Session Attendance State (Synthetic records only, strictly non-punitive)
CREATE TABLE IF NOT EXISTS learning_sessionattendancestate (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    session_occurrence_id UUID NOT NULL,
    student_id UUID NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PRESENT',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_sessionattendancestate PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_sessionattendancestate_id UNIQUE (id),
    CONSTRAINT fk_sessionattendancestate_occurrence FOREIGN KEY (tenant_id, session_occurrence_id)
        REFERENCES learning_sessionoccurrence (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_session_attendance_student UNIQUE (tenant_id, session_occurrence_id, student_id),
    CONSTRAINT chk_sessionattendance_status CHECK (status IN ('PRESENT', 'ABSENT', 'EXCUSED', 'LATE'))
);

-- Session Change Record (Audit trail for rescheduling/cancellation)
CREATE TABLE IF NOT EXISTS learning_sessionchangerecord (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    learning_session_id UUID NOT NULL,
    changed_by_id UUID,
    change_type VARCHAR(32) NOT NULL,
    original_start TIMESTAMPTZ,
    new_start TIMESTAMPTZ,
    reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_sessionchangerecord PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_sessionchangerecord_id UNIQUE (id),
    CONSTRAINT fk_sessionchangerecord_session FOREIGN KEY (tenant_id, learning_session_id)
        REFERENCES learning_learningsession (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_sessionchange_type CHECK (change_type IN ('RESCHEDULED', 'CANCELLED', 'MENTOR_REASSIGNED', 'TOPIC_UPDATED'))
);

-- ------------------------------------------------------------------------------
-- 3. P3-VS22: Program Delivery Quality & Operations Control Center
-- ------------------------------------------------------------------------------

-- Program Delivery Aggregate (Derived, Non-Authoritative Projection)
CREATE TABLE IF NOT EXISTS learning_programdeliveryaggregate (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    cohort_id UUID NOT NULL,
    total_sessions INT NOT NULL DEFAULT 0,
    completed_sessions INT NOT NULL DEFAULT 0,
    cancelled_sessions INT NOT NULL DEFAULT 0,
    rescheduled_sessions INT NOT NULL DEFAULT 0,
    active_release_version VARCHAR(32) NOT NULL DEFAULT '',
    is_authoritative BOOLEAN NOT NULL DEFAULT FALSE,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT pk_learning_programdeliveryaggregate PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_programdeliveryaggregate_id UNIQUE (id),
    CONSTRAINT uq_deliveryagg_cohort UNIQUE (tenant_id, cohort_id),
    CONSTRAINT chk_deliveryagg_non_authoritative CHECK (is_authoritative = FALSE)
);

-- Curriculum Release Coverage Projection
CREATE TABLE IF NOT EXISTS learning_curriculumreleasecoverage (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    course_id UUID NOT NULL,
    cohorts_adopted_count INT NOT NULL DEFAULT 0,
    active_learners_count INT NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_curriculumreleasecoverage PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_curriculumreleasecoverage_id UNIQUE (id),
    CONSTRAINT fk_curriculumreleasecoverage_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_releasecoverage_version UNIQUE (tenant_id, curriculum_version_id)
);

-- Cohort Schedule Health Projection
CREATE TABLE IF NOT EXISTS learning_cohortschedulehealth (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    cohort_schedule_id UUID NOT NULL,
    health_status VARCHAR(32) NOT NULL DEFAULT 'ON_TRACK',
    pending_sessions_count INT NOT NULL DEFAULT 0,
    delayed_sessions_count INT NOT NULL DEFAULT 0,
    missed_occurrences_count INT NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_cohortschedulehealth PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_cohortschedulehealth_id UNIQUE (id),
    CONSTRAINT fk_cohortschedulehealth_schedule FOREIGN KEY (tenant_id, cohort_schedule_id)
        REFERENCES learning_cohortschedule (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_cohortschedulehealth_schedule UNIQUE (tenant_id, cohort_schedule_id),
    CONSTRAINT chk_cohortschedulehealth_status CHECK (health_status IN ('ON_TRACK', 'ATTENTION_NEEDED', 'AT_RISK', 'CRITICAL_DELAY'))
);

-- Delivery Exception Queue
CREATE TABLE IF NOT EXISTS learning_deliveryexceptionqueue (
    id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    cohort_id UUID NOT NULL,
    learning_session_id UUID,
    exception_type VARCHAR(64) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    description TEXT NOT NULL,
    resolved_by_id UUID,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_deliveryexceptionqueue PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_learning_deliveryexceptionqueue_id UNIQUE (id),
    CONSTRAINT fk_deliveryexception_session FOREIGN KEY (tenant_id, learning_session_id)
        REFERENCES learning_learningsession (tenant_id, id) ON DELETE SET NULL,
    CONSTRAINT chk_deliveryexception_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    CONSTRAINT chk_deliveryexception_status CHECK (status IN ('OPEN', 'INVESTIGATING', 'RESOLVED', 'IGNORED'))
);

-- ------------------------------------------------------------------------------
-- 4. PostgreSQL 17 FORCE RLS Policies & Revocations
-- ------------------------------------------------------------------------------

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

-- Enforce Immutability & Append-Only Grants
REVOKE UPDATE, DELETE ON learning_curriculumreleaseauditlog FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_modulereleasesnapshot FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_lessonreleasesnapshot FROM PUBLIC;

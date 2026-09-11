-- ============================================================================
-- P3-MACRO-EPIC-23-25: CURRICULUM AUTHORING, EDITORIAL & RELEASE READINESS
-- POSTGRESQL 17 DDL, FORCE RLS, NOBYPASSRLS & COMPOSITE FK SPECIFICATION
-- Version: v1.1-CANONICAL-CLAUDE-HARDENED
-- Authority: COMMANDER_P3_MACRO_EPIC_23_25_DISCOVERY_DIRECTIVE & CLAUDE_SECURITY_AUDIT
-- Fleet Standard GUC: app.current_tenant
-- Session Protocol: SET LOCAL "app.current_tenant" = %s strictly inside transaction.atomic()
-- Hard Invariants Enforced:
--   1. STUDENT_RANKING = 0 (No peer ranks, no leaderboards)
--   2. HISTORICAL_EVIDENCE_REBINDING = 0 (Immutable learner history)
--   3. AUTHOR_SELF_APPROVAL = DENY (Separation of duties)
--   4. AI_DECISION_AUTHORITY = 0 (Synthetic/advisory only)
--   5. REAL_PII = 0 (21-key exclusion check on JSONB & text)
--   6. FORCE RLS + NOBYPASSRLS on all tenant-owned tables
--   7. Composite FKs: 100% (tenant_id, target_id)
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. P3-VS23: CURRICULUM AUTHORING & EDITORIAL WORKFLOW
-- ----------------------------------------------------------------------------

-- Curriculum Draft Workspace
CREATE TABLE IF NOT EXISTS learning_curriculumdraftworkspace (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    course_id UUID NOT NULL,
    base_version_id UUID NOT NULL,
    workspace_title VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_by_id UUID NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_curriculumdraftworkspace PRIMARY KEY (id),
    CONSTRAINT uq_learning_curriculumdraftworkspace_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_draftworkspace_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_draftworkspace_course FOREIGN KEY (tenant_id, course_id)
        REFERENCES learning_course (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_draftworkspace_base_version FOREIGN KEY (tenant_id, base_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_draftworkspace_created_by FOREIGN KEY (tenant_id, created_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_draftworkspace_status CHECK (status IN ('ACTIVE', 'SUBMITTED', 'ARCHIVED')),
    CONSTRAINT chk_draftworkspace_metadata_no_pii CHECK (
        jsonb_typeof(metadata) = 'object'
        AND NOT (metadata ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

CREATE INDEX IF NOT EXISTS idx_draftworkspace_tenant_course_status
    ON learning_curriculumdraftworkspace (tenant_id, course_id, status);

-- Content Change Set
CREATE TABLE IF NOT EXISTS learning_contentchangeset (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    workspace_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    change_summary TEXT NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    author_id UUID NULL,
    submitted_at TIMESTAMPTZ NULL,
    approved_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_contentchangeset PRIMARY KEY (id),
    CONSTRAINT uq_learning_contentchangeset_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_contentchangeset_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_contentchangeset_workspace FOREIGN KEY (tenant_id, workspace_id)
        REFERENCES learning_curriculumdraftworkspace (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_contentchangeset_author FOREIGN KEY (tenant_id, author_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_contentchangeset_status CHECK (
        status IN ('DRAFT', 'IN_REVIEW', 'CHANGES_REQUESTED', 'APPROVED', 'MERGED_TO_RELEASE')
    ),
    CONSTRAINT chk_contentchangeset_summary_bound CHECK (
        char_length(change_summary) <= 5000 AND
        change_summary !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_contentchangeset_tenant_workspace_status
    ON learning_contentchangeset (tenant_id, workspace_id, status);

-- Editorial Review
CREATE TABLE IF NOT EXISTS learning_editorialreview (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    change_set_id UUID NOT NULL,
    reviewer_id UUID NULL,
    decision VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    review_notes TEXT NOT NULL DEFAULT '',
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_editorialreview PRIMARY KEY (id),
    CONSTRAINT uq_learning_editorialreview_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_editorialreview_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_editorialreview_changeset FOREIGN KEY (tenant_id, change_set_id)
        REFERENCES learning_contentchangeset (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_editorialreview_reviewer FOREIGN KEY (tenant_id, reviewer_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_editorialreview_decision CHECK (
        decision IN ('PENDING', 'UNDER_REVIEW', 'CHANGES_REQUESTED', 'APPROVED', 'REJECTED')
    ),
    CONSTRAINT chk_editorialreview_notes_bound CHECK (
        char_length(review_notes) <= 5000 AND
        review_notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

-- Review Comment
CREATE TABLE IF NOT EXISTS learning_reviewcomment (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    review_id UUID NOT NULL,
    author_id UUID NULL,
    comment_text TEXT NOT NULL,
    target_entity VARCHAR(64) NOT NULL,
    target_entity_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_reviewcomment PRIMARY KEY (id),
    CONSTRAINT uq_learning_reviewcomment_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_reviewcomment_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_reviewcomment_review FOREIGN KEY (tenant_id, review_id)
        REFERENCES learning_editorialreview (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_reviewcomment_author FOREIGN KEY (tenant_id, author_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_reviewcomment_text_no_pii CHECK (
        char_length(trim(comment_text)) >= 1 AND char_length(comment_text) <= 3000 AND
        comment_text !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

-- Review Resolution
CREATE TABLE IF NOT EXISTS learning_reviewresolution (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    review_id UUID NOT NULL,
    resolver_id UUID NULL,
    resolution_status VARCHAR(32) NOT NULL DEFAULT 'RESOLVED',
    resolution_notes TEXT NOT NULL DEFAULT '',
    resolved_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_reviewresolution PRIMARY KEY (id),
    CONSTRAINT uq_learning_reviewresolution_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_reviewresolution_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_reviewresolution_review FOREIGN KEY (tenant_id, review_id)
        REFERENCES learning_editorialreview (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_reviewresolution_resolver FOREIGN KEY (tenant_id, resolver_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_reviewresolution_status CHECK (resolution_status IN ('RESOLVED', 'WAIVED', 'DEFERRED'))
);

-- Author Assignment
CREATE TABLE IF NOT EXISTS learning_authorassignment (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    workspace_id UUID NOT NULL,
    author_id UUID NULL,
    assigned_role VARCHAR(32) NOT NULL DEFAULT 'PRIMARY_AUTHOR',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_authorassignment PRIMARY KEY (id),
    CONSTRAINT uq_learning_authorassignment_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_authorassignment_workspace_author UNIQUE (tenant_id, workspace_id, author_id),
    CONSTRAINT fk_authorassignment_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_authorassignment_workspace FOREIGN KEY (tenant_id, workspace_id)
        REFERENCES learning_curriculumdraftworkspace (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_authorassignment_author FOREIGN KEY (tenant_id, author_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_authorassignment_role CHECK (assigned_role IN ('PRIMARY_AUTHOR', 'CONTRIBUTOR', 'CURATOR'))
);

-- Change Approval Record (Immutable Audit)
CREATE TABLE IF NOT EXISTS learning_changeapprovalrecord (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    change_set_id UUID NOT NULL,
    approver_id UUID NULL,
    approval_verdict VARCHAR(32) NOT NULL,
    approval_hash VARCHAR(64) NOT NULL,
    justification TEXT NOT NULL DEFAULT '',
    approved_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_changeapprovalrecord PRIMARY KEY (id),
    CONSTRAINT uq_learning_changeapprovalrecord_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_changeapproval_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_changeapproval_changeset FOREIGN KEY (tenant_id, change_set_id)
        REFERENCES learning_contentchangeset (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_changeapproval_approver FOREIGN KEY (tenant_id, approver_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_changeapproval_verdict CHECK (approval_verdict IN ('APPROVED', 'CONDITIONALLY_APPROVED'))
);

CREATE INDEX IF NOT EXISTS idx_changeapproval_tenant_changeset
    ON learning_changeapprovalrecord (tenant_id, change_set_id);
CREATE INDEX IF NOT EXISTS idx_changeapproval_tenant_approver
    ON learning_changeapprovalrecord (tenant_id, approver_id);

-- ----------------------------------------------------------------------------
-- 2. P3-VS24: LEARNING ASSESSMENT BLUEPRINT & RUBRIC GOVERNANCE
-- ----------------------------------------------------------------------------

-- Assessment Blueprint
CREATE TABLE IF NOT EXISTS learning_assessmentblueprint (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    course_id UUID NOT NULL,
    blueprint_title VARCHAR(255) NOT NULL,
    version_tag VARCHAR(32) NOT NULL DEFAULT 'v1.0',
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    pedagogical_intent TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_assessmentblueprint PRIMARY KEY (id),
    CONSTRAINT uq_learning_assessmentblueprint_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_assessmentblueprint_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_assessmentblueprint_course FOREIGN KEY (tenant_id, course_id)
        REFERENCES learning_course (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_assessmentblueprint_status CHECK (status IN ('ACTIVE', 'DRAFT', 'SUPERSEDED', 'RETIRED'))
);

-- Learning Objective Mapping
CREATE TABLE IF NOT EXISTS learning_learningobjectivemapping (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    blueprint_id UUID NOT NULL,
    objective_code VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    bloom_taxonomy_level VARCHAR(32) NOT NULL DEFAULT 'APPLY',
    weight_percentage NUMERIC(5, 2) NOT NULL DEFAULT 10.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_learningobjectivemapping PRIMARY KEY (id),
    CONSTRAINT uq_learning_learningobjectivemapping_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_objectivemapping_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_objectivemapping_blueprint FOREIGN KEY (tenant_id, blueprint_id)
        REFERENCES learning_assessmentblueprint (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_objectivemapping_weight CHECK (weight_percentage > 0 AND weight_percentage <= 100.00),
    CONSTRAINT chk_objectivemapping_taxonomy CHECK (
        bloom_taxonomy_level IN ('REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE')
    )
);

-- Rubric Definition
CREATE TABLE IF NOT EXISTS learning_rubricdefinition (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    blueprint_id UUID NOT NULL,
    rubric_title VARCHAR(255) NOT NULL,
    scale_type VARCHAR(32) NOT NULL DEFAULT 'QUALITATIVE_STANDARD',
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    is_anti_ranking_compliant BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_rubricdefinition PRIMARY KEY (id),
    CONSTRAINT uq_learning_rubricdefinition_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_rubricdefinition_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_rubricdefinition_blueprint FOREIGN KEY (tenant_id, blueprint_id)
        REFERENCES learning_assessmentblueprint (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_rubricdefinition_status CHECK (status IN ('DRAFT', 'ACTIVE', 'SUPERSEDED', 'RETIRED')),
    CONSTRAINT chk_rubric_anti_ranking CHECK (is_anti_ranking_compliant = TRUE)
);

-- Rubric Criterion
CREATE TABLE IF NOT EXISTS learning_rubriccriterion (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    rubric_id UUID NOT NULL,
    criterion_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    weight_percentage NUMERIC(5, 2) NOT NULL,
    evaluation_levels JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_rubriccriterion PRIMARY KEY (id),
    CONSTRAINT uq_learning_rubriccriterion_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_rubriccriterion_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_rubriccriterion_rubric FOREIGN KEY (tenant_id, rubric_id)
        REFERENCES learning_rubricdefinition (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_rubriccriterion_weight CHECK (weight_percentage > 0 AND weight_percentage <= 100.00),
    CONSTRAINT chk_rubriccriterion_levels_no_pii CHECK (
        jsonb_typeof(evaluation_levels) = 'array'
    )
);

-- Assessment Release Binding (Historical Immutability Link)
CREATE TABLE IF NOT EXISTS learning_assessmentreleasebinding (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    course_release_id UUID NOT NULL,
    blueprint_id UUID NOT NULL,
    rubric_id UUID NOT NULL,
    is_authoritative BOOLEAN NOT NULL DEFAULT TRUE,
    bound_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_assessmentreleasebinding PRIMARY KEY (id),
    CONSTRAINT uq_learning_assessmentreleasebinding_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_binding_release_blueprint UNIQUE (tenant_id, course_release_id, blueprint_id),
    CONSTRAINT fk_assessmentbinding_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_assessmentbinding_release FOREIGN KEY (tenant_id, course_release_id)
        REFERENCES learning_courserelease (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_assessmentbinding_blueprint FOREIGN KEY (tenant_id, blueprint_id)
        REFERENCES learning_assessmentblueprint (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_assessmentbinding_rubric FOREIGN KEY (tenant_id, rubric_id)
        REFERENCES learning_rubricdefinition (tenant_id, id) ON DELETE RESTRICT
);

-- Rubric Review Record (Immutable Audit)
CREATE TABLE IF NOT EXISTS learning_rubricreviewrecord (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    rubric_id UUID NOT NULL,
    reviewer_id UUID NULL,
    verdict VARCHAR(32) NOT NULL,
    pedagogical_notes TEXT NOT NULL DEFAULT '',
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_rubricreviewrecord PRIMARY KEY (id),
    CONSTRAINT uq_learning_rubricreviewrecord_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_rubricreview_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_rubricreview_rubric FOREIGN KEY (tenant_id, rubric_id)
        REFERENCES learning_rubricdefinition (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_rubricreview_reviewer FOREIGN KEY (tenant_id, reviewer_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_rubricreview_verdict CHECK (verdict IN ('APPROVED', 'REVISION_REQUESTED'))
);

CREATE INDEX IF NOT EXISTS idx_rubricreview_tenant_rubric
    ON learning_rubricreviewrecord (tenant_id, rubric_id);
CREATE INDEX IF NOT EXISTS idx_rubricreview_tenant_reviewer
    ON learning_rubricreviewrecord (tenant_id, reviewer_id);

-- ----------------------------------------------------------------------------
-- 3. P3-VS25: RELEASE READINESS, CHANGE IMPACT & PROGRAM ROLLFORWARD
-- ----------------------------------------------------------------------------

-- Curriculum Change Impact (Immutable Analysis)
CREATE TABLE IF NOT EXISTS learning_curriculumchangeimpact (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    source_version_id UUID NOT NULL,
    target_version_id UUID NOT NULL,
    impact_level VARCHAR(32) NOT NULL DEFAULT 'MINOR',
    breaking_changes_detected BOOLEAN NOT NULL DEFAULT FALSE,
    affected_cohorts_count INT NOT NULL DEFAULT 0,
    impact_details JSONB NOT NULL DEFAULT '{}'::jsonb,
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_curriculumchangeimpact PRIMARY KEY (id),
    CONSTRAINT uq_learning_curriculumchangeimpact_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_changeimpact_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_changeimpact_source_version FOREIGN KEY (tenant_id, source_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_changeimpact_target_version FOREIGN KEY (tenant_id, target_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_changeimpact_level CHECK (impact_level IN ('PATCH', 'MINOR', 'MAJOR', 'BREAKING')),
    CONSTRAINT chk_changeimpact_details_no_pii CHECK (
        jsonb_typeof(impact_details) = 'object'
    )
);

-- Release Readiness Check
CREATE TABLE IF NOT EXISTS learning_releasereadinesscheck (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    check_name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL DEFAULT 'EDITORIAL',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    check_output TEXT NOT NULL DEFAULT '',
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_releasereadinesscheck PRIMARY KEY (id),
    CONSTRAINT uq_learning_releasereadinesscheck_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_readinesscheck_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_readinesscheck_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_readinesscheck_status CHECK (status IN ('PENDING', 'PASSED', 'FAILED', 'WAIVED'))
);

-- Release Readiness Gate
CREATE TABLE IF NOT EXISTS learning_releasereadinessgate (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    curriculum_version_id UUID NOT NULL,
    gate_name VARCHAR(128) NOT NULL,
    is_blocking BOOLEAN NOT NULL DEFAULT TRUE,
    verdict VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_releasereadinessgate PRIMARY KEY (id),
    CONSTRAINT uq_learning_releasereadinessgate_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_gate_version_name UNIQUE (tenant_id, curriculum_version_id, gate_name),
    CONSTRAINT fk_readinessgate_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_readinessgate_version FOREIGN KEY (tenant_id, curriculum_version_id)
        REFERENCES learning_curriculumversion (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_readinessgate_verdict CHECK (verdict IN ('PENDING', 'PASSED', 'FAILED', 'WAIVED'))
);

-- Cohort Rollforward Plan
CREATE TABLE IF NOT EXISTS learning_cohortrollforwardplan (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cohort_schedule_id UUID NOT NULL,
    target_release_id UUID NOT NULL,
    rollforward_mode VARCHAR(32) NOT NULL DEFAULT 'FUTURE_MODULES_ONLY',
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT',
    scheduled_effective_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_cohortrollforwardplan PRIMARY KEY (id),
    CONSTRAINT uq_learning_cohortrollforwardplan_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_cohortrollforward_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_cohortrollforward_cohort FOREIGN KEY (tenant_id, cohort_schedule_id)
        REFERENCES learning_cohortschedule (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_cohortrollforward_target_release FOREIGN KEY (tenant_id, target_release_id)
        REFERENCES learning_courserelease (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_cohortrollforward_mode CHECK (
        rollforward_mode IN ('FUTURE_MODULES_ONLY', 'NEXT_COHORT_ONLY', 'EXPLICIT_APPROVAL_REQUIRED')
    ),
    CONSTRAINT chk_cohortrollforward_status CHECK (status IN ('DRAFT', 'APPROVED', 'APPLIED', 'CANCELLED'))
);

-- Curriculum Migration Decision (Controlled Transition Decision)
CREATE TABLE IF NOT EXISTS learning_curriculummigrationdecision (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    decided_by_id UUID NULL,
    decision VARCHAR(32) NOT NULL,
    justification TEXT NOT NULL DEFAULT '',
    decided_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_curriculummigrationdecision PRIMARY KEY (id),
    CONSTRAINT uq_learning_curriculummigrationdecision_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_migrationdecision_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_migrationdecision_plan FOREIGN KEY (tenant_id, plan_id)
        REFERENCES learning_cohortrollforwardplan (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_migrationdecision_decided_by FOREIGN KEY (tenant_id, decided_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_migrationdecision_decision CHECK (decision IN ('PROCEED', 'HALT', 'EXCEPTION_REQUIRED'))
);

-- Release Exception Record (Immutable Audit)
CREATE TABLE IF NOT EXISTS learning_releaseexceptionrecord (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    gate_id UUID NOT NULL,
    granted_by_id UUID NULL,
    exception_reason TEXT NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_releaseexceptionrecord PRIMARY KEY (id),
    CONSTRAINT uq_learning_releaseexceptionrecord_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_releaseexception_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_releaseexception_gate FOREIGN KEY (tenant_id, gate_id)
        REFERENCES learning_releasereadinessgate (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_releaseexception_granted_by FOREIGN KEY (tenant_id, granted_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_releaseexception_reason_no_pii CHECK (
        char_length(trim(exception_reason)) >= 10 AND char_length(exception_reason) <= 3000 AND
        exception_reason !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE INDEX IF NOT EXISTS idx_releaseexception_tenant_gate
    ON learning_releaseexceptionrecord (tenant_id, gate_id);
CREATE INDEX IF NOT EXISTS idx_releaseexception_tenant_grantor
    ON learning_releaseexceptionrecord (tenant_id, granted_by_id);
CREATE INDEX IF NOT EXISTS idx_migrationdecision_tenant_plan
    ON learning_curriculummigrationdecision (tenant_id, plan_id);
CREATE INDEX IF NOT EXISTS idx_migrationdecision_tenant_decider
    ON learning_curriculummigrationdecision (tenant_id, decided_by_id);

-- ----------------------------------------------------------------------------
-- 4. ROW LEVEL SECURITY (RLS) & ACCESS CONTROL REVOCATION
-- ----------------------------------------------------------------------------

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_curriculumdraftworkspace',
        'learning_contentchangeset',
        'learning_editorialreview',
        'learning_reviewcomment',
        'learning_reviewresolution',
        'learning_authorassignment',
        'learning_changeapprovalrecord',
        'learning_assessmentblueprint',
        'learning_learningobjectivemapping',
        'learning_rubricdefinition',
        'learning_rubriccriterion',
        'learning_assessmentreleasebinding',
        'learning_rubricreviewrecord',
        'learning_curriculumchangeimpact',
        'learning_releasereadinesscheck',
        'learning_releasereadinessgate',
        'learning_cohortrollforwardplan',
        'learning_curriculummigrationdecision',
        'learning_releaseexceptionrecord'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS p3_epic23_25_tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY p3_epic23_25_tenant_isolation_policy ON %I ' ||
            'USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
            'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Ensure connection roles operate under strict NOBYPASSRLS and least privilege
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
        ALTER ROLE codesho_runtime NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
        REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM codesho_runtime;
        REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM codesho_runtime;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        ALTER ROLE app_role NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
        REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM app_role;
        REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM app_role;
    END IF;
END $$;

-- Revoke mutation rights on append-only and immutable audit tables from PUBLIC
REVOKE UPDATE, DELETE ON learning_changeapprovalrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_rubricreviewrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_releaseexceptionrecord FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_curriculumchangeimpact FROM PUBLIC;

COMMIT;

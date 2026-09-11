-- ==============================================================================
-- P3-MACRO-EPIC-26-28 SCHEMA DDL v1.1-HARDENED
-- Enterprise Governance, Data Lifecycle & Pilot Readiness Center
-- PostgreSQL 17 Canonical Hardened DDL
-- Remediation for GLM Discovery Audit (B1, B2, M1-M6 Resolved)
-- Session Protocol: SET LOCAL "app.current_tenant" = %s inside transaction.atomic()
-- ==============================================================================

BEGIN;

-- ------------------------------------------------------------------------------
-- 1. P3-VS26: DELEGATED ADMINISTRATION & ACCESS GOVERNANCE
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_staff_access_assignment (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role_name VARCHAR(64) NOT NULL,
    scope_type VARCHAR(32) NOT NULL DEFAULT 'TENANT_WIDE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    valid_until TIMESTAMPTZ NULL,
    assigned_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_staff_access_assignment PRIMARY KEY (id),
    CONSTRAINT uq_learning_staff_access_assignment_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_staff_assignment UNIQUE (tenant_id, user_id, role_name),
    CONSTRAINT fk_staff_assignment_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_staff_assignment_user FOREIGN KEY (tenant_id, user_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_staff_assignment_assigned_by FOREIGN KEY (tenant_id, assigned_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_staff_role_valid CHECK (role_name IN ('TENANT_ADMIN', 'DELEGATED_STAFF', 'COMPLIANCE_OFFICER', 'AUDITOR', 'PROGRAM_OPERATOR')),
    CONSTRAINT chk_staff_validity_window CHECK (valid_until IS NULL OR valid_until > valid_from)
);

CREATE INDEX IF NOT EXISTS idx_staff_assignment_tenant_user_active
    ON learning_staff_access_assignment (tenant_id, user_id, is_active);

CREATE TABLE IF NOT EXISTS learning_delegated_admin_scope (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    assignment_id UUID NOT NULL,
    scope_resource_type VARCHAR(64) NOT NULL,
    scope_resource_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_delegated_admin_scope PRIMARY KEY (id),
    CONSTRAINT uq_learning_delegated_admin_scope_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_scope_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_scope_assignment FOREIGN KEY (tenant_id, assignment_id)
        REFERENCES learning_staff_access_assignment (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT chk_scope_resource_type CHECK (scope_resource_type IN ('BRANCH', 'PROGRAM', 'DEPARTMENT', 'COHORT'))
);

CREATE TABLE IF NOT EXISTS learning_privileged_permission_grant (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    permission_code VARCHAR(64) NOT NULL,
    justification TEXT NOT NULL,
    granted_by_id UUID NOT NULL,
    second_approver_id UUID NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_privileged_permission_grant PRIMARY KEY (id),
    CONSTRAINT uq_learning_privileged_permission_grant_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_privilege_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_privilege_user FOREIGN KEY (tenant_id, user_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_privilege_granted_by FOREIGN KEY (tenant_id, granted_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_privilege_second_approver FOREIGN KEY (tenant_id, second_approver_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_privilege_no_self_grant CHECK (user_id <> granted_by_id),
    CONSTRAINT chk_privilege_distinct_second_approver CHECK (second_approver_id IS NULL OR second_approver_id <> granted_by_id),
    CONSTRAINT chk_privilege_status CHECK (status IN ('ACTIVE', 'EXPIRED', 'REVOKED')),
    CONSTRAINT chk_privilege_justification_pii CHECK (
        char_length(trim(justification)) >= 5 AND char_length(justification) <= 2000 AND
        justification !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_access_review_campaign (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    campaign_period VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    deadline TIMESTAMPTZ NOT NULL,
    created_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_access_review_campaign PRIMARY KEY (id),
    CONSTRAINT uq_learning_access_review_campaign_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_campaign_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_campaign_created_by FOREIGN KEY (tenant_id, created_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_campaign_status CHECK (status IN ('ACTIVE', 'CONCLUDED', 'CANCELLED')),
    CONSTRAINT chk_campaign_title_pii CHECK (
        char_length(trim(title)) >= 3 AND char_length(title) <= 255 AND
        title !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_access_review_decision (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    campaign_id UUID NOT NULL,
    assignment_id UUID NOT NULL,
    reviewer_id UUID NOT NULL,
    decision VARCHAR(32) NOT NULL, -- MAINTAIN, REVOKE, RESTRICT
    notes TEXT NOT NULL DEFAULT '',
    decided_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_access_review_decision PRIMARY KEY (id),
    CONSTRAINT uq_learning_access_review_decision_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_review_decision_per_assignment UNIQUE (tenant_id, campaign_id, assignment_id),
    CONSTRAINT fk_decision_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_decision_campaign FOREIGN KEY (tenant_id, campaign_id)
        REFERENCES learning_access_review_campaign (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_decision_assignment FOREIGN KEY (tenant_id, assignment_id)
        REFERENCES learning_staff_access_assignment (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_decision_reviewer FOREIGN KEY (tenant_id, reviewer_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_review_decision CHECK (decision IN ('MAINTAIN', 'REVOKE', 'RESTRICT')),
    CONSTRAINT chk_review_notes_pii CHECK (
        char_length(notes) <= 2000 AND
        notes !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_privileged_action_audit (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    target_resource VARCHAR(128) NOT NULL,
    ip_address INET NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_privileged_action_audit PRIMARY KEY (id),
    CONSTRAINT uq_learning_privileged_action_audit_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_audit_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_audit_actor FOREIGN KEY (tenant_id, actor_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_privileged_action_audit_details_no_pii CHECK (
        jsonb_typeof(details) = 'object'
        AND NOT (details ?| ARRAY[
            'name', 'phone', 'email', 'national_id', 'location', 'avatar_url', 'phone_number',
            'mobile', 'fingerprint', 'face_id', 'voice_sample', 'bank_account', 'iban', 'credit_card',
            'card_number', 'cvv', 'password', 'token', 'secret', 'ssn', 'address'
        ])
    )
);

-- ------------------------------------------------------------------------------
-- 2. P3-VS27: DATA LIFECYCLE, RETENTION & DISPOSITION GOVERNANCE
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_data_retention_policy (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    data_category VARCHAR(64) NOT NULL,
    retention_period_days INT NOT NULL,
    disposition_action VARCHAR(32) NOT NULL DEFAULT 'ANONYMIZE',
    created_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_data_retention_policy PRIMARY KEY (id),
    CONSTRAINT uq_learning_data_retention_policy_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_retention_category UNIQUE (tenant_id, data_category),
    CONSTRAINT fk_retention_policy_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_retention_policy_created_by FOREIGN KEY (tenant_id, created_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_retention_period_positive CHECK (retention_period_days >= 30),
    CONSTRAINT chk_disposition_action CHECK (disposition_action IN ('ANONYMIZE', 'PURGE', 'ARCHIVE'))
);

CREATE TABLE IF NOT EXISTS learning_retention_policy_version (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    version_number INT NOT NULL,
    retention_period_days INT NOT NULL,
    disposition_action VARCHAR(32) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    created_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_retention_policy_version PRIMARY KEY (id),
    CONSTRAINT uq_learning_retention_policy_version_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_policy_version UNIQUE (tenant_id, policy_id, version_number),
    CONSTRAINT fk_version_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_version_policy FOREIGN KEY (tenant_id, policy_id)
        REFERENCES learning_data_retention_policy (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_version_created_by FOREIGN KEY (tenant_id, created_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS learning_legal_hold (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    legal_case_reference VARCHAR(128) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    placed_by_id UUID NOT NULL,
    placed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    released_by_id UUID NULL,
    released_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_legal_hold PRIMARY KEY (id),
    CONSTRAINT uq_learning_legal_hold_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_hold_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_hold_placed_by FOREIGN KEY (tenant_id, placed_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_hold_released_by FOREIGN KEY (tenant_id, released_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_hold_status CHECK (status IN ('ACTIVE', 'RELEASED')),
    CONSTRAINT chk_hold_release_consistency CHECK (
        (status = 'RELEASED' AND released_at IS NOT NULL AND released_by_id IS NOT NULL) OR
        (status = 'ACTIVE' AND released_at IS NULL AND released_by_id IS NULL)
    ),
    CONSTRAINT chk_hold_reason_pii CHECK (
        char_length(trim(reason)) >= 5 AND char_length(reason) <= 2000 AND
        reason !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_legal_hold_scope (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    legal_hold_id UUID NOT NULL,
    target_entity_type VARCHAR(64) NOT NULL,
    target_entity_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_legal_hold_scope PRIMARY KEY (id),
    CONSTRAINT uq_learning_legal_hold_scope_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_scope_hold_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_scope_legal_hold FOREIGN KEY (tenant_id, legal_hold_id)
        REFERENCES learning_legal_hold (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_retention_evaluation (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    policy_id UUID NOT NULL,
    evaluated_entity_type VARCHAR(64) NOT NULL,
    candidates_count INT NOT NULL DEFAULT 0,
    exempted_by_legal_hold_count INT NOT NULL DEFAULT 0,
    disposition_ready_count INT NOT NULL DEFAULT 0,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_retention_evaluation PRIMARY KEY (id),
    CONSTRAINT uq_learning_retention_evaluation_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_eval_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_eval_policy FOREIGN KEY (tenant_id, policy_id)
        REFERENCES learning_data_retention_policy (tenant_id, id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS learning_data_disposition_record (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    evaluation_id UUID NOT NULL,
    action_applied VARCHAR(32) NOT NULL,
    records_processed INT NOT NULL DEFAULT 0,
    cryptographic_digest VARCHAR(128) NOT NULL,
    executed_by_id UUID NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_data_disposition_record PRIMARY KEY (id),
    CONSTRAINT uq_learning_data_disposition_record_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_disp_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_disp_eval FOREIGN KEY (tenant_id, evaluation_id)
        REFERENCES learning_retention_evaluation (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_disp_executed_by FOREIGN KEY (tenant_id, executed_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS learning_disposition_audit_log (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    disposition_record_id UUID NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_key_hash VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_disposition_audit_log PRIMARY KEY (id),
    CONSTRAINT uq_learning_disposition_audit_log_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_disp_audit_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_disp_audit_rec FOREIGN KEY (tenant_id, disposition_record_id)
        REFERENCES learning_data_disposition_record (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

-- ------------------------------------------------------------------------------
-- 3. P3-VS28: ENTERPRISE CONTROL EVIDENCE & PILOT READINESS CENTER
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_readiness_control (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    control_code VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_readiness_control PRIMARY KEY (id),
    CONSTRAINT uq_learning_readiness_control_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT uq_readiness_control_code UNIQUE (tenant_id, control_code),
    CONSTRAINT fk_control_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT chk_control_category CHECK (category IN ('SECURITY', 'DATA_GOVERNANCE', 'TESTING', 'RLS', 'FLEET')),
    CONSTRAINT chk_control_desc_pii CHECK (
        char_length(trim(description)) >= 5 AND char_length(description) <= 2000 AND
        description !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_readiness_evidence (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    control_id UUID NOT NULL,
    evidence_type VARCHAR(64) NOT NULL,
    artifact_reference VARCHAR(255) NOT NULL,
    verification_hash VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'VALID',
    recorded_by_id UUID NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_readiness_evidence PRIMARY KEY (id),
    CONSTRAINT uq_learning_readiness_evidence_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_evidence_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_evidence_control FOREIGN KEY (tenant_id, control_id)
        REFERENCES learning_readiness_control (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_evidence_recorded_by FOREIGN KEY (tenant_id, recorded_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_evidence_status CHECK (status IN ('VALID', 'SUPERSEDED', 'REVOKED'))
);

CREATE TABLE IF NOT EXISTS learning_readiness_assessment_run (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    run_reference VARCHAR(64) NOT NULL,
    total_controls INT NOT NULL DEFAULT 0,
    passed_controls INT NOT NULL DEFAULT 0,
    failed_controls INT NOT NULL DEFAULT 0,
    overall_status VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS',
    executed_by_id UUID NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_readiness_assessment_run PRIMARY KEY (id),
    CONSTRAINT uq_learning_readiness_assessment_run_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_run_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_run_executed_by FOREIGN KEY (tenant_id, executed_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_run_status CHECK (overall_status IN ('IN_PROGRESS', 'READY', 'NOT_READY', 'BLOCKED', 'EXCEPTION_REQUIRED'))
);

CREATE TABLE IF NOT EXISTS learning_readiness_finding (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    assessment_run_id UUID NOT NULL,
    control_id UUID NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MAJOR',
    finding_summary TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_readiness_finding PRIMARY KEY (id),
    CONSTRAINT uq_learning_readiness_finding_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_finding_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_finding_run FOREIGN KEY (tenant_id, assessment_run_id)
        REFERENCES learning_readiness_assessment_run (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_finding_control FOREIGN KEY (tenant_id, control_id)
        REFERENCES learning_readiness_control (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_finding_severity CHECK (severity IN ('BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR')),
    CONSTRAINT chk_finding_summary_pii CHECK (
        char_length(trim(finding_summary)) >= 5 AND char_length(finding_summary) <= 2000 AND
        finding_summary !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_readiness_exception (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    finding_id UUID NOT NULL,
    reason TEXT NOT NULL,
    expiry_date TIMESTAMPTZ NOT NULL,
    approved_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_readiness_exception PRIMARY KEY (id),
    CONSTRAINT uq_learning_readiness_exception_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_exception_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_exception_finding FOREIGN KEY (tenant_id, finding_id)
        REFERENCES learning_readiness_finding (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_exception_approved_by FOREIGN KEY (tenant_id, approved_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_exception_reason_pii CHECK (
        char_length(trim(reason)) >= 5 AND char_length(reason) <= 2000 AND
        reason !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_pilot_readiness_gate (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    assessment_run_id UUID NOT NULL,
    gate_verdict VARCHAR(32) NOT NULL,
    human_attestation_summary TEXT NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_pilot_readiness_gate PRIMARY KEY (id),
    CONSTRAINT uq_learning_pilot_readiness_gate_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_gate_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_gate_assessment FOREIGN KEY (tenant_id, assessment_run_id)
        REFERENCES learning_readiness_assessment_run (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT chk_gate_verdict CHECK (gate_verdict IN ('READY', 'NOT_READY', 'BLOCKED', 'EXCEPTION_REQUIRED')),
    CONSTRAINT chk_attestation_summary_pii CHECK (
        char_length(trim(human_attestation_summary)) >= 5 AND char_length(human_attestation_summary) <= 2000 AND
        human_attestation_summary !~* '(\+?[0-9]{10,14}|[0-9]{3}-?[0-9]{2}-?[0-9]{4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{16}|IR[0-9]{24}|fingerprint|face_id|voice_sample|bank_account|iban|credit_card)'
    )
);

CREATE TABLE IF NOT EXISTS learning_control_attestation_audit (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    gate_id UUID NOT NULL,
    attested_by_id UUID NOT NULL,
    attestation_role VARCHAR(64) NOT NULL,
    signature_digest VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),

    CONSTRAINT pk_learning_control_attestation_audit PRIMARY KEY (id),
    CONSTRAINT uq_learning_control_attestation_audit_tenant_id UNIQUE (tenant_id, id),
    CONSTRAINT fk_attestation_audit_tenant FOREIGN KEY (tenant_id)
        REFERENCES platform_tenant_tenant (id) ON DELETE CASCADE,
    CONSTRAINT fk_attestation_gate FOREIGN KEY (tenant_id, gate_id)
        REFERENCES learning_pilot_readiness_gate (tenant_id, id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_attestation_attested_by FOREIGN KEY (tenant_id, attested_by_id)
        REFERENCES platform_tenant_tenantmembership (tenant_id, user_id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

-- ------------------------------------------------------------------------------
-- 4. STRATEGIC COVERAGE INDEXES (P3-MACRO-EPIC-26-28)
-- ------------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_staff_assignment_tenant_user_active
    ON learning_staff_access_assignment (tenant_id, user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_delegated_admin_scope_tenant_assignment
    ON learning_delegated_admin_scope (tenant_id, assignment_id);

CREATE INDEX IF NOT EXISTS idx_privileged_permission_grant_tenant_user_status
    ON learning_privileged_permission_grant (tenant_id, user_id, status);

CREATE INDEX IF NOT EXISTS idx_access_review_campaign_tenant_status
    ON learning_access_review_campaign (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_access_review_decision_tenant_campaign_reviewer
    ON learning_access_review_decision (tenant_id, campaign_id, reviewer_id);

CREATE INDEX IF NOT EXISTS idx_privileged_action_audit_tenant_actor_created
    ON learning_privileged_action_audit (tenant_id, actor_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_data_retention_policy_tenant_active
    ON learning_data_retention_policy (tenant_id, is_active);

CREATE INDEX IF NOT EXISTS idx_retention_policy_version_tenant_policy
    ON learning_retention_policy_version (tenant_id, policy_id, version_number DESC);

CREATE INDEX IF NOT EXISTS idx_legal_hold_tenant_status
    ON learning_legal_hold (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_legal_hold_scope_tenant_hold
    ON learning_legal_hold_scope (tenant_id, hold_id);

CREATE INDEX IF NOT EXISTS idx_data_disposition_record_tenant_status
    ON learning_data_disposition_record (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_disposition_audit_log_tenant_actor_created
    ON learning_disposition_audit_log (tenant_id, actor_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_readiness_control_tenant_category
    ON learning_readiness_control (tenant_id, control_category);

CREATE INDEX IF NOT EXISTS idx_readiness_assessment_run_tenant_status
    ON learning_readiness_assessment_run (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_readiness_finding_tenant_severity_status
    ON learning_readiness_finding (tenant_id, severity, status);

CREATE INDEX IF NOT EXISTS idx_pilot_readiness_gate_tenant_status
    ON learning_pilot_readiness_gate (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_control_attestation_audit_tenant_gate
    ON learning_control_attestation_audit (tenant_id, gate_id, created_at DESC);

-- ------------------------------------------------------------------------------
-- 5. ROW LEVEL SECURITY (RLS) & AUDIT REVOCATION GUARDS
-- ------------------------------------------------------------------------------

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_staff_access_assignment',
        'learning_delegated_admin_scope',
        'learning_privileged_permission_grant',
        'learning_access_review_campaign',
        'learning_access_review_decision',
        'learning_privileged_action_audit',
        'learning_data_retention_policy',
        'learning_retention_policy_version',
        'learning_legal_hold',
        'learning_legal_hold_scope',
        'learning_retention_evaluation',
        'learning_data_disposition_record',
        'learning_disposition_audit_log',
        'learning_readiness_control',
        'learning_readiness_evidence',
        'learning_readiness_assessment_run',
        'learning_readiness_finding',
        'learning_readiness_exception',
        'learning_pilot_readiness_gate',
        'learning_control_attestation_audit'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_policy ON %I;', tbl);
        EXECUTE format(
            'CREATE POLICY tenant_isolation_policy ON %I FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Enforce append-only immutability on audit and evidence tables
REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_readiness_evidence FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
        REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM app_role;
        REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM app_role;
        REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM app_role;
        REVOKE UPDATE, DELETE ON learning_readiness_evidence FROM app_role;
    END IF;
END $$;

COMMIT;

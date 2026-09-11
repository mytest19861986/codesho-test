-- ==============================================================================
-- P3-MACRO-EPIC-26-28 SCHEMA DDL v1.0
-- Enterprise Governance, Data Lifecycle & Pilot Readiness Center
-- PostgreSQL 17 Canonical Hardened DDL
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. EXTENSIONS & DOMAINS
-- ------------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 2. P3-VS26: DELEGATED ADMINISTRATION & ACCESS GOVERNANCE
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_staff_access_assignment (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    role_name VARCHAR(64) NOT NULL,
    scope_type VARCHAR(32) NOT NULL DEFAULT 'TENANT_WIDE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMPTZ NULL,
    assigned_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_staff_access_assignment PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_staff_assignment UNIQUE (tenant_id, user_id, role_name)
);

CREATE TABLE IF NOT EXISTS learning_delegated_admin_scope (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    assignment_id UUID NOT NULL,
    scope_resource_type VARCHAR(64) NOT NULL,
    scope_resource_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_delegated_admin_scope PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_scope_assignment FOREIGN KEY (tenant_id, assignment_id)
        REFERENCES learning_staff_access_assignment (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_privileged_permission_grant (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    permission_code VARCHAR(64) NOT NULL,
    justification TEXT NOT NULL,
    granted_by_id UUID NOT NULL,
    second_approver_id UUID NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_privileged_permission_grant PRIMARY KEY (tenant_id, id),
    CONSTRAINT chk_privilege_no_self_grant CHECK (user_id <> granted_by_id)
);

CREATE TABLE IF NOT EXISTS learning_access_review_campaign (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    campaign_period VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    deadline TIMESTAMPTZ NOT NULL,
    created_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_access_review_campaign PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS learning_access_review_decision (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL,
    assignment_id UUID NOT NULL,
    reviewer_id UUID NOT NULL,
    decision VARCHAR(32) NOT NULL, -- MAINTAIN, REVOKE, RESTRICT
    notes TEXT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_access_review_decision PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_decision_campaign FOREIGN KEY (tenant_id, campaign_id)
        REFERENCES learning_access_review_campaign (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_decision_assignment FOREIGN KEY (tenant_id, assignment_id)
        REFERENCES learning_staff_access_assignment (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_review_decision_per_assignment UNIQUE (tenant_id, campaign_id, assignment_id)
);

CREATE TABLE IF NOT EXISTS learning_privileged_action_audit (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    actor_id UUID NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    target_resource VARCHAR(128) NOT NULL,
    ip_address INET NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_privileged_action_audit PRIMARY KEY (tenant_id, id)
);

-- ------------------------------------------------------------------------------
-- 3. P3-VS27: DATA LIFECYCLE, RETENTION & DISPOSITION GOVERNANCE
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_data_retention_policy (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    data_category VARCHAR(64) NOT NULL,
    retention_period_days INT NOT NULL,
    disposition_action VARCHAR(32) NOT NULL DEFAULT 'ANONYMIZE', -- ANONYMIZE, PURGE, ARCHIVE
    created_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_data_retention_policy PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_retention_category UNIQUE (tenant_id, data_category)
);

CREATE TABLE IF NOT EXISTS learning_retention_policy_version (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    policy_id UUID NOT NULL,
    version_number INT NOT NULL,
    retention_period_days INT NOT NULL,
    disposition_action VARCHAR(32) NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_retention_policy_version PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_policy_version FOREIGN KEY (tenant_id, policy_id)
        REFERENCES learning_data_retention_policy (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT uq_policy_version UNIQUE (tenant_id, policy_id, version_number)
);

CREATE TABLE IF NOT EXISTS learning_legal_hold (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    legal_case_reference VARCHAR(128) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, RELEASED
    placed_by_id UUID NOT NULL,
    placed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    released_by_id UUID NULL,
    released_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_legal_hold PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS learning_legal_hold_scope (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    legal_hold_id UUID NOT NULL,
    target_entity_type VARCHAR(64) NOT NULL,
    target_entity_id VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_legal_hold_scope PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_hold_scope FOREIGN KEY (tenant_id, legal_hold_id)
        REFERENCES learning_legal_hold (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_retention_evaluation (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    policy_id UUID NOT NULL,
    evaluated_entity_type VARCHAR(64) NOT NULL,
    candidates_count INT NOT NULL DEFAULT 0,
    exempted_by_legal_hold_count INT NOT NULL DEFAULT 0,
    disposition_ready_count INT NOT NULL DEFAULT 0,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_retention_evaluation PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_eval_policy FOREIGN KEY (tenant_id, policy_id)
        REFERENCES learning_data_retention_policy (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_data_disposition_record (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    evaluation_id UUID NOT NULL,
    action_applied VARCHAR(32) NOT NULL,
    records_processed INT NOT NULL DEFAULT 0,
    cryptographic_digest VARCHAR(128) NOT NULL,
    executed_by_id UUID NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_data_disposition_record PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_disp_eval FOREIGN KEY (tenant_id, evaluation_id)
        REFERENCES learning_retention_evaluation (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_disposition_audit_log (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    disposition_record_id UUID NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_key_hash VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_disposition_audit_log PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_disp_audit_rec FOREIGN KEY (tenant_id, disposition_record_id)
        REFERENCES learning_data_disposition_record (tenant_id, id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 4. P3-VS28: ENTERPRISE CONTROL EVIDENCE & PILOT READINESS CENTER
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS learning_readiness_control (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    control_code VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL, -- SECURITY, DATA_GOVERNANCE, TESTING, RLS, FLEET
    description TEXT NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_readiness_control PRIMARY KEY (tenant_id, id),
    CONSTRAINT uq_readiness_control_code UNIQUE (tenant_id, control_code)
);

CREATE TABLE IF NOT EXISTS learning_readiness_evidence (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    control_id UUID NOT NULL,
    evidence_type VARCHAR(64) NOT NULL,
    artifact_reference VARCHAR(255) NOT NULL,
    verification_hash VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'VALID',
    recorded_by_id UUID NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_readiness_evidence PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_evidence_control FOREIGN KEY (tenant_id, control_id)
        REFERENCES learning_readiness_control (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_readiness_assessment_run (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    run_reference VARCHAR(64) NOT NULL,
    total_controls INT NOT NULL DEFAULT 0,
    passed_controls INT NOT NULL DEFAULT 0,
    failed_controls INT NOT NULL DEFAULT 0,
    overall_status VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS', -- READY, NOT_READY, BLOCKED, EXCEPTION_REQUIRED
    executed_by_id UUID NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_readiness_assessment_run PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS learning_readiness_finding (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    assessment_run_id UUID NOT NULL,
    control_id UUID NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MAJOR', -- BLOCKER, CRITICAL, MAJOR, MINOR
    finding_summary TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_readiness_finding PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_finding_run FOREIGN KEY (tenant_id, assessment_run_id)
        REFERENCES learning_readiness_assessment_run (tenant_id, id) ON DELETE CASCADE,
    CONSTRAINT fk_finding_control FOREIGN KEY (tenant_id, control_id)
        REFERENCES learning_readiness_control (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_readiness_exception (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    finding_id UUID NOT NULL,
    reason TEXT NOT NULL,
    expiry_date TIMESTAMPTZ NOT NULL,
    approved_by_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_readiness_exception PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_exception_finding FOREIGN KEY (tenant_id, finding_id)
        REFERENCES learning_readiness_finding (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_pilot_readiness_gate (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    assessment_run_id UUID NOT NULL,
    gate_verdict VARCHAR(32) NOT NULL, -- READY, NOT_READY, BLOCKED, EXCEPTION_REQUIRED
    human_attestation_summary TEXT NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_pilot_readiness_gate PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_gate_assessment FOREIGN KEY (tenant_id, assessment_run_id)
        REFERENCES learning_readiness_assessment_run (tenant_id, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_control_attestation_audit (
    tenant_id UUID NOT NULL,
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    gate_id UUID NOT NULL,
    attested_by_id UUID NOT NULL,
    attestation_role VARCHAR(64) NOT NULL,
    signature_digest VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_learning_control_attestation_audit PRIMARY KEY (tenant_id, id),
    CONSTRAINT fk_attestation_gate FOREIGN KEY (tenant_id, gate_id)
        REFERENCES learning_pilot_readiness_gate (tenant_id, id) ON DELETE CASCADE
);

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
            'CREATE POLICY tenant_isolation_policy ON %I FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
            tbl
        );
    END LOOP;
END $$;

-- Enforce append-only immutability on audit tables
REVOKE UPDATE, DELETE ON learning_privileged_action_audit FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_disposition_audit_log FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_control_attestation_audit FROM PUBLIC;
REVOKE UPDATE, DELETE ON learning_readiness_evidence FROM PUBLIC;

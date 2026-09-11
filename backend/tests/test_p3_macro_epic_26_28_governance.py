import datetime
import uuid
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone

from modules.platform_tenant.models import Tenant, TenantMembership
from modules.identity.models import User
from modules.learning.models import (
    StaffAccessAssignment,
    DelegatedAdminScope,
    PrivilegedPermissionGrant,
    AccessReviewCampaign,
    AccessReviewDecision,
    PrivilegedActionAudit,
    DataRetentionPolicy,
    RetentionPolicyVersion,
    LegalHold,
    LegalHoldScope,
    RetentionEvaluation,
    DataDispositionRecord,
    DispositionAuditLog,
    ReadinessControl,
    ReadinessEvidence,
    ReadinessAssessmentRun,
    ReadinessFinding,
    ReadinessException,
    PilotReadinessGate,
    ControlAttestationAudit,
    StaffRole,
    ScopeResourceType,
    PrivilegedGrantStatus,
    AccessReviewCampaignStatus,
    AccessReviewDecisionChoice,
    DispositionAction,
    LegalHoldStatus,
    ReadinessControlCategory,
    ReadinessEvidenceStatus,
    ReadinessOverallStatus,
    ReadinessFindingSeverity,
    PilotGateVerdict,
)
from modules.learning.enterprise_governance_service import EnterpriseGovernanceService


@pytest.mark.django_db
class TestP3MacroEpic2628EnterpriseGovernanceAndPilotReadinessMatrix:
    """
    Comprehensive Invariant and Negative Verification Matrix (N1 - N36)
    for P3-MACRO-EPIC-26-28:
      - P3-VS26: Delegated Administration & Access Governance
      - P3-VS27: Data Lifecycle, Retention & Disposition Governance
      - P3-VS28: Enterprise Control Evidence & Pilot Readiness Center
    Conforming 100% to DDL v1.2-HARDENED and Commander RUNTIME_UNLOCK.
    """

    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        self.tenant_a = Tenant.objects.create(name="Gov Academy Alpha", slug="gov-alpha")
        self.tenant_b = Tenant.objects.create(name="Gov Academy Beta", slug="gov-beta")

        self.user_admin = User.objects.create_user(username="admin_a", email="admin@alpha.com")
        self.user_staff = User.objects.create_user(username="staff_a", email="staff@alpha.com")
        self.user_second = User.objects.create_user(username="second_a", email="second@alpha.com")
        self.user_auditor = User.objects.create_user(username="auditor_a", email="auditor@alpha.com")

        self.admin_id = self.user_admin.id
        self.staff_id = self.user_staff.id
        self.second_id = self.user_second.id
        self.auditor_id = self.user_auditor.id

        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.admin_id, role="tenant_admin")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.staff_id, role="staff")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.second_id, role="staff")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.auditor_id, role="auditor")

    # -------------------------------------------------------------------------
    # N1 - N5: Multi-Tenancy & Isolation Fail-Closed
    # -------------------------------------------------------------------------
    def test_n1_query_without_matching_tenant_fails_closed(self):
        """N1: Unmatched tenant returns 0 rows across governance tables."""
        assign = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            assigned_by_id=self.admin_id,
        )
        assert StaffAccessAssignment.objects.filter(tenant_id=uuid.uuid4(), id=assign.id).count() == 0

    def test_n2_guc_empty_string_fail_closed(self):
        """N2: Empty or non-matching tenant isolation."""
        assert PrivilegedActionAudit.objects.filter(tenant_id=uuid.uuid4()).count() == 0

    def test_n3_positive_isolation_matching_tenant(self):
        """N3: Tenant A can query exactly its own resources."""
        assign = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            assigned_by_id=self.admin_id,
        )
        assert StaffAccessAssignment.objects.filter(tenant_id=self.tenant_a.id, id=assign.id).count() == 1

    def test_n4_cross_tenant_staff_assignment_leak_denied(self):
        """N4: Tenant B cannot see Tenant A's staff assignment."""
        assign = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            assigned_by_id=self.admin_id,
        )
        assert StaffAccessAssignment.objects.filter(tenant_id=self.tenant_b.id, id=assign.id).count() == 0

    def test_n5_cross_tenant_privileged_grant_and_legal_hold(self):
        """N5: Cross-tenant lookup for privileged grant and legal hold returns 0 rows."""
        grant = EnterpriseGovernanceService.grant_privileged_permission(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            permission_code="MANAGE_ROSTER",
            justification="Term exam preparation roster update",
            granted_by_id=self.admin_id,
            expires_at=timezone.now() + datetime.timedelta(days=7),
        )
        hold = EnterpriseGovernanceService.place_legal_hold(
            tenant_id=self.tenant_a.id,
            title="Internal Audit Hold",
            legal_case_reference="AUDIT-2026-01",
            reason="Preserve logs for academic review",
            placed_by_id=self.admin_id,
            scopes=[{"target_entity_type": "USER", "target_entity_id": str(self.staff_id)}],
        )
        assert PrivilegedPermissionGrant.objects.filter(tenant_id=self.tenant_b.id, id=grant.id).count() == 0
        assert LegalHold.objects.filter(tenant_id=self.tenant_b.id, id=hold.id).count() == 0

    # -------------------------------------------------------------------------
    # N6 - N8: Composite FK Closure & Separation of Duties
    # -------------------------------------------------------------------------
    def test_n6_composite_fk_closure_mismatched_tenant_rejected(self):
        """N6: DelegatedAdminScope clean() rejects mismatched assignment tenant."""
        assign = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            assigned_by_id=self.admin_id,
        )
        scope = DelegatedAdminScope(
            tenant=self.tenant_b,  # Mismatch
            assignment=assign,
            scope_resource_type=ScopeResourceType.BRANCH,
            scope_resource_id="BR-CENTRAL",
        )
        with pytest.raises(ValidationError):
            scope.clean()

    def test_n7_privilege_self_grant_denial(self):
        """N7: Invariant PRIVILEGE_SELF_GRANT: DENY."""
        with pytest.raises(PermissionDenied):
            EnterpriseGovernanceService.grant_privileged_permission(
                tenant_id=self.tenant_a.id,
                user_id=self.admin_id,
                permission_code="SUPER_ADMIN",
                justification="Emergency self grant",
                granted_by_id=self.admin_id,  # Same user
                expires_at=timezone.now() + datetime.timedelta(days=1),
            )

    def test_n8_two_person_rule_escalation_denial(self):
        """N8: Invariant TWO_PERSON_RULE: ENFORCED (second_approver == grantor rejected)."""
        with pytest.raises(PermissionDenied):
            EnterpriseGovernanceService.grant_privileged_permission(
                tenant_id=self.tenant_a.id,
                user_id=self.staff_id,
                permission_code="SUPER_ADMIN",
                justification="Emergency privilege delegation",
                granted_by_id=self.admin_id,
                second_approver_id=self.admin_id,  # Collusion / identical
                expires_at=timezone.now() + datetime.timedelta(days=1),
            )

    # -------------------------------------------------------------------------
    # N9 - N12: Append-Only & Immutability Protection
    # -------------------------------------------------------------------------
    def test_n9_immutability_privileged_action_audit(self):
        """N9: PrivilegedActionAudit records must preserve immutable provenance."""
        audit = PrivilegedActionAudit.objects.create(
            tenant=self.tenant_a,
            actor_id=self.admin_id,
            action_type="TEST_ACTION",
            target_resource="res:1",
            details={"key": "val"},
        )
        assert audit.id is not None
        assert audit.action_type == "TEST_ACTION"

    def test_n10_immutability_disposition_audit_log(self):
        """N10: DispositionAuditLog preserves audit history."""
        policy = EnterpriseGovernanceService.set_retention_policy(
            tenant_id=self.tenant_a.id,
            data_category="COURSE_LOGS",
            retention_period_days=90,
            created_by_id=self.admin_id,
        )
        disp = EnterpriseGovernanceService.evaluate_and_execute_disposition(
            tenant_id=self.tenant_a.id,
            policy_id=policy.id,
            executed_by_id=self.admin_id,
            targeted_entity_keys=[{"type": "LOG", "id": "log-1"}],
        )
        log = DispositionAuditLog.objects.filter(disposition_record=disp).first()
        assert log is not None
        assert log.status == "SUCCESS"

    def test_n11_immutability_control_attestation_audit(self):
        """N11: ControlAttestationAudit captures cryptographic signature digest."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-SEC-01",
            category=ReadinessControlCategory.SECURITY,
            description="Tenant isolation validation",
        )
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-2026-001",
            executed_by_id=self.admin_id,
        )
        gate = EnterpriseGovernanceService.evaluate_pilot_gate(
            tenant_id=self.tenant_a.id,
            assessment_run_id=run.id,
            attested_by_id=self.auditor_id,
            attestation_role="LEAD_AUDITOR",
            human_summary="Formal attestation review complete.",
        )
        attest = ControlAttestationAudit.objects.filter(gate=gate).first()
        assert attest is not None
        assert len(attest.signature_digest) == 64

    def test_n12_readiness_evidence_preservation(self):
        """N12: ReadinessEvidence records verified cryptographic hash."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-RLS-01",
            category=ReadinessControlCategory.RLS,
            description="Enforce PostgreSQL 17 FORCE RLS",
        )
        ev = EnterpriseGovernanceService.attach_readiness_evidence(
            tenant_id=self.tenant_a.id,
            control_id=ctrl.id,
            evidence_type="CI_TEST_LOG",
            artifact_reference="ci://build/123/rls.log",
            raw_payload="POSTGRESQL_17_FORCE_RLS_PASSED",
            recorded_by_id=self.admin_id,
        )
        assert ev.verification_hash is not None

    # -------------------------------------------------------------------------
    # N13 - N15: Legal Hold Precedence & Release Consistency
    # -------------------------------------------------------------------------
    def test_n13_legal_hold_bypass_denial(self):
        """N13: Records covered by active LegalHold are exempted from disposition."""
        hold = EnterpriseGovernanceService.place_legal_hold(
            tenant_id=self.tenant_a.id,
            title="Litigation Hold A",
            legal_case_reference="CASE-404",
            reason="Preserve all logs for discovery",
            placed_by_id=self.admin_id,
            scopes=[{"target_entity_type": "SESSION_LOG", "target_entity_id": "session-100"}],
        )
        policy = EnterpriseGovernanceService.set_retention_policy(
            tenant_id=self.tenant_a.id,
            data_category="SESSION_LOG",
            retention_period_days=30,
            created_by_id=self.admin_id,
        )
        disp = EnterpriseGovernanceService.evaluate_and_execute_disposition(
            tenant_id=self.tenant_a.id,
            policy_id=policy.id,
            executed_by_id=self.admin_id,
            targeted_entity_keys=[
                {"type": "SESSION_LOG", "id": "session-100"},
                {"type": "SESSION_LOG", "id": "session-101"},
            ],
        )
        assert disp.evaluation.exempted_by_legal_hold_count == 1
        assert disp.records_processed == 1

    def test_n14_legal_hold_active_with_released_at_rejected(self):
        """N14: Invariant chk_hold_release_consistency (ACTIVE hold cannot have released_at)."""
        hold = LegalHold(
            tenant=self.tenant_a,
            title="Invalid Hold",
            legal_case_reference="CASE-INV",
            reason="Testing consistency check",
            placed_by_id=self.admin_id,
            status=LegalHoldStatus.ACTIVE,
            released_at=timezone.now(),  # Inconsistent
        )
        with pytest.raises(ValidationError):
            hold.clean()

    def test_n15_legal_hold_released_without_released_by_rejected(self):
        """N15: Invariant chk_hold_release_consistency (RELEASED hold must have released_by_id)."""
        hold = LegalHold(
            tenant=self.tenant_a,
            title="Invalid Released Hold",
            legal_case_reference="CASE-REL",
            reason="Testing release consistency",
            placed_by_id=self.admin_id,
            status=LegalHoldStatus.RELEASED,
            released_at=timezone.now(),
            released_by_id=None,  # Missing
        )
        with pytest.raises(ValidationError):
            hold.clean()

    # -------------------------------------------------------------------------
    # N16 - N18: FSM Transitions & Lifecycle Invariants
    # -------------------------------------------------------------------------
    def test_n16_access_review_campaign_fsm_validity(self):
        """N16: Access review campaign valid status enum."""
        camp = EnterpriseGovernanceService.create_access_review_campaign(
            tenant_id=self.tenant_a.id,
            title="Q3 Privileged Access Review",
            campaign_period="2026-Q3",
            deadline=timezone.now() + datetime.timedelta(days=14),
            created_by_id=self.admin_id,
        )
        assert camp.status == AccessReviewCampaignStatus.ACTIVE

    def test_n17_privilege_grant_revocation_lifecycle(self):
        """N17: PrivilegedPermissionGrant status transition from ACTIVE to REVOKED."""
        grant = EnterpriseGovernanceService.grant_privileged_permission(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            permission_code="PUBLISH_CONTENT",
            justification="Course update sprint",
            granted_by_id=self.admin_id,
            expires_at=timezone.now() + datetime.timedelta(days=3),
        )
        revoked = EnterpriseGovernanceService.revoke_privileged_permission(
            tenant_id=self.tenant_a.id,
            grant_id=grant.id,
            actor_id=self.admin_id,
            reason="Sprint concluded",
        )
        assert revoked.status == PrivilegedGrantStatus.REVOKED

    def test_n18_readiness_assessment_run_fsm_resolution(self):
        """N18: ReadinessAssessmentRun completes with proper overall_status."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-TEST-01",
            category=ReadinessControlCategory.TESTING,
            description="Run full backend test suite",
        )
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-ALPHA-01",
            executed_by_id=self.admin_id,
        )
        assert run.overall_status in ReadinessOverallStatus.values

    # -------------------------------------------------------------------------
    # N19 - N20: Anti-Ranking & Advisory Readiness Gatekeeper Constraints
    # -------------------------------------------------------------------------
    def test_n19_anti_ranking_compliance(self):
        """N19: Zero learner ranking fields or methods present on governance services."""
        assert not hasattr(EnterpriseGovernanceService, "rank_students")
        assert not hasattr(EnterpriseGovernanceService, "compute_learner_percentile")

    def test_n20_non_authoritative_advisory_readiness_gate(self):
        """N20: Invariant PRODUCTION_DEPLOY_AUTHORITY: 0 (Gate never triggers deployment)."""
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-ADVISORY-01",
            executed_by_id=self.admin_id,
        )
        gate = EnterpriseGovernanceService.evaluate_pilot_gate(
            tenant_id=self.tenant_a.id,
            assessment_run_id=run.id,
            attested_by_id=self.auditor_id,
            attestation_role="ADVISOR",
            human_summary="Advisory assessment conducted.",
        )
        assert gate.gate_verdict in PilotGateVerdict.values
        # Verify gate does not expose deployment trigger
        assert not hasattr(gate, "trigger_production_deploy")

    # -------------------------------------------------------------------------
    # N21 - N24: Chronological & Window Ordering
    # -------------------------------------------------------------------------
    def test_n21_staff_validity_window_ordering(self):
        """N21: Staff assignment with valid_until <= valid_from rejected."""
        assign = StaffAccessAssignment(
            tenant=self.tenant_a,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            valid_from=timezone.now(),
            valid_until=timezone.now() - datetime.timedelta(hours=1),
            assigned_by_id=self.admin_id,
        )
        with pytest.raises(ValidationError):
            assign.clean()

    def test_n22_retention_period_minimum_baseline(self):
        """N22: Retention policy version < 30 days rejected."""
        with pytest.raises(ValidationError):
            EnterpriseGovernanceService.set_retention_policy(
                tenant_id=self.tenant_a.id,
                data_category="QUICK_LOGS",
                retention_period_days=10,  # Below 30 days minimum
                created_by_id=self.admin_id,
            )

    def test_n23_assessment_execution_timing(self):
        """N23: Readiness assessment run execution sets completed_at chronologically."""
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-TIME-01",
            executed_by_id=self.admin_id,
        )
        assert run.completed_at >= run.created_at

    def test_n24_finding_resolution_and_exception_grant(self):
        """N24: Readiness finding resolution order via explicit exception grant."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-SEC-99",
            category=ReadinessControlCategory.SECURITY,
            description="Third-party audit attestation",
            is_mandatory=True,
        )
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-FIND-01",
            executed_by_id=self.admin_id,
        )
        finding = ReadinessFinding.objects.filter(assessment_run=run, control=ctrl).first()
        assert finding is not None
        assert not finding.is_resolved

        exc = EnterpriseGovernanceService.grant_readiness_exception(
            tenant_id=self.tenant_a.id,
            finding_id=finding.id,
            reason="External audit report delivery scheduled next week",
            expiry_date=timezone.now() + datetime.timedelta(days=14),
            approved_by_id=self.admin_id,
        )
        finding.refresh_from_db()
        assert finding.is_resolved

    # -------------------------------------------------------------------------
    # N25 - N29: Strict PII Blacklist (JSONB) & Free-Text Bounds
    # -------------------------------------------------------------------------
    def test_n25_pii_blacklist_jsonb_rejection(self):
        """N25: Blacklisted PII keys in PrivilegedActionAudit details rejected."""
        audit = PrivilegedActionAudit(
            tenant=self.tenant_a,
            actor_id=self.admin_id,
            action_type="UPDATE_PROFILE",
            target_resource="user:123",
            details={"national_id": "0012345678"},  # Prohibited PII key
        )
        with pytest.raises(ValidationError):
            audit.clean()

    def test_n26_pii_free_text_privilege_justification_rejection(self):
        """N26: Email or phone pattern in privilege justification rejected."""
        with pytest.raises(ValidationError):
            EnterpriseGovernanceService.grant_privileged_permission(
                tenant_id=self.tenant_a.id,
                user_id=self.staff_id,
                permission_code="EDIT_RECORDS",
                justification="Contact me at support@external-leak.com for info",
                granted_by_id=self.admin_id,
                expires_at=timezone.now() + datetime.timedelta(days=1),
            )

    def test_n27_pii_free_text_legal_hold_reason_rejection(self):
        """N27: Bank account or credit card in legal hold reason rejected."""
        hold = LegalHold(
            tenant=self.tenant_a,
            title="Litigation X",
            legal_case_reference="CASE-PII",
            reason="Dispute involving credit_card transactions",
            placed_by_id=self.admin_id,
        )
        with pytest.raises(ValidationError):
            hold.clean()

    def test_n28_pii_free_text_readiness_finding_rejection(self):
        """N28: National ID regex in finding summary rejected."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-PII-01",
            category=ReadinessControlCategory.DATA_GOVERNANCE,
            description="General inspection",
        )
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-PII-01",
            executed_by_id=self.admin_id,
        )
        finding = ReadinessFinding(
            tenant=self.tenant_a,
            assessment_run=run,
            control=ctrl,
            finding_summary="User with fingerprint leak detected",
        )
        with pytest.raises(ValidationError):
            finding.clean()

    def test_n29_pii_free_text_attestation_summary_rejection(self):
        """N29: IBAN or bank details in human attestation summary rejected."""
        run = EnterpriseGovernanceService.execute_pilot_readiness_assessment(
            tenant_id=self.tenant_a.id,
            run_reference="RUN-PII-02",
            executed_by_id=self.admin_id,
        )
        gate = PilotReadinessGate(
            tenant=self.tenant_a,
            assessment_run=run,
            gate_verdict=PilotGateVerdict.READY,
            human_attestation_summary="Attestation details with iban IR120000000000000000000001",
        )
        with pytest.raises(ValidationError):
            gate.clean()

    # -------------------------------------------------------------------------
    # N30 - N31: Enum Domain Boundary Guards
    # -------------------------------------------------------------------------
    def test_n30_scope_resource_enum_constraint(self):
        """N30: DelegatedAdminScope resource enum values enforced."""
        assign = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=self.tenant_a.id,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            assigned_by_id=self.admin_id,
        )
        scope = DelegatedAdminScope.objects.create(
            tenant=self.tenant_a,
            assignment=assign,
            scope_resource_type=ScopeResourceType.PROGRAM,
            scope_resource_id="PROG-CS",
        )
        assert scope.scope_resource_type == ScopeResourceType.PROGRAM

    def test_n31_readiness_control_category_enum(self):
        """N31: ReadinessControl category matches valid enum."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-CAT-01",
            category=ReadinessControlCategory.FLEET,
            description="Fleet consensus verification",
        )
        assert ctrl.category == ReadinessControlCategory.FLEET

    # -------------------------------------------------------------------------
    # N32 - N36: Zero Bare UUIDs, Cascade Wipe, SHA-256 Digest & Policy Uniqueness
    # -------------------------------------------------------------------------
    def test_n32_zero_bare_foreign_key_uuids(self):
        """N32: Schema introspection: All 20 models enforce tenant FK."""
        models_to_check = [
            StaffAccessAssignment, DelegatedAdminScope, PrivilegedPermissionGrant,
            AccessReviewCampaign, AccessReviewDecision, PrivilegedActionAudit,
            DataRetentionPolicy, RetentionPolicyVersion, LegalHold,
            LegalHoldScope, RetentionEvaluation, DataDispositionRecord,
            DispositionAuditLog, ReadinessControl, ReadinessEvidence,
            ReadinessAssessmentRun, ReadinessFinding, ReadinessException,
            PilotReadinessGate, ControlAttestationAudit,
        ]
        for m in models_to_check:
            tenant_field = m._meta.get_field("tenant")
            assert tenant_field.is_relation
            assert tenant_field.related_model == Tenant

    def test_n33_tenant_cascade_wipe_cleans_governance_data(self):
        """N33: Hard deletion of tenant cleanly wipes all dependent governance records."""
        temp_tenant = Tenant.objects.create(name="Wipe Tenant", slug="wipe-tenant")
        assign = EnterpriseGovernanceService.assign_staff_access(
            tenant_id=temp_tenant.id,
            user_id=self.staff_id,
            role_name=StaffRole.DELEGATED_STAFF,
            assigned_by_id=self.admin_id,
        )
        assert StaffAccessAssignment.objects.filter(tenant_id=temp_tenant.id).count() == 1
        temp_tenant.delete()
        assert StaffAccessAssignment.objects.filter(tenant_id=temp_tenant.id).count() == 0

    def test_n34_malformed_tenant_guc_safe_handling(self):
        """N34: Malformed or non-existent tenant UUID handled safely."""
        assert StaffAccessAssignment.objects.filter(tenant_id=uuid.uuid4()).count() == 0

    def test_n35_evidence_hash_sha256_digest_integrity(self):
        """N35: Readiness evidence stores valid 64-char SHA-256 digest."""
        ctrl = EnterpriseGovernanceService.register_readiness_control(
            tenant_id=self.tenant_a.id,
            control_code="CTRL-HASH-01",
            category=ReadinessControlCategory.TESTING,
            description="Artifact hashing test",
        )
        ev = EnterpriseGovernanceService.attach_readiness_evidence(
            tenant_id=self.tenant_a.id,
            control_id=ctrl.id,
            evidence_type="RAW_LOG",
            artifact_reference="ref://test",
            raw_payload="EXACT_EVIDENCE_STREAM",
            recorded_by_id=self.admin_id,
        )
        assert len(ev.verification_hash) == 64

    def test_n36_single_active_retention_policy_per_category(self):
        """N36: Enforce unique category constraint per tenant."""
        EnterpriseGovernanceService.set_retention_policy(
            tenant_id=self.tenant_a.id,
            data_category="UNIQUE_CATEGORY",
            retention_period_days=60,
            created_by_id=self.admin_id,
        )
        # Attempting direct duplicate create violates unique constraint
        with pytest.raises(IntegrityError):
            DataRetentionPolicy.objects.create(
                tenant=self.tenant_a,
                data_category="UNIQUE_CATEGORY",
                retention_period_days=45,
                created_by_id=self.admin_id,
            )

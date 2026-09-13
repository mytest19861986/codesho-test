import uuid
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from modules.platform_tenant.models import Tenant
from modules.identity.models import User
from modules.learning.models import (
    ReleaseCandidate,
    ReleaseCandidateState,
    IncidentRecord,
    IncidentSeverity,
    IncidentState,
    PilotTenantProvisioningPlan,
)


@pytest.mark.django_db
class TestPhase4ControlledPilotPreparationNegativeMatrix:
    """
    Comprehensive Invariant and Negative Verification Matrix (N4-01 - N4-16)
    for Phase 4: Controlled Pilot Preparation & Operational Readiness.
    Authoritative against COMMANDER_P4_UNLOCK_DIRECTIVE.
    """

    @pytest.fixture(autouse=True)
    def setup_p4_data(self):
        self.tenant_a = Tenant.objects.create(name="Pilot School Alpha", slug="pilot-alpha")
        self.tenant_b = Tenant.objects.create(name="Pilot School Beta", slug="pilot-beta")
        self.operator_user = User.objects.create(
            username="platform_operator_1",
            email="operator1@synthetic.codesho.local",
            is_staff=True,
        )
        self.peer_operator = User.objects.create(
            username="platform_operator_2",
            email="operator2@synthetic.codesho.local",
            is_staff=True,
        )

    # -------------------------------------------------------------------------
    # N4-01: Zero Automated Production Deploy (PRODUCTION_DEPLOY_AUTHORITY: 0)
    # -------------------------------------------------------------------------
    def test_n4_01_production_deploy_target_strictly_denied(self):
        rc = ReleaseCandidate(
            tenant=self.tenant_a,
            version_tag="v4.0.0-rc1",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.DRAFT,
            is_production_target=True,  # Prohibited
            created_by_id=self.operator_user.id,
        )
        with pytest.raises(ValidationError, match="PRODUCTION_DEPLOY_AUTHORITY: 0"):
            rc.clean()

    # -------------------------------------------------------------------------
    # N4-02: Dual-Custody Approval Required for Pilot Deployment
    # -------------------------------------------------------------------------
    def test_n4_02_pilot_deploy_without_dual_custody_denied(self):
        rc = ReleaseCandidate(
            tenant=self.tenant_a,
            version_tag="v4.0.0-rc2",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.PILOT_DEPLOYED,
            has_dual_custody_approval=False,  # Lacks peer signature
            created_by_id=self.operator_user.id,
        )
        with pytest.raises(ValidationError, match="Dual-custody approval is strictly required"):
            rc.clean()

    # -------------------------------------------------------------------------
    # N4-03: PII Scrubbing in Incident Summary (REAL_CHILD_DATA: 0)
    # -------------------------------------------------------------------------
    def test_n4_03_incident_summary_rejects_real_email_pii(self):
        incident = IncidentRecord(
            tenant=self.tenant_a,
            incident_number="INC-2026-001",
            severity=IncidentSeverity.SEV2,
            state=IncidentState.DETECTED,
            summary="Error observed for student user real.child@gmail.com on dashboard",
        )
        with pytest.raises(ValidationError, match="PII"):
            incident.clean()

    # -------------------------------------------------------------------------
    # N4-04: PII Scrubbing in Post-Incident Review (PIR)
    # -------------------------------------------------------------------------
    def test_n4_04_incident_postmortem_rejects_real_phone_pii(self):
        incident = IncidentRecord(
            tenant=self.tenant_a,
            incident_number="INC-2026-002",
            severity=IncidentSeverity.SEV1,
            state=IncidentState.RESOLVED,
            summary="Synthetic outage mitigated by runbook R-04",
            post_incident_review="Parent contacted at +989121234567 during triage",
        )
        with pytest.raises(ValidationError, match="PII"):
            incident.clean()

    # -------------------------------------------------------------------------
    # N4-05: Synthetic-Only Provisioning Boundary (REAL_PILOT_ACTIVATION: 0)
    # -------------------------------------------------------------------------
    def test_n4_05_pilot_provisioning_plan_rejects_non_synthetic_mode(self):
        plan = PilotTenantProvisioningPlan(
            tenant=self.tenant_a,
            plan_code="PLAN-ALPHA-01",
            organization_name="Real High School #12",
            is_synthetic_only=False,  # Prohibited
        )
        with pytest.raises(ValidationError, match="REAL_PILOT_ACTIVATION: 0"):
            plan.clean()

    # -------------------------------------------------------------------------
    # N4-06: Tenant Isolation for Release Candidates (No Cross-Tenant Collision)
    # -------------------------------------------------------------------------
    def test_n4_06_release_candidate_tenant_isolation_enforced(self):
        rc_a = ReleaseCandidate.objects.create(
            tenant=self.tenant_a,
            version_tag="v4.0.0-rc-common",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.DRAFT,
            created_by_id=self.operator_user.id,
        )
        # Same version tag in different tenant must succeed
        rc_b = ReleaseCandidate.objects.create(
            tenant=self.tenant_b,
            version_tag="v4.0.0-rc-common",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.DRAFT,
            created_by_id=self.operator_user.id,
        )
        assert rc_a.id != rc_b.id
        assert rc_a.tenant_id != rc_b.tenant_id

    # -------------------------------------------------------------------------
    # N4-07: Unique Version Tag per Tenant
    # -------------------------------------------------------------------------
    def test_n4_07_duplicate_version_tag_within_same_tenant_fails(self):
        ReleaseCandidate.objects.create(
            tenant=self.tenant_a,
            version_tag="v4.0.0-unique",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.DRAFT,
            created_by_id=self.operator_user.id,
        )
        with pytest.raises(IntegrityError):
            ReleaseCandidate.objects.create(
                tenant=self.tenant_a,
                version_tag="v4.0.0-unique",
                commit_sha="a6bc0d9",
                state=ReleaseCandidateState.DRAFT,
                created_by_id=self.operator_user.id,
            )

    # -------------------------------------------------------------------------
    # N4-08: Unique Incident Number per Tenant
    # -------------------------------------------------------------------------
    def test_n4_08_duplicate_incident_number_within_same_tenant_fails(self):
        IncidentRecord.objects.create(
            tenant=self.tenant_a,
            incident_number="INC-UNIQUE-01",
            severity=IncidentSeverity.SEV3,
            state=IncidentState.DETECTED,
            summary="Synthetic test incident A",
        )
        with pytest.raises(IntegrityError):
            IncidentRecord.objects.create(
                tenant=self.tenant_a,
                incident_number="INC-UNIQUE-01",
                severity=IncidentSeverity.SEV3,
                state=IncidentState.DETECTED,
                summary="Synthetic test incident B",
            )

    # -------------------------------------------------------------------------
    # N4-09: Valid Incident Severity Choices
    # -------------------------------------------------------------------------
    def test_n4_09_invalid_incident_severity_rejected(self):
        with pytest.raises(ValidationError):
            inc = IncidentRecord(
                tenant=self.tenant_a,
                incident_number="INC-INVALID-SEV",
                severity="SEV99",
                summary="Valid synthetic summary",
            )
            inc.full_clean()

    # -------------------------------------------------------------------------
    # N4-10: Valid Release Candidate State Choices
    # -------------------------------------------------------------------------
    def test_n4_10_invalid_rc_state_rejected(self):
        with pytest.raises(ValidationError):
            rc = ReleaseCandidate(
                tenant=self.tenant_a,
                version_tag="v4.0.0-bad-state",
                commit_sha="a6bc0d9",
                state="PROD_DEPLOYED",  # Invalid
                created_by_id=self.operator_user.id,
            )
            rc.full_clean()

    # -------------------------------------------------------------------------
    # N4-11: Dual-Custody Transition Lifecycle
    # -------------------------------------------------------------------------
    def test_n4_11_valid_pilot_deploy_with_dual_custody_succeeds(self):
        rc = ReleaseCandidate(
            tenant=self.tenant_a,
            version_tag="v4.0.0-rc-approved",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.PILOT_DEPLOYED,
            has_dual_custody_approval=True,
            created_by_id=self.operator_user.id,
            approved_by_id=self.peer_operator.id,
        )
        rc.full_clean()
        rc.save()
        assert rc.state == ReleaseCandidateState.PILOT_DEPLOYED
        assert rc.has_dual_custody_approval is True

    # -------------------------------------------------------------------------
    # N4-12: Rollback State Transition Support
    # -------------------------------------------------------------------------
    def test_n4_12_rollback_state_transition_valid(self):
        rc = ReleaseCandidate.objects.create(
            tenant=self.tenant_a,
            version_tag="v4.0.0-rc-rollback",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.PILOT_DEPLOYED,
            has_dual_custody_approval=True,
            created_by_id=self.operator_user.id,
            approved_by_id=self.peer_operator.id,
        )
        rc.state = ReleaseCandidateState.ROLLED_BACK
        rc.full_clean()
        rc.save()
        assert rc.state == ReleaseCandidateState.ROLLED_BACK

    # -------------------------------------------------------------------------
    # N4-13: Synthetic Provisioning Clean Save
    # -------------------------------------------------------------------------
    def test_n4_13_synthetic_provisioning_plan_succeeds(self):
        plan = PilotTenantProvisioningPlan(
            tenant=self.tenant_a,
            plan_code="PLAN-SYNTH-01",
            organization_name="Synthetic Cohort Alpha",
            is_synthetic_only=True,
        )
        plan.full_clean()
        plan.save()
        assert plan.is_synthetic_only is True

    # -------------------------------------------------------------------------
    # N4-14: Incident Lifecycle FSM Progression
    # -------------------------------------------------------------------------
    def test_n4_14_incident_lifecycle_fsm_progression(self):
        inc = IncidentRecord.objects.create(
            tenant=self.tenant_a,
            incident_number="INC-2026-FSM",
            severity=IncidentSeverity.SEV2,
            state=IncidentState.DETECTED,
            summary="Worker delay detected on synthetic queue",
        )
        inc.state = IncidentState.TRIAGED
        inc.full_clean()
        inc.save()

        inc.state = IncidentState.INVESTIGATING
        inc.assigned_operator_id = self.operator_user.id
        inc.full_clean()
        inc.save()

        inc.state = IncidentState.MITIGATED
        inc.full_clean()
        inc.save()

        inc.state = IncidentState.RESOLVED
        inc.post_incident_review = "Mitigated by scaling synthetic worker pool"
        inc.full_clean()
        inc.save()

        assert inc.state == IncidentState.RESOLVED

    # -------------------------------------------------------------------------
    # N4-15: Release Candidate Abort Transition
    # -------------------------------------------------------------------------
    def test_n4_15_release_candidate_abort_transition(self):
        rc = ReleaseCandidate.objects.create(
            tenant=self.tenant_a,
            version_tag="v4.0.0-rc-abort",
            commit_sha="a6bc0d9",
            state=ReleaseCandidateState.CANDIDATE_TAGGED,
            created_by_id=self.operator_user.id,
        )
        rc.state = ReleaseCandidateState.ABORTED
        rc.full_clean()
        rc.save()
        assert rc.state == ReleaseCandidateState.ABORTED

    # -------------------------------------------------------------------------
    # N4-16: Student Anti-Ranking Policy Guarantee (STUDENT_RANKING: 0)
    # -------------------------------------------------------------------------
    def test_n4_16_anti_ranking_invariant_guaranteed(self):
        # Ensure Phase 4 telemetry and release metadata contains zero competitive ranking keys
        disallowed_ranking_tokens = [
            "leaderboard",
            "student_rank",
            "class_rank",
            "top_students",
            "percentile_rank",
            "competitive_score",
        ]
        # Inspect model field names across Phase 4 models
        p4_models = [ReleaseCandidate, IncidentRecord, PilotTenantProvisioningPlan]
        for model in p4_models:
            field_names = [f.name.lower() for f in model._meta.get_fields()]
            for disallowed in disallowed_ranking_tokens:
                assert disallowed not in field_names, f"Model {model.__name__} violates STUDENT_RANKING: 0 with field {disallowed}"

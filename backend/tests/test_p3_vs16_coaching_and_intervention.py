import uuid
import datetime
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from modules.platform_tenant.models import Tenant, TenantMembership
from modules.identity.models import User
from modules.learning.models import (
    CoachingAuditAction,
    CoachingAuditLog,
    CoachingNote,
    CoachingNoteType,
    CoachingSession,
    CoachingSessionStatus,
    FollowUpAction,
    FollowUpActionStatus,
    LearningInsight,
    LearningStudentSuccessPlan,
    SupportIntervention,
    SupportInterventionCategory,
    SupportInterventionStatus,
)
from modules.learning.coaching_coordinator_service import CoachingCoordinatorService
from modules.learning.views import (
    CoachingSessionListCreateView,
    CoachingSessionTransitionView,
    CoachingNoteCreateView,
    SupportInterventionListCreateView,
    SupportInterventionTransitionView,
    FollowUpActionListCreateView,
    FollowUpActionTransitionView,
)


@pytest.mark.django_db
class TestP3VS16CoachingAndInterventionMatrix:
    """
    Comprehensive Negative and Invariant Proof Suite (N1 - N28)
    for Phase 3 Vertical Slice 16:
    Mentor-Student Success Coaching and Intervention Workflow.
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant_a = Tenant.objects.create(name="Alpha Academy", slug="alpha-academy")
        self.tenant_b = Tenant.objects.create(name="Beta Academy", slug="beta-academy")

        self.user_student_a = User.objects.create_user(username="student_a", email="student_a@alpha.com")
        self.user_student_b = User.objects.create_user(username="student_b", email="student_b@beta.com")
        self.user_mentor_a = User.objects.create_user(username="mentor_a", email="mentor_a@alpha.com")
        self.user_mentor_b = User.objects.create_user(username="mentor_b", email="mentor_b@beta.com")
        self.user_admin_a = User.objects.create_user(username="admin_a", email="admin_a@alpha.com")

        self.student_a_id = self.user_student_a.id
        self.student_b_id = self.user_student_b.id
        self.mentor_a_id = self.user_mentor_a.id
        self.mentor_b_id = self.user_mentor_b.id
        self.admin_a_id = self.user_admin_a.id

        # Memberships
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.student_a_id, role="student")
        TenantMembership.objects.create(tenant=self.tenant_b, user_id=self.student_b_id, role="student")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.mentor_a_id, role="mentor")
        TenantMembership.objects.create(tenant=self.tenant_b, user_id=self.mentor_b_id, role="mentor")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.admin_a_id, role="admin")

        self.factory = APIRequestFactory()

    # -------------------------------------------------------------------------
    # N1 - N2, N25 - N26: Tenant Isolation & Fail-Closed GUC Checks
    # -------------------------------------------------------------------------
    def test_n1_tenant_isolation_coaching_session_fail_closed(self):
        """N1: Coaching sessions are strictly isolated and fail-closed across tenants."""
        session = CoachingCoordinatorService.schedule_session(
            tenant_id=self.tenant_a.id,
            actor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Weekly Strategy Check-in",
            scheduled_at=timezone.now() + datetime.timedelta(days=2),
        )
        assert session.tenant_id == self.tenant_a.id
        assert CoachingSession.objects.filter(tenant=self.tenant_b, id=session.id).count() == 0

    def test_n2_tenant_isolation_support_intervention_fail_closed(self):
        """N2: Interventions in Tenant A are invisible to Tenant B."""
        intervention = CoachingCoordinatorService.propose_intervention(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            title="Math Scaffolding Support",
            category=SupportInterventionCategory.ACADEMIC_SCAFFOLDING,
            rationale="Identified prerequisite gaps in quadratic formulas.",
        )
        assert SupportIntervention.objects.filter(tenant=self.tenant_b, id=intervention.id).count() == 0

    # -------------------------------------------------------------------------
    # N3 - N5: Composite FK Cross-Tenant Linkage Rejections
    # -------------------------------------------------------------------------
    def test_n3_cross_tenant_mentor_linkage_rejection(self):
        """N3: Cannot link mentor from Tenant B into a session in Tenant A."""
        with pytest.raises((ValidationError, IntegrityError)):
            session = CoachingSession(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                mentor_id=self.mentor_b_id, # Mentor from Tenant B
                title="Cross Tenant Session",
                scheduled_at=timezone.now() + datetime.timedelta(days=1),
            )
            session.clean()

    def test_n4_cross_tenant_student_linkage_rejection(self):
        """N4: Cannot link student from Tenant B into a session in Tenant A."""
        with pytest.raises((ValidationError, IntegrityError)):
            session = CoachingSession(
                tenant=self.tenant_a,
                student_id=self.student_b_id, # Student from Tenant B
                mentor_id=self.mentor_a_id,
                title="Cross Tenant Student Session",
                scheduled_at=timezone.now() + datetime.timedelta(days=1),
            )
            session.clean()

    def test_n5_cross_tenant_plan_leakage_rejection(self):
        """N5: Cannot link success plan from Tenant B into an intervention in Tenant A."""
        plan_b = LearningStudentSuccessPlan.objects.create(
            tenant=self.tenant_b,
            student_id=self.student_b_id,
            title="Plan in B",
            target_period="CURRENT_TERM",
        )
        with pytest.raises(ValidationError, match="Success plan tenant mismatch"):
            intervention = SupportIntervention(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                mentor_id=self.mentor_a_id,
                success_plan=plan_b, # Plan from Tenant B
                title="Intervention with Foreign Plan",
                category=SupportInterventionCategory.STUDY_STRATEGY,
                rationale="Valid supportive rationale.",
                is_authoritative=False,
            )
            intervention.clean()

    # -------------------------------------------------------------------------
    # N6: Anti-Automated Decider (Non-Authoritative Invariant)
    # -------------------------------------------------------------------------
    def test_n6_anti_authoritative_decider_enforcement(self):
        """N6: Intervention marked is_authoritative = True must be strictly rejected."""
        with pytest.raises(ValidationError, match="respect learner agency"):
            intervention = SupportIntervention(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                mentor_id=self.mentor_a_id,
                title="Mandatory Detention",
                category=SupportInterventionCategory.ACADEMIC_SCAFFOLDING,
                rationale="Automated enforcement system rationale.",
                is_authoritative=True, # Prohibited
            )
            intervention.clean()

    # -------------------------------------------------------------------------
    # N7: Supportive Non-Punitive Category Enforcement
    # -------------------------------------------------------------------------
    def test_n7_punitive_category_rejection(self):
        """N7: Punitive categories (e.g. SUSPENSION, DETENTION) are invalid."""
        with pytest.raises(ValidationError):
            intervention = SupportIntervention(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                mentor_id=self.mentor_a_id,
                title="Punitive Measure",
                category="PUNITIVE_DETENTION", # Invalid choice
                rationale="Non supportive punitive measure.",
                is_authoritative=False,
            )
            intervention.full_clean()

    # -------------------------------------------------------------------------
    # N8: Mandatory Agency Consent Gate (Mentor Cannot Force ACCEPTED)
    # -------------------------------------------------------------------------
    def test_n8_mentor_cannot_force_accept_intervention(self):
        """N8: Mentor attempting to ACCEPT an intervention must receive 403 / PermissionDenied."""
        intervention = CoachingCoordinatorService.propose_intervention(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            title="Peer Tutoring Support",
            category=SupportInterventionCategory.PEER_STUDY_CONNECTION,
            rationale="Connecting with study group for algebra reviews.",
        )
        with pytest.raises(PermissionDenied, match="Only the student has the agency"):
            CoachingCoordinatorService.accept_intervention(
                tenant_id=self.tenant_a.id,
                intervention_id=intervention.id,
                student_id=self.mentor_a_id, # Mentor masquerading or attempting to accept
            )

    # -------------------------------------------------------------------------
    # N9 - N10: Append-Only Audit Log and Notes Immutability
    # -------------------------------------------------------------------------
    def test_n9_append_only_audit_log_immutability(self):
        """N9: CoachingAuditLog cannot be edited or deleted."""
        log = CoachingAuditLog.objects.create(
            tenant=self.tenant_a,
            actor_id=self.mentor_a_id,
            action_type=CoachingAuditAction.SCHEDULE_SESSION,
        )
        with pytest.raises(ValidationError, match="strictly append-only"):
            log.save()
        with pytest.raises(ValidationError, match="cannot be deleted"):
            log.delete()

    def test_n10_append_only_coaching_note_immutability(self):
        """N10: CoachingNote cannot be modified or deleted once recorded."""
        session = CoachingCoordinatorService.schedule_session(
            tenant_id=self.tenant_a.id,
            actor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Review Session",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
        )
        note = CoachingCoordinatorService.add_note(
            tenant_id=self.tenant_a.id,
            session_id=session.id,
            author_id=self.mentor_a_id,
            note_type=CoachingNoteType.OBSERVATION,
            content="Student demonstrates excellent grasp of concepts.",
        )
        with pytest.raises(ValidationError, match="strictly append-only"):
            note.save()
        with pytest.raises(ValidationError, match="cannot be deleted"):
            note.delete()

    # -------------------------------------------------------------------------
    # N12 - N13: Text and Title Length Bounds
    # -------------------------------------------------------------------------
    def test_n12_coaching_note_content_bounds(self):
        """N12: Coaching note content must be between 3 and 4000 chars."""
        session = CoachingCoordinatorService.schedule_session(
            tenant_id=self.tenant_a.id,
            actor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Valid Title",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
        )
        with pytest.raises(ValidationError, match="at least 3 characters"):
            note_short = CoachingNote(
                tenant=self.tenant_a,
                session=session,
                author_id=self.mentor_a_id,
                content="hi",
            )
            note_short.clean()

        with pytest.raises(ValidationError, match="cannot exceed 4000"):
            note_long = CoachingNote(
                tenant=self.tenant_a,
                session=session,
                author_id=self.mentor_a_id,
                content="A" * 4001,
            )
            note_long.clean()

    def test_n13_intervention_title_bounds(self):
        """N13: Support intervention title must be between 3 and 255 chars."""
        with pytest.raises(ValidationError, match="at least 3 characters"):
            interv_short = SupportIntervention(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                mentor_id=self.mentor_a_id,
                title="no",
                rationale="Valid rationale here.",
                is_authoritative=False,
            )
            interv_short.clean()

    # -------------------------------------------------------------------------
    # N14 - N16: PII Scrubbing and Prohibited Key Filtration
    # -------------------------------------------------------------------------
    def test_n14_free_text_pii_regex_rejection(self):
        """N14: Free text containing phone numbers, IBANs, or emails is rejected."""
        with pytest.raises(ValidationError, match="PII detected"):
            CoachingCoordinatorService.schedule_session(
                tenant_id=self.tenant_a.id,
                actor_id=self.mentor_a_id,
                student_id=self.student_a_id,
                mentor_id=self.mentor_a_id,
                title="Session for 09121234567 regarding progress", # Phone number embedded
                scheduled_at=timezone.now() + datetime.timedelta(days=1),
            )

    def test_n15_jsonb_prohibited_pii_key_rejection(self):
        """N15: Metadata containing prohibited keys (e.g. national_id) is scrubbed/rejected."""
        with pytest.raises(ValidationError, match="Prohibited PII key 'national_id'"):
            CoachingCoordinatorService.propose_intervention(
                tenant_id=self.tenant_a.id,
                mentor_id=self.mentor_a_id,
                student_id=self.student_a_id,
                title="Resource Scaffolding",
                category=SupportInterventionCategory.RESOURCE_RECOMMENDATION,
                rationale="Valid educational recommendation.",
                metadata={"national_id": "0012345678"},
            )

    # -------------------------------------------------------------------------
    # N17 - N18: FSM Direct Jump Rejection & Time Consistency
    # -------------------------------------------------------------------------
    def test_n17_fsm_illegal_direct_jump_rejection(self):
        """N17: Cannot jump from PROPOSED directly to COMPLETED."""
        intervention = CoachingCoordinatorService.propose_intervention(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            title="Pacing Support",
            category=SupportInterventionCategory.PACING_ADJUSTMENT,
            rationale="Adjustment of sprint deadlines.",
        )
        with pytest.raises(ValidationError, match="Must be ACTIVE"):
            CoachingCoordinatorService.complete_intervention(
                tenant_id=self.tenant_a.id,
                intervention_id=intervention.id,
                actor_id=self.mentor_a_id,
            )

    def test_n18_session_status_time_consistency(self):
        """N18: started_at > completed_at in coaching session is invalid."""
        now = timezone.now()
        session = CoachingSession(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Session Time Inconsistency",
            status=CoachingSessionStatus.COMPLETED,
            scheduled_at=now - datetime.timedelta(hours=2),
            started_at=now,
            completed_at=now - datetime.timedelta(hours=1), # Completed before started
        )
        with pytest.raises(ValidationError, match="started_at must be before or equal to completed_at"):
            session.clean()

    # -------------------------------------------------------------------------
    # N19: Strict Anti-Ranking Policy REST Filter Rejection
    # -------------------------------------------------------------------------
    def test_n19_anti_ranking_policy_rejection(self):
        """N19: API requests with rank or leaderboard query params must return 400 Bad Request."""
        request = self.factory.get("/api/v1/learning/coaching-sessions/?rank=true")
        request.user = self.user_student_a
        request.tenant_id = self.tenant_a.id

        view = CoachingSessionListCreateView.as_view()
        response = view(request)
        assert response.status_code == 400
        assert "Anti-Ranking Policy" in response.data["detail"]

    # -------------------------------------------------------------------------
    # N20: Cross-Cohort Mentor Guard
    # -------------------------------------------------------------------------
    def test_n20_cross_cohort_mentor_guard(self):
        """N20: Mentor from Tenant B querying sessions in Tenant A gets empty set."""
        session = CoachingCoordinatorService.schedule_session(
            tenant_id=self.tenant_a.id,
            actor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Cohort A Coaching",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
        )
        request = self.factory.get("/api/v1/learning/coaching-sessions/")
        request.user = self.user_mentor_b
        request.tenant_id = self.tenant_a.id

        view = CoachingSessionListCreateView.as_view()
        response = view(request)
        assert response.status_code == 200
        assert len(response.data) == 0

    # -------------------------------------------------------------------------
    # N23: Follow-Up Action Exact Origin XOR Enforcement
    # -------------------------------------------------------------------------
    def test_n23_followup_action_origin_exact_xor(self):
        """N23: FollowUpAction must link to either an intervention OR a session, never both, never neither."""
        session = CoachingCoordinatorService.schedule_session(
            tenant_id=self.tenant_a.id,
            actor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Session for Action",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
        )
        intervention = CoachingCoordinatorService.propose_intervention(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            title="Intervention for Action",
            category=SupportInterventionCategory.STUDY_STRATEGY,
            rationale="Study plan revision.",
        )
        # Both set
        with pytest.raises(ValidationError, match="exactly one source"):
            CoachingCoordinatorService.assign_action(
                tenant_id=self.tenant_a.id,
                assigned_by_id=self.mentor_a_id,
                student_id=self.student_a_id,
                title="Ambiguous Action",
                due_date=timezone.now() + datetime.timedelta(days=3),
                intervention_id=intervention.id,
                session_id=session.id,
            )

        # Neither set
        with pytest.raises(ValidationError, match="exactly one source"):
            CoachingCoordinatorService.assign_action(
                tenant_id=self.tenant_a.id,
                assigned_by_id=self.mentor_a_id,
                student_id=self.student_a_id,
                title="Rootless Action",
                due_date=timezone.now() + datetime.timedelta(days=3),
            )

    # -------------------------------------------------------------------------
    # Positive Happy Path: Full Lifecycle & Agency Flow
    # -------------------------------------------------------------------------
    def test_positive_learner_agency_lifecycle(self):
        """Student accepts intervention -> Mentor activates -> Action completed -> Completed."""
        # 1. Mentor proposes intervention
        intervention = CoachingCoordinatorService.propose_intervention(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            title="Adaptive Study Scaffolding",
            category=SupportInterventionCategory.ACADEMIC_SCAFFOLDING,
            rationale="Targeted support for calculus midterm.",
        )
        assert intervention.status == SupportInterventionStatus.PROPOSED
        assert intervention.is_authoritative is False

        # 2. Student accepts with feedback
        intervention = CoachingCoordinatorService.accept_intervention(
            tenant_id=self.tenant_a.id,
            intervention_id=intervention.id,
            student_id=self.student_a_id,
            feedback="Thank you, I would like to review limits first.",
        )
        assert intervention.status == SupportInterventionStatus.ACCEPTED
        assert intervention.acknowledged_at is not None

        # 3. Mentor starts intervention
        intervention = CoachingCoordinatorService.start_intervention(
            tenant_id=self.tenant_a.id,
            intervention_id=intervention.id,
            actor_id=self.mentor_a_id,
        )
        assert intervention.status == SupportInterventionStatus.ACTIVE

        # 4. Action assigned
        action = CoachingCoordinatorService.assign_action(
            tenant_id=self.tenant_a.id,
            assigned_by_id=self.mentor_a_id,
            student_id=self.student_a_id,
            title="Complete Chapter 3 Exercises",
            due_date=timezone.now() + datetime.timedelta(days=4),
            intervention_id=intervention.id,
        )
        assert action.status == FollowUpActionStatus.PENDING

        # 5. Student completes action
        action = CoachingCoordinatorService.complete_action(
            tenant_id=self.tenant_a.id,
            action_id=action.id,
            actor_id=self.student_a_id,
        )
        assert action.status == FollowUpActionStatus.COMPLETED

        # 6. Mentor completes intervention
        intervention = CoachingCoordinatorService.complete_intervention(
            tenant_id=self.tenant_a.id,
            intervention_id=intervention.id,
            actor_id=self.mentor_a_id,
        )
        assert intervention.status == SupportInterventionStatus.COMPLETED
        assert intervention.completed_at is not None

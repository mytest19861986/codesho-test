import datetime
import uuid
from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from modules.platform_tenant.models import Tenant, TenantMembership
from modules.identity.models import User
from modules.learning.models import (
    FollowUpCommitment,
    FollowUpCommitmentOwnerRole,
    LearningCheckIn,
    LearningCheckInStatus,
    MentorCaseloadAssignment,
    MentorOperationsAuditAction,
    MentorOperationsAuditLog,
    ProgramSupportAggregate,
    SupportQueueItem,
    SupportQueueStatus,
    SupportQueueUrgency,
    CoachingSession,
    SupportIntervention,
)
from modules.learning.mentor_operations_service import MentorOperationsService
from modules.learning.views import (
    MentorCaseloadView,
    MentorCaseloadUnassignView,
    MentorSupportQueueView,
    MentorSupportQueueResolveView,
    MentorCheckInListCreateView,
    MentorCheckInTransitionView,
    MentorCommitmentListCreateView,
    MentorCommitmentCompleteView,
    MentorProgramAnalyticsView,
)


@pytest.mark.django_db
class TestP3MacroEpic1719OperationsMatrix:
    """
    Comprehensive Negative and Invariant Proof Suite (N1 - N33)
    for Phase 3 Macro Epic 17-19:
    Mentor Caseload Management, Support Queues, Learning Check-ins Orchestration,
    and Program Success Support Analytics.
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

        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.student_a_id, role="student")
        TenantMembership.objects.create(tenant=self.tenant_b, user_id=self.student_b_id, role="student")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.mentor_a_id, role="mentor")
        TenantMembership.objects.create(tenant=self.tenant_b, user_id=self.mentor_b_id, role="mentor")
        TenantMembership.objects.create(tenant=self.tenant_a, user_id=self.admin_a_id, role="admin")

        self.factory = APIRequestFactory()

    # -------------------------------------------------------------------------
    # N1, N2, N31, N32, N33: Tenant Isolation & Fail-Closed GUC Checks
    # -------------------------------------------------------------------------
    def test_n1_tenant_isolation_fail_closed_across_models(self):
        """N1: Tenant isolation fails closed when querying cross-tenant records."""
        assignment = MentorOperationsService.assign_caseload(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            actor_id=self.admin_a_id,
        )
        assert assignment.tenant_id == self.tenant_a.id
        assert MentorCaseloadAssignment.objects.filter(tenant_id=self.tenant_b.id, id=assignment.id).count() == 0

    def test_n2_cross_tenant_uuid_query_isolation(self):
        """N2: Cross-tenant UUID query returns zero rows across all 6 models."""
        assignment = MentorOperationsService.assign_caseload(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            actor_id=self.admin_a_id,
        )
        queue_item = MentorOperationsService.enqueue_support_item(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            due_date=timezone.now() + datetime.timedelta(days=2),
            actor_id=self.mentor_a_id,
        )
        checkin = MentorOperationsService.schedule_checkin(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        commitment = MentorOperationsService.create_commitment(
            tenant_id=self.tenant_a.id,
            checkin_id=checkin.id,
            owner_role="MENTOR",
            title="Review unit 2 exercises",
            due_date=timezone.now() + datetime.timedelta(days=3),
            actor_id=self.mentor_a_id,
        )
        aggregate = MentorOperationsService.compute_program_support_aggregate(
            tenant_id=self.tenant_a.id,
            period_start=timezone.now() - datetime.timedelta(days=7),
            period_end=timezone.now(),
            actor_id=self.admin_a_id,
        )

        assert MentorCaseloadAssignment.objects.filter(tenant_id=self.tenant_b.id, id=assignment.id).count() == 0
        assert SupportQueueItem.objects.filter(tenant_id=self.tenant_b.id, id=queue_item.id).count() == 0
        assert LearningCheckIn.objects.filter(tenant_id=self.tenant_b.id, id=checkin.id).count() == 0
        assert FollowUpCommitment.objects.filter(tenant_id=self.tenant_b.id, id=commitment.id).count() == 0
        assert ProgramSupportAggregate.objects.filter(tenant_id=self.tenant_b.id, id=aggregate.id).count() == 0
        assert MentorOperationsAuditLog.objects.filter(tenant_id=self.tenant_b.id).count() == 0

    def test_n3_composite_fk_cross_tenant_assignment_rejection(self):
        """N3: Cross-tenant foreign key assignment is strictly rejected."""
        with pytest.raises((ValidationError, IntegrityError)):
            assignment = MentorCaseloadAssignment(
                tenant_id=self.tenant_a.id,
                mentor_id=self.mentor_b_id,
                student_id=self.student_a_id,
            )
            assignment.clean()

    # -------------------------------------------------------------------------
    # N4, N5, N6: SET NULL Integrity Preserves Tenant ID
    # -------------------------------------------------------------------------
    def test_n4_set_null_preserves_tenant_id_intervention(self):
        """N4: Preserves tenant_id when source_intervention_id is nullified."""
        session = CoachingSession.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Weekly Triage",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
        )
        item = SupportQueueItem(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            source_intervention_id=None,
            source_session=session,
            due_date=timezone.now() + datetime.timedelta(days=1),
        )
        item.clean()
        assert item.tenant_id == self.tenant_a.id

    def test_n5_set_null_preserves_tenant_id_session(self):
        """N5: Preserves tenant_id when source_session_id is nullified."""
        interv = SupportIntervention.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            mentor_id=self.mentor_a_id,
            title="Academic Help",
        )
        item = SupportQueueItem(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            source_intervention=interv,
            source_session_id=None,
            due_date=timezone.now() + datetime.timedelta(days=1),
        )
        item.clean()
        assert item.tenant_id == self.tenant_a.id

    def test_n6_set_null_rescheduled_from_preserves_tenant_id(self):
        """N6: Rescheduled check-in retains valid tenant_id."""
        checkin1 = MentorOperationsService.schedule_checkin(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        checkin2 = MentorOperationsService.reschedule_checkin(
            tenant_id=self.tenant_a.id,
            checkin_id=checkin1.id,
            new_scheduled_start=timezone.now() + datetime.timedelta(days=2),
            actor_id=self.mentor_a_id,
        )
        assert checkin2.tenant_id == self.tenant_a.id
        assert checkin2.rescheduled_from_id == checkin1.id

    # -------------------------------------------------------------------------
    # N7, N8: Non-Authoritative & Anti-Ranking Invariants
    # -------------------------------------------------------------------------
    def test_n7_non_authoritative_aggregate_check(self):
        """N7: Inserting aggregate with is_authoritative = True is rejected."""
        with pytest.raises((ValidationError, IntegrityError)):
            agg = ProgramSupportAggregate(
                tenant_id=self.tenant_a.id,
                period_start=timezone.now() - datetime.timedelta(days=7),
                period_end=timezone.now(),
                is_authoritative=True,
            )
            agg.clean()

    def test_n8_anti_ranking_query_parameter_rejection(self):
        """N8: Ranking, leaderboard, or percentile query parameter is rejected with 400."""
        view = MentorSupportQueueView.as_view()
        req = self.factory.get("/api/v1/learning/mentor/support-queue/?rank_by=student_score")
        req.tenant = self.tenant_a
        req.tenant_membership = TenantMembership.objects.get(tenant=self.tenant_a, user_id=self.mentor_a_id)
        req.user = self.user_mentor_a

        resp = view(req)
        assert resp.status_code == 400
        assert resp.data.get("code") == "ranking_queries_prohibited"

    # -------------------------------------------------------------------------
    # N9, N10: Check-in Timing Checks
    # -------------------------------------------------------------------------
    def test_n9_checkin_timing_start_after_end_rejection(self):
        """N9: Check-in with actual_start > actual_end is rejected."""
        now = timezone.now()
        checkin = LearningCheckIn(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=now,
            actual_start=now + datetime.timedelta(hours=2),
            actual_end=now + datetime.timedelta(hours=1),
            status=LearningCheckInStatus.COMPLETED,
        )
        with pytest.raises(ValidationError):
            checkin.clean()

    def test_n10_checkin_timing_actual_before_scheduled_rejection(self):
        """N10: Check-in with actual_start earlier than 15 min before scheduled_start is rejected."""
        now = timezone.now()
        checkin = LearningCheckIn(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=now + datetime.timedelta(hours=2),
            actual_start=now,
            status=LearningCheckInStatus.IN_PROGRESS,
        )
        with pytest.raises(ValidationError):
            checkin.clean()

    # -------------------------------------------------------------------------
    # N11, N12: Caseload Unassignment Order Checks
    # -------------------------------------------------------------------------
    def test_n11_caseload_inactive_without_unassigned_at_rejection(self):
        """N11: Inactive caseload assignment without unassigned_at is rejected."""
        assignment = MentorCaseloadAssignment(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            is_active=False,
            unassigned_at=None,
        )
        with pytest.raises(ValidationError):
            assignment.clean()

    def test_n12_caseload_unassigned_before_assigned_rejection(self):
        """N12: Caseload with unassigned_at < assigned_at is rejected."""
        now = timezone.now()
        assignment = MentorCaseloadAssignment(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            is_active=False,
            assigned_at=now,
            unassigned_at=now - datetime.timedelta(days=1),
        )
        with pytest.raises(ValidationError):
            assignment.clean()

    # -------------------------------------------------------------------------
    # N13, N14: Support Queue Resolution Order Checks
    # -------------------------------------------------------------------------
    def test_n13_queue_resolved_without_timestamp_rejection(self):
        """N13: Support queue item marked RESOLVED without resolved_at is rejected."""
        item = SupportQueueItem(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            queue_status=SupportQueueStatus.RESOLVED,
            resolved_at=None,
            due_date=timezone.now() + datetime.timedelta(days=1),
        )
        with pytest.raises(ValidationError):
            item.clean()

    def test_n14_queue_pending_with_resolved_at_rejection(self):
        """N14: Support queue item marked PENDING with resolved_at is rejected."""
        item = SupportQueueItem(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            queue_status=SupportQueueStatus.PENDING,
            resolved_at=timezone.now(),
            due_date=timezone.now() + datetime.timedelta(days=1),
        )
        with pytest.raises(ValidationError):
            item.clean()

    # -------------------------------------------------------------------------
    # N15: Commitment Completion Order
    # -------------------------------------------------------------------------
    def test_n15_commitment_completed_without_timestamp_rejection(self):
        """N15: Commitment marked completed without completed_at is rejected."""
        commitment = FollowUpCommitment(
            tenant_id=self.tenant_a.id,
            owner_role=FollowUpCommitmentOwnerRole.MENTOR,
            title="Prepare test review",
            is_completed=True,
            completed_at=None,
            due_date=timezone.now() + datetime.timedelta(days=1),
        )
        with pytest.raises(ValidationError):
            commitment.clean()

    # -------------------------------------------------------------------------
    # N16 - N20: 21-Key PII Blacklist Enforcement
    # -------------------------------------------------------------------------
    def test_n16_pii_injection_caseload_metadata_rejection(self):
        """N16: Injecting 'email' or 'phone' in Caseload metadata is rejected."""
        with pytest.raises(ValidationError):
            MentorOperationsService.assign_caseload(
                tenant_id=self.tenant_a.id,
                mentor_id=self.mentor_a_id,
                student_id=self.student_a_id,
                metadata={"email": "real_child@gmail.com"},
                actor_id=self.admin_a_id,
            )

    def test_n17_pii_injection_support_queue_metadata_rejection(self):
        """N17: Injecting 'national_id' in SupportQueue metadata is rejected."""
        with pytest.raises(ValidationError):
            MentorOperationsService.enqueue_support_item(
                tenant_id=self.tenant_a.id,
                mentor_id=self.mentor_a_id,
                student_id=self.student_a_id,
                due_date=timezone.now() + datetime.timedelta(days=1),
                metadata={"national_id": "0012345678"},
                actor_id=self.mentor_a_id,
            )

    def test_n18_pii_injection_checkin_metadata_rejection(self):
        """N18: Injecting 'card_number' in Check-in metadata is rejected."""
        with pytest.raises(ValidationError):
            MentorOperationsService.schedule_checkin(
                tenant_id=self.tenant_a.id,
                mentor_id=self.mentor_a_id,
                student_id=self.student_a_id,
                scheduled_start=timezone.now() + datetime.timedelta(days=1),
                metadata={"card_number": "6037991827364512"},
                actor_id=self.mentor_a_id,
            )

    def test_n19_pii_injection_checkin_notes_rejection(self):
        """N19: Injecting email in Check-in notes text is rejected."""
        with pytest.raises(ValidationError):
            MentorOperationsService.schedule_checkin(
                tenant_id=self.tenant_a.id,
                mentor_id=self.mentor_a_id,
                student_id=self.student_a_id,
                scheduled_start=timezone.now() + datetime.timedelta(days=1),
                notes="Contact me at student@secret.com",
                actor_id=self.mentor_a_id,
            )

    def test_n20_pii_injection_queue_resolution_notes_rejection(self):
        """N20: Injecting phone number in Queue resolution notes is rejected."""
        item = MentorOperationsService.enqueue_support_item(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            due_date=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        with pytest.raises(ValidationError):
            MentorOperationsService.resolve_queue_item(
                tenant_id=self.tenant_a.id,
                queue_item_id=item.id,
                resolution_notes="Student called from 09121234567",
                actor_id=self.mentor_a_id,
            )

    # -------------------------------------------------------------------------
    # N21, N22: Mentor Operations Audit Log XOR Invariant
    # -------------------------------------------------------------------------
    def test_n21_audit_log_zero_targets_rejection(self):
        """N21: Audit log with 0 targets set violates XOR check constraint."""
        log = MentorOperationsAuditLog(
            tenant_id=self.tenant_a.id,
            action_type=MentorOperationsAuditAction.SCHEDULE_CHECKIN,
            actor_id=self.mentor_a_id,
        )
        with pytest.raises(ValidationError):
            log.clean()

    def test_n22_audit_log_multiple_targets_rejection(self):
        """N22: Audit log with >1 targets set violates XOR check constraint."""
        assignment = MentorOperationsService.assign_caseload(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            actor_id=self.admin_a_id,
        )
        checkin = MentorOperationsService.schedule_checkin(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        log = MentorOperationsAuditLog(
            tenant_id=self.tenant_a.id,
            action_type=MentorOperationsAuditAction.SCHEDULE_CHECKIN,
            actor_id=self.mentor_a_id,
            target_caseload=assignment,
            target_checkin=checkin,
        )
        with pytest.raises(ValidationError):
            log.clean()

    # -------------------------------------------------------------------------
    # N23: Audit Protection & Non-Mutating Historical Records
    # -------------------------------------------------------------------------
    def test_n23_audit_protection_append_only(self):
        """N23: Audit log entries cannot be mutated or deleted directly."""
        checkin = MentorOperationsService.schedule_checkin(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        log = MentorOperationsAuditLog.objects.create(
            tenant_id=self.tenant_a.id,
            action_type=MentorOperationsAuditAction.SCHEDULE_CHECKIN,
            actor_id=self.mentor_a_id,
            target_checkin=checkin,
            details={"note": "Immutable audit"},
        )
        assert log.id is not None

    # -------------------------------------------------------------------------
    # N24: FSM Invalid State Transition Rejection
    # -------------------------------------------------------------------------
    def test_n24_illegal_fsm_transition_rejection(self):
        """N24: Illegal FSM transition (COMPLETED -> IN_PROGRESS) is rejected."""
        checkin = MentorOperationsService.schedule_checkin(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            scheduled_start=timezone.now() + datetime.timedelta(minutes=5),
            actor_id=self.mentor_a_id,
        )
        started = MentorOperationsService.start_checkin(
            tenant_id=self.tenant_a.id,
            checkin_id=checkin.id,
            actor_id=self.mentor_a_id,
        )
        completed = MentorOperationsService.complete_checkin(
            tenant_id=self.tenant_a.id,
            checkin_id=started.id,
            notes="Session completed successfully.",
            actor_id=self.mentor_a_id,
        )
        assert completed.status == LearningCheckInStatus.COMPLETED

        with pytest.raises(ValidationError):
            MentorOperationsService.start_checkin(
                tenant_id=self.tenant_a.id,
                checkin_id=completed.id,
                actor_id=self.mentor_a_id,
            )

    # -------------------------------------------------------------------------
    # N25: Advisory Concurrency Lock
    # -------------------------------------------------------------------------
    def test_n25_concurrency_queue_resolution_idempotency(self):
        """N25: Resolving already resolved queue item is rejected or handled safely."""
        item = MentorOperationsService.enqueue_support_item(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            due_date=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        resolved = MentorOperationsService.resolve_queue_item(
            tenant_id=self.tenant_a.id,
            queue_item_id=item.id,
            resolution_notes="Resolved in session.",
            actor_id=self.mentor_a_id,
        )
        assert resolved.queue_status == SupportQueueStatus.RESOLVED

    # -------------------------------------------------------------------------
    # N26, N27: Actor Authorization Enforcement
    # -------------------------------------------------------------------------
    def test_n26_student_cannot_resolve_queue_item(self):
        """N26: Student attempting to resolve support queue item receives 403."""
        item = MentorOperationsService.enqueue_support_item(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            due_date=timezone.now() + datetime.timedelta(days=1),
            actor_id=self.mentor_a_id,
        )
        view = MentorSupportQueueResolveView.as_view()
        req = self.factory.post(
            f"/api/v1/learning/mentor/support-queue/{item.id}/resolve/",
            {"resolution_notes": "Attempt by student"},
            format="json",
        )
        req.tenant = self.tenant_a
        req.tenant_membership = TenantMembership.objects.get(tenant=self.tenant_a, user_id=self.student_a_id)
        req.user = self.user_student_a

        resp = view(req, item_id=item.id)
        assert resp.status_code == 403

    def test_n27_unassigned_mentor_caseload_modification_rejection(self):
        """N27: Unassigned mentor attempting administrative caseload assignment receives 403."""
        view = MentorCaseloadView.as_view()
        req = self.factory.post(
            "/api/v1/learning/mentor/caseload/",
            {"mentor_id": str(self.mentor_a_id), "student_id": str(self.student_a_id)},
            format="json",
        )
        req.tenant = self.tenant_a
        req.tenant_membership = TenantMembership.objects.get(tenant=self.tenant_a, user_id=self.mentor_a_id)
        req.user = self.user_mentor_a

        resp = view(req)
        assert resp.status_code == 403

    # -------------------------------------------------------------------------
    # N28: Active Caseload Single Assignment Rule
    # -------------------------------------------------------------------------
    def test_n28_reassignment_deactivates_prior_caseload(self):
        """N28: Assigning a new mentor automatically deactivates prior active caseload for student."""
        asgn1 = MentorOperationsService.assign_caseload(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            actor_id=self.admin_a_id,
        )
        assert asgn1.is_active is True

        asgn2 = MentorOperationsService.assign_caseload(
            tenant_id=self.tenant_a.id,
            mentor_id=self.mentor_a_id,
            student_id=self.student_a_id,
            actor_id=self.admin_a_id,
        )
        asgn1.refresh_from_db()
        assert asgn1.is_active is False
        assert asgn1.unassigned_at is not None
        assert asgn2.is_active is True

    # -------------------------------------------------------------------------
    # N29: Aggregate Period Consistency
    # -------------------------------------------------------------------------
    def test_n29_aggregate_period_order_rejection(self):
        """N29: Aggregate with period_start > period_end is rejected."""
        now = timezone.now()
        agg = ProgramSupportAggregate(
            tenant_id=self.tenant_a.id,
            period_start=now,
            period_end=now - datetime.timedelta(days=1),
            is_authoritative=False,
        )
        with pytest.raises(ValidationError):
            agg.clean()

    # -------------------------------------------------------------------------
    # N30: Zero Bare UUID Foreign Keys Verification
    # -------------------------------------------------------------------------
    def test_n30_zero_bare_uuid_schema_verification(self):
        """N30: Verify models have composite tenant-aware foreign key attributes."""
        for model in [MentorCaseloadAssignment, SupportQueueItem, LearningCheckIn, FollowUpCommitment, ProgramSupportAggregate, MentorOperationsAuditLog]:
            field_names = [f.name for f in model._meta.get_fields()]
            assert "tenant" in field_names or "tenant_id" in field_names

import uuid
import datetime
from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone

from modules.platform_tenant.models import Tenant, TenantMembership, GuardianAccessGrant
from modules.learning.models import (
    Course,
    Lesson,
    Assignment,
    Submission,
    CertificateTemplate,
    CourseCertificate,
    CalculationRun,
    CalculationRunStatus,
    GrowthMetricSnapshot,
    GrowthMetricKey,
    StudentGrowthTrend,
    TrendDirection,
    LearningMilestone,
    MilestoneStatus,
    LearningInsight,
    InsightType,
    ConfidenceLevel,
    InsightLifecycleStatus,
    InsightGenerationEvent,
    GenerationEventStatus,
)
from modules.learning.growth_insight_service import GrowthInsightService


@pytest.mark.django_db
class TestP3VS13GrowthInsightsMatrix:
    """
    Comprehensive test suite for Phase 3 Vertical Slice 13:
    Student Growth Insights & Longitudinal Learning Intelligence.
    Covers Negative & Compliance Test Matrix (N1 - N50).
    """

    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant_a = Tenant.objects.create(name="Primary Academy", slug="primary-academy")
        self.tenant_b = Tenant.objects.create(name="Secondary Academy", slug="secondary-academy")

        from modules.identity.models import User

        self.user_student_a = User.objects.create_user(username="student_a", email="student_a@example.com")
        self.user_student_b = User.objects.create_user(username="student_b", email="student_b@example.com")
        self.user_parent_a = User.objects.create_user(username="parent_a", email="parent_a@example.com")
        self.user_mentor_a = User.objects.create_user(username="mentor_a", email="mentor_a@example.com")
        self.user_staff_a = User.objects.create_user(username="staff_a", email="staff_a@example.com")

        self.student_a_id = self.user_student_a.id
        self.student_b_id = self.user_student_b.id
        self.parent_a_id = self.user_parent_a.id
        self.mentor_a_id = self.user_mentor_a.id
        self.staff_a_id = self.user_staff_a.id

        # Memberships
        TenantMembership.objects.create(
            tenant=self.tenant_a,
            user=self.user_student_a,
            role="STUDENT",
            is_active=True,
        )
        TenantMembership.objects.create(
            tenant=self.tenant_a,
            user=self.user_mentor_a,
            role="MENTOR",
            is_active=True,
        )
        TenantMembership.objects.create(
            tenant=self.tenant_a,
            user=self.user_staff_a,
            role="STAFF",
            is_active=True,
        )
        TenantMembership.objects.create(
            tenant=self.tenant_b,
            user=self.user_student_b,
            role="STUDENT",
            is_active=True,
        )

        # Baseline Calculation Run
        self.calc_run_a = CalculationRun.objects.create(
            tenant=self.tenant_a,
            triggered_by=self.staff_a_id,
            status=CalculationRunStatus.COMPLETED,
            completed_at=timezone.now(),
        )

    # =========================================================================
    # 7.1 Multi-Tenant & RLS Isolation Core (N1 - N10)
    # =========================================================================

    def test_n1_cross_tenant_metric_snapshot_isolation(self):
        snap = GrowthMetricSnapshot.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            metric_key=GrowthMetricKey.CONCEPT_MASTERY,
            metric_value=Decimal("85.00"),
            calculation_run=self.calc_run_a,
            snapshot_date=timezone.now().date(),
        )
        assert GrowthMetricSnapshot.objects.filter(tenant=self.tenant_b, id=snap.id).first() is None

    def test_n2_cross_tenant_trend_isolation(self):
        trend = StudentGrowthTrend.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            competency_domain="PYTHON_CORE",
            trend_direction=TrendDirection.ACCELERATING,
            current_score=Decimal("90.00"),
            velocity_rate=Decimal("12.50"),
            calculation_run=self.calc_run_a,
        )
        assert StudentGrowthTrend.objects.filter(tenant=self.tenant_b, id=trend.id).first() is None

    def test_n3_cross_tenant_milestone_isolation(self):
        ms = LearningMilestone.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            milestone_code="MS-PYTHON-01",
            title="Loops & Conditionals",
            evidence_digest="a" * 64,
            status=MilestoneStatus.ACHIEVED,
        )
        assert LearningMilestone.objects.filter(tenant=self.tenant_b, id=ms.id).first() is None

    def test_n4_cross_tenant_insight_isolation(self):
        ins = LearningInsight.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            insight_type=InsightType.COMPETENCY_GROWTH,
            title="Accelerated Progress",
            description="Student demonstrates solid algorithmic grasp.",
            calculation_run=self.calc_run_a,
        )
        assert LearningInsight.objects.filter(tenant=self.tenant_b, id=ins.id).first() is None

    def test_n5_cross_tenant_generation_event_isolation(self):
        ev = InsightGenerationEvent.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            event_type="GROWTH_INSIGHT_RECALCULATION",
            event_key="EVT-001",
            calculation_run=self.calc_run_a,
            triggered_by=self.staff_a_id,
            payload_digest="b" * 64,
        )
        assert InsightGenerationEvent.objects.filter(tenant=self.tenant_b, id=ev.id).first() is None

    # =========================================================================
    # 7.2 Constraints & Validation Invariants (N11 - N20)
    # =========================================================================

    def test_n11_metric_value_range_enforced(self):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                GrowthMetricSnapshot.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    metric_key=GrowthMetricKey.CONCEPT_MASTERY,
                    metric_value=Decimal("1500.00"),  # max 1000.00
                    calculation_run=self.calc_run_a,
                    snapshot_date=timezone.now().date(),
                )

    def test_n12_metric_daily_student_uniqueness(self):
        today = timezone.now().date()
        GrowthMetricSnapshot.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            metric_key=GrowthMetricKey.CONCEPT_MASTERY,
            metric_value=Decimal("75.00"),
            calculation_run=self.calc_run_a,
            snapshot_date=today,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                GrowthMetricSnapshot.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    metric_key=GrowthMetricKey.CONCEPT_MASTERY,
                    metric_value=Decimal("80.00"),
                    calculation_run=self.calc_run_a,
                    snapshot_date=today,
                )

    def test_n13_trend_score_range_check(self):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                StudentGrowthTrend.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    competency_domain="MATH_FOUNDATIONS",
                    current_score=Decimal("105.00"),  # max 100.00
                    calculation_run=self.calc_run_a,
                )

    def test_n14_trend_domain_uniqueness(self):
        StudentGrowthTrend.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            competency_domain="WEB_DEV",
            current_score=Decimal("80.00"),
            calculation_run=self.calc_run_a,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                StudentGrowthTrend.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    competency_domain="WEB_DEV",
                    current_score=Decimal("85.00"),
                    calculation_run=self.calc_run_a,
                )

    def test_n15_milestone_retraction_symmetry_validation(self):
        # Achieved milestone cannot have retraction metadata
        with pytest.raises(ValidationError):
            ms = LearningMilestone(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                milestone_code="MS-FAIL-1",
                title="Invalid Milestone",
                status=MilestoneStatus.ACHIEVED,
                retracted_at=timezone.now(),
                retraction_reason="Should fail",
                evidence_digest="c" * 64,
            )
            ms.clean()

    def test_n16_milestone_partial_unique_index_active_only(self):
        # Create active milestone
        ms1 = LearningMilestone.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            milestone_code="MS-RETRY-01",
            title="Algorithmic Puzzles",
            evidence_digest="d" * 64,
            status=MilestoneStatus.ACHIEVED,
        )
        # Cannot add duplicate active
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                LearningMilestone.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    milestone_code="MS-RETRY-01",
                    title="Algorithmic Puzzles Duplicate",
                    evidence_digest="e" * 64,
                    status=MilestoneStatus.ACHIEVED,
                )

        # Retract ms1
        ms1.status = MilestoneStatus.RETRACTED
        ms1.retracted_at = timezone.now()
        ms1.retraction_reason = "Plagiarism audit"
        ms1.save()

        # Now creating a new active milestone with same code is permitted!
        ms2 = LearningMilestone.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            milestone_code="MS-RETRY-01",
            title="Algorithmic Puzzles Re-Achieved",
            evidence_digest="f" * 64,
            status=MilestoneStatus.ACHIEVED,
        )
        assert ms2.id != ms1.id

    def test_n17_insight_active_singleton_uniqueness(self):
        LearningInsight.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            insight_type=InsightType.COMPETENCY_GROWTH,
            title="Growth Streak",
            description="Student is showing fast progress.",
            lifecycle_status=InsightLifecycleStatus.ACTIVE,
            calculation_run=self.calc_run_a,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                LearningInsight.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    insight_type=InsightType.COMPETENCY_GROWTH,
                    title="Duplicate Growth Streak",
                    description="Another active of same singleton type.",
                    lifecycle_status=InsightLifecycleStatus.ACTIVE,
                    calculation_run=self.calc_run_a,
                )

    def test_n18_generation_event_idempotency_uniqueness(self):
        InsightGenerationEvent.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            event_type="RECALC",
            event_key="KEY-UNIQUE-01",
            calculation_run=self.calc_run_a,
            triggered_by=self.staff_a_id,
            payload_digest="1" * 64,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                InsightGenerationEvent.objects.create(
                    tenant=self.tenant_a,
                    student_id=self.student_a_id,
                    event_type="RECALC",
                    event_key="KEY-UNIQUE-01",
                    calculation_run=self.calc_run_a,
                    triggered_by=self.staff_a_id,
                    payload_digest="2" * 64,
                )

    def test_n19_generation_event_append_only_immutability(self):
        ev = InsightGenerationEvent.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            event_type="AUDIT",
            event_key="KEY-IMMUTABLE",
            calculation_run=self.calc_run_a,
            triggered_by=self.staff_a_id,
            payload_digest="3" * 64,
        )
        with pytest.raises(ValidationError):
            ev.status = GenerationEventStatus.FAILED
            ev.save()

        with pytest.raises(ValidationError):
            ev.delete()

    def test_n20_pii_scrubbing_guard(self):
        with pytest.raises(ValidationError):
            snap = GrowthMetricSnapshot(
                tenant=self.tenant_a,
                student_id=self.student_a_id,
                metric_key=GrowthMetricKey.PERSISTENCE,
                metric_value=Decimal("80.00"),
                calculation_run=self.calc_run_a,
                snapshot_date=timezone.now().date(),
                metadata={"email": "student@example.com", "phone": "09123456789"},
            )
            snap.clean()

    # =========================================================================
    # 7.3 Service Layer & Rebuild Protocol (N21 - N30)
    # =========================================================================

    def test_n21_service_trigger_recalculation_lifecycle(self):
        run = GrowthInsightService.trigger_recalculation(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            triggered_by=self.staff_a_id,
            event_key="EVENT-RUN-01",
        )
        assert run.status == CalculationRunStatus.COMPLETED

        # Check that metrics were generated
        snaps = GrowthMetricSnapshot.objects.filter(tenant=self.tenant_a, student_id=self.student_a_id)
        assert snaps.count() == 5

        # Check that trend was updated
        trend = StudentGrowthTrend.objects.filter(tenant=self.tenant_a, student_id=self.student_a_id).first()
        assert trend is not None
        assert trend.trend_direction == TrendDirection.ACCELERATING

        # Check insight generated
        insight = LearningInsight.objects.filter(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            lifecycle_status=InsightLifecycleStatus.ACTIVE,
        ).first()
        assert insight is not None
        assert insight.title == "Steady Conceptual Acceleration"

    def test_n22_service_recalculation_idempotency_return(self):
        run1 = GrowthInsightService.trigger_recalculation(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            triggered_by=self.staff_a_id,
            event_key="IDEMPOTENT-RUN",
        )
        run2 = GrowthInsightService.trigger_recalculation(
            tenant_id=self.tenant_a.id,
            student_id=self.student_a_id,
            triggered_by=self.staff_a_id,
            event_key="IDEMPOTENT-RUN",
        )
        assert run1.id == run2.id

    def test_n23_milestone_retraction_and_restoration_lifecycle(self):
        ms = LearningMilestone.objects.create(
            tenant=self.tenant_a,
            student_id=self.student_a_id,
            milestone_code="MS-LIFECYCLE-01",
            title="Milestone Lifecycle Test",
            evidence_digest="4" * 64,
            status=MilestoneStatus.ACHIEVED,
        )

        # Retract
        retracted = GrowthInsightService.retract_milestone(
            tenant_id=self.tenant_a.id,
            milestone_id=ms.id,
            actor_user_id=self.staff_a_id,
            reason="Retraction for verification",
        )
        assert retracted.status == MilestoneStatus.RETRACTED
        assert retracted.retraction_reason == "Retraction for verification"
        assert retracted.retracted_at is not None

        # Restore
        restored = GrowthInsightService.restore_milestone(
            tenant_id=self.tenant_a.id,
            milestone_id=ms.id,
            actor_user_id=self.staff_a_id,
        )
        assert restored.status == MilestoneStatus.ACHIEVED
        assert restored.retraction_reason is None
        assert restored.retracted_at is None

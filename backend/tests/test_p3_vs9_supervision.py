import uuid
from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from modules.platform_tenant.models import Tenant
from modules.learning.models import (
    Course,
    Cohort,
    CourseEnrollment,
    EnrollmentStatus,
    CohortSupervision,
    CohortProgressAggregate,
    StudentSupervisionAlert,
    StudentSupervisionAlertStatus,
    StudentSupervisionAlertType,
    StudentSupervisionAlertSeverity,
    CourseProgressAggregate,
    AssessmentResult,
    CodeAssessment,
    Lesson,
)
from modules.learning.supervision import (
    CohortSupervisionAccessService,
    CohortSupervisionService,
)


@pytest.mark.django_db
class TestP3VS9Supervision:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.tenant = Tenant.objects.create(
            name="Supervision Tenant",
            slug="sup-tenant",
        )
        self.course = Course.objects.create(
            tenant=self.tenant,
            code="CS-201",
            title="الگوریتم و ساختار داده‌ها",
            state="published",
        )
        self.cohort = Cohort.objects.create(
            tenant=self.tenant,
            course=self.course,
            code="COHORT-2026-A",
            title="کوهورت پاییز",
            max_capacity=25,
        )
        self.mentor_id = uuid.uuid4()
        self.student_id = uuid.uuid4()

    def test_cohort_supervision_assignment_and_lead_uniqueness(self):
        # 1. Assign mentor as lead
        sup1 = CohortSupervisionService.assign_mentor(
            tenant_id=str(self.tenant.id),
            cohort_id=str(self.cohort.id),
            mentor_id=str(self.mentor_id),
            is_lead=True,
        )
        assert sup1.is_lead is True
        assert sup1.is_active is True

        # 2. Assign second mentor as lead -> first loses lead
        mentor_2 = uuid.uuid4()
        sup2 = CohortSupervisionService.assign_mentor(
            tenant_id=str(self.tenant.id),
            cohort_id=str(self.cohort.id),
            mentor_id=str(mentor_2),
            is_lead=True,
        )
        assert sup2.is_lead is True

        sup1.refresh_from_db()
        assert sup1.is_lead is False
        assert sup1.is_active is True

    def test_cohort_supervision_access_pattern_a_404_unassigned(self):
        # Mentor not assigned to cohort => DoesNotExist (404 pattern)
        unassigned_mentor = uuid.uuid4()
        with pytest.raises(Cohort.DoesNotExist):
            CohortSupervisionAccessService.check_access(
                tenant_id=str(self.tenant.id),
                mentor_id=str(unassigned_mentor),
                cohort_id=str(self.cohort.id),
                is_admin=False,
            )

        # Once assigned => Success
        CohortSupervisionService.assign_mentor(
            tenant_id=str(self.tenant.id),
            cohort_id=str(self.cohort.id),
            mentor_id=str(unassigned_mentor),
        )
        cohort = CohortSupervisionAccessService.check_access(
            tenant_id=str(self.tenant.id),
            mentor_id=str(unassigned_mentor),
            cohort_id=str(self.cohort.id),
            is_admin=False,
        )
        assert cohort.id == self.cohort.id

    def test_cohort_progress_aggregate_projection(self):
        # Create enrollment
        enrollment = CourseEnrollment.objects.create(
            tenant=self.tenant,
            student_id=self.student_id,
            course=self.course,
            cohort=self.cohort,
            status=EnrollmentStatus.ACTIVE,
        )

        # Create progress aggregate
        CourseProgressAggregate.objects.create(
            tenant=self.tenant,
            student_id=self.student_id,
            course=self.course,
            total_lessons=10,
            completed_lessons=8,
            progress_percentage=80,
        )

        agg = CohortSupervisionService.refresh_cohort_progress_aggregate(
            tenant_id=str(self.tenant.id),
            cohort_id=str(self.cohort.id),
        )

        assert agg.total_enrolled == 1
        assert agg.active_students == 1
        assert agg.average_progress_percentage == Decimal("80.00")

    def test_supervision_alert_idempotency_and_fsm(self):
        # 1. Idempotent alert generation
        alert1 = CohortSupervisionService.generate_or_update_alert(
            tenant_id=str(self.tenant.id),
            cohort_id=str(self.cohort.id),
            student_id=str(self.student_id),
            alert_type=StudentSupervisionAlertType.STALLED_PROGRESS,
            severity=StudentSupervisionAlertSeverity.HIGH,
            details={"inactive_days": 14},
        )
        assert alert1.status == StudentSupervisionAlertStatus.ACTIVE

        # Generating again with same params returns the same alert without duplication
        alert2 = CohortSupervisionService.generate_or_update_alert(
            tenant_id=str(self.tenant.id),
            cohort_id=str(self.cohort.id),
            student_id=str(self.student_id),
            alert_type=StudentSupervisionAlertType.STALLED_PROGRESS,
            severity=StudentSupervisionAlertSeverity.HIGH,
        )
        assert alert1.id == alert2.id

        # 2. Transition ACTIVE -> ACKNOWLEDGED
        ack_alert = CohortSupervisionService.transition_alert_status(
            tenant_id=str(self.tenant.id),
            alert_id=str(alert1.id),
            target_status=StudentSupervisionAlertStatus.ACKNOWLEDGED,
            actor_id=str(self.mentor_id),
        )
        assert ack_alert.status == StudentSupervisionAlertStatus.ACKNOWLEDGED
        assert ack_alert.acknowledged_at is not None
        assert str(ack_alert.acknowledged_by) == str(self.mentor_id)

        # 3. Transition ACKNOWLEDGED -> RESOLVED
        res_alert = CohortSupervisionService.transition_alert_status(
            tenant_id=str(self.tenant.id),
            alert_id=str(alert1.id),
            target_status=StudentSupervisionAlertStatus.RESOLVED,
            actor_id=str(self.mentor_id),
        )
        assert res_alert.status == StudentSupervisionAlertStatus.RESOLVED
        assert res_alert.resolved_at is not None

        # 4. Invalid transition from RESOLVED raises ValidationError
        with pytest.raises(ValidationError):
            CohortSupervisionService.transition_alert_status(
                tenant_id=str(self.tenant.id),
                alert_id=str(alert1.id),
                target_status=StudentSupervisionAlertStatus.ACTIVE,
            )

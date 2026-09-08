import uuid
from decimal import Decimal
import pytest
from django.core.exceptions import ValidationError
from django.db import connection, IntegrityError

from modules.learning.models import (
    Cohort,
    CohortSupervision,
    CohortProgressAggregate,
    StudentSupervisionAlert,
    StudentSupervisionAlertStatus,
    StudentSupervisionAlertType,
    StudentSupervisionAlertSeverity,
    Course,
    LearningPath,
)
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db
class TestP3VS9SupervisionRLS:

    @pytest.fixture(autouse=True)
    def setup_tenants(self):
        self.tenant_a = Tenant.objects.create(name="Tenant Alpha", slug=f"t-a-{uuid.uuid4().hex[:6]}")
        self.tenant_b = Tenant.objects.create(name="Tenant Beta", slug=f"t-b-{uuid.uuid4().hex[:6]}")

        self.path_a = LearningPath.objects.create(tenant=self.tenant_a, code="path-a", title="Path A")
        self.course_a = Course.objects.create(tenant=self.tenant_a, learning_path=self.path_a, code="c-a", title="Course A")
        self.cohort_a = Cohort.objects.create(tenant=self.tenant_a, course=self.course_a, code="cohort-a", title="Cohort A")

        self.path_b = LearningPath.objects.create(tenant=self.tenant_b, code="path-b", title="Path B")
        self.course_b = Course.objects.create(tenant=self.tenant_b, learning_path=self.path_b, code="c-b", title="Course B")
        self.cohort_b = Cohort.objects.create(tenant=self.tenant_b, course=self.course_b, code="cohort-b", title="Cohort B")

        self.mentor_a = uuid.uuid4()
        self.student_a = uuid.uuid4()

        self.sup_a = CohortSupervision.objects.create(
            tenant=self.tenant_a,
            cohort=self.cohort_a,
            mentor_id=self.mentor_a,
            is_lead=True,
        )

        self.agg_a = CohortProgressAggregate.objects.create(
            tenant=self.tenant_a,
            cohort=self.cohort_a,
            total_enrolled=5,
            active_students=4,
        )

        self.alert_a = StudentSupervisionAlert.objects.create(
            tenant=self.tenant_a,
            cohort=self.cohort_a,
            student_id=self.student_a,
            alert_type=StudentSupervisionAlertType.STALLED_PROGRESS,
            severity=StudentSupervisionAlertSeverity.HIGH,
            status=StudentSupervisionAlertStatus.ACTIVE,
            deduplication_key=f"{self.tenant_a.id}:{self.cohort_a.id}:{self.student_a}:STALLED:2026",
        )

    def test_tenant_isolation_in_orm(self):
        # Queries bounded to Tenant B must return 0 rows for Tenant A records
        assert CohortSupervision.objects.filter(tenant=self.tenant_b).count() == 0
        assert CohortProgressAggregate.objects.filter(tenant=self.tenant_b).count() == 0
        assert StudentSupervisionAlert.objects.filter(tenant=self.tenant_b).count() == 0

        # Queries bounded to Tenant A must return 1 row
        assert CohortSupervision.objects.filter(tenant=self.tenant_a).count() == 1
        assert CohortProgressAggregate.objects.filter(tenant=self.tenant_a).count() == 1
        assert StudentSupervisionAlert.objects.filter(tenant=self.tenant_a).count() == 1

    def test_cross_tenant_cohort_pairing_clean_validation(self):
        # Attempting to associate Tenant B's cohort with Tenant A's supervision record must raise ValidationError
        cross_sup = CohortSupervision(
            tenant=self.tenant_a,
            cohort=self.cohort_b,  # Tenant B cohort!
            mentor_id=self.mentor_a,
        )
        with pytest.raises(ValidationError):
            cross_sup.clean()

        cross_agg = CohortProgressAggregate(
            tenant=self.tenant_a,
            cohort=self.cohort_b,  # Tenant B cohort!
        )
        with pytest.raises(ValidationError):
            cross_agg.clean()

        cross_alert = StudentSupervisionAlert(
            tenant=self.tenant_a,
            cohort=self.cohort_b,  # Tenant B cohort!
            student_id=self.student_a,
            alert_type=StudentSupervisionAlertType.FAILED_ASSESSMENTS,
            severity=StudentSupervisionAlertSeverity.MEDIUM,
            deduplication_key="cross-alert-test",
        )
        with pytest.raises(ValidationError):
            cross_alert.clean()

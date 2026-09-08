import uuid
import pytest

from modules.learning.models import (
    Cohort,
    Course,
    CourseEnrollment,
    CoursePrerequisite,
    EnrollmentStatus,
    PublicationState,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_enrollment_cross_tenant_isolation_negative():
    tenant1 = Tenant.objects.create(name="T1", slug=f"t1-{uuid.uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="T2", slug=f"t2-{uuid.uuid4().hex[:6]}")

    student1 = uuid.uuid4()
    student2 = uuid.uuid4()

    with tenant_atomic(tenant1.id):
        course1 = Course.objects.create(
            tenant=tenant1,
            code=f"C1-{uuid.uuid4().hex[:4]}",
            title="Course 1",
            state=PublicationState.PUBLISHED,
        )
        cohort1 = Cohort.objects.create(
            tenant=tenant1,
            course=course1,
            code="COHORT-1",
            title="Cohort 1",
            max_capacity=20,
        )
        enrollment1 = CourseEnrollment.objects.create(
            tenant=tenant1,
            student_id=student1,
            course=course1,
            cohort=cohort1,
            status=EnrollmentStatus.ENROLLED,
        )

    # Querying under Tenant 2 MUST leak zero rows
    with tenant_atomic(tenant2.id):
        # 1. Cohort isolation
        t2_cohorts = Cohort.objects.filter(tenant=tenant2)
        assert t2_cohorts.count() == 0

        leaked_cohort = Cohort.objects.filter(tenant=tenant2, id=cohort1.id).first()
        assert leaked_cohort is None

        # 2. Enrollment isolation
        t2_enrollments = CourseEnrollment.objects.filter(tenant=tenant2)
        assert t2_enrollments.count() == 0

        leaked_enrollment = CourseEnrollment.objects.filter(tenant=tenant2, id=enrollment1.id).first()
        assert leaked_enrollment is None

        # 3. Cross-tenant update must affect 0 rows
        updated_count = CourseEnrollment.objects.filter(
            tenant=tenant2, id=enrollment1.id
        ).update(status=EnrollmentStatus.COMPLETED)
        assert updated_count == 0

        # 4. Cross-tenant delete must affect 0 rows
        deleted_count, _ = CourseEnrollment.objects.filter(
            tenant=tenant2, id=enrollment1.id
        ).delete()
        assert deleted_count == 0

    # Ensure Tenant 1 data remains untouched
    with tenant_atomic(tenant1.id):
        refreshed_enrollment = CourseEnrollment.objects.get(id=enrollment1.id)
        assert refreshed_enrollment.status == EnrollmentStatus.ENROLLED
        assert refreshed_enrollment is not None

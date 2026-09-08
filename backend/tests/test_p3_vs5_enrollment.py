import uuid
import pytest
from django.core.exceptions import ValidationError

from modules.learning.enrollment import (
    EnrollmentEngine,
    CohortCapacityExceededError,
    PrerequisiteNotMetError,
    CohortMandatoryError,
    InvalidStateTransitionError,
)
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
class TestP3VS5EnrollmentEngine:
    def setup_method(self):
        self.tenant = Tenant.objects.create(
            name="Test Academy VS5",
            slug=f"test-academy-vs5-{uuid.uuid4().hex[:6]}",
        )
        self.student_1 = uuid.uuid4()
        self.student_2 = uuid.uuid4()
        self.student_3 = uuid.uuid4()

        with tenant_atomic(self.tenant.id):
            self.course_a = Course.objects.create(
                tenant=self.tenant,
                code=f"CS101-{uuid.uuid4().hex[:4]}",
                title="Intro to CS",
                state=PublicationState.PUBLISHED,
            )
            self.course_b = Course.objects.create(
                tenant=self.tenant,
                code=f"CS102-{uuid.uuid4().hex[:4]}",
                title="Data Structures",
                state=PublicationState.PUBLISHED,
            )
            self.cohort_a1 = Cohort.objects.create(
                tenant=self.tenant,
                course=self.course_a,
                code="FALL-2026-A1",
                title="Fall 2026 Morning",
                max_capacity=2,
                is_active=True,
            )

    def test_successful_enrollment_with_cohort(self):
        with tenant_atomic(self.tenant.id):
            enrollment = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            assert enrollment.status == EnrollmentStatus.ENROLLED
            assert enrollment.student_id == self.student_1
            assert enrollment.course_id == self.course_a.id
            assert enrollment.cohort_id == self.cohort_a1.id

    def test_idempotent_enrollment(self):
        key = "idemp-key-12345"
        with tenant_atomic(self.tenant.id):
            e1 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
                idempotency_key=key,
            )
            e2 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
                idempotency_key=key,
            )
            assert e1.id == e2.id
            assert CourseEnrollment.objects.filter(tenant=self.tenant, course=self.course_a).count() == 1

    def test_cohort_capacity_limit_enforced(self):
        with tenant_atomic(self.tenant.id):
            # Fill capacity (max_capacity = 2)
            EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_2,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            # Attempt 3rd enrollment: must raise CohortCapacityExceededError
            with pytest.raises(CohortCapacityExceededError):
                EnrollmentEngine.enroll_student(
                    tenant_id=self.tenant.id,
                    student_id=self.student_3,
                    course_id=self.course_a.id,
                    cohort_id=self.cohort_a1.id,
                )

    def test_cohort_mandatory_policy(self):
        with tenant_atomic(self.tenant.id):
            self.course_b.is_cohort_mandatory = True
            self.course_b.save()

            with pytest.raises(CohortMandatoryError):
                EnrollmentEngine.enroll_student(
                    tenant_id=self.tenant.id,
                    student_id=self.student_1,
                    course_id=self.course_b.id,
                    cohort_id=None,
                )

    def test_prerequisite_validation(self):
        with tenant_atomic(self.tenant.id):
            # CS102 requires CS101
            CoursePrerequisite.objects.create(
                tenant=self.tenant,
                course=self.course_b,
                prerequisite_course=self.course_a,
            )

            # Attempt to enroll in CS102 without completing CS101: fails
            with pytest.raises(PrerequisiteNotMetError):
                EnrollmentEngine.enroll_student(
                    tenant_id=self.tenant.id,
                    student_id=self.student_1,
                    course_id=self.course_b.id,
                )

            # Now complete CS101
            e1 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            EnrollmentEngine.activate_enrollment(e1.id, self.tenant.id)
            EnrollmentEngine.complete_enrollment(e1.id, self.tenant.id)

            # Re-attempt CS102: now succeeds!
            e2 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_b.id,
            )
            assert e2.status == EnrollmentStatus.ENROLLED

    def test_suspended_releases_capacity_and_reactivation_checks_capacity(self):
        with tenant_atomic(self.tenant.id):
            e1 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            e2 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_2,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            # Suspend e1: frees up 1 seat
            EnrollmentEngine.suspend_enrollment(e1.id, self.tenant.id)
            assert CourseEnrollment.objects.get(id=e1.id).status == EnrollmentStatus.SUSPENDED

            # Now student 3 can enroll into the freed seat
            e3 = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_3,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            assert e3.status == EnrollmentStatus.ENROLLED

            # Now cohort is full again (student_2 + student_3). Attempting to reactivate e1 must raise CohortCapacityExceededError!
            with pytest.raises(CohortCapacityExceededError):
                EnrollmentEngine.activate_enrollment(e1.id, self.tenant.id)

    def test_completed_is_terminal_state(self):
        with tenant_atomic(self.tenant.id):
            e = EnrollmentEngine.enroll_student(
                tenant_id=self.tenant.id,
                student_id=self.student_1,
                course_id=self.course_a.id,
                cohort_id=self.cohort_a1.id,
            )
            EnrollmentEngine.activate_enrollment(e.id, self.tenant.id)
            EnrollmentEngine.complete_enrollment(e.id, self.tenant.id)

            # Cannot reactivate or suspend
            with pytest.raises(InvalidStateTransitionError):
                EnrollmentEngine.activate_enrollment(e.id, self.tenant.id)

            with pytest.raises(InvalidStateTransitionError):
                EnrollmentEngine.suspend_enrollment(e.id, self.tenant.id)

    def test_database_composite_foreign_key_cross_course_mismatch_rejected(self):
        with tenant_atomic(self.tenant.id):
            # Try to insert CourseEnrollment with course_b and cohort_a1 (which belongs to course_a)
            # Model clean() and DB FK must prevent this
            with pytest.raises(ValidationError):
                CourseEnrollment.objects.create(
                    tenant=self.tenant,
                    student_id=self.student_1,
                    course=self.course_b,
                    cohort=self.cohort_a1,
                )

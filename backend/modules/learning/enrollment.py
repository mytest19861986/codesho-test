import uuid
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    Cohort,
    Course,
    CourseEnrollment,
    CoursePrerequisite,
    EnrollmentStatus,
)


class EnrollmentError(Exception):
    """Base exception for enrollment domain errors."""
    pass


class CohortCapacityExceededError(EnrollmentError):
    """Raised when the target cohort is full."""
    pass


class PrerequisiteNotMetError(EnrollmentError):
    """Raised when prerequisites for the course are not completed."""
    pass


class CohortMandatoryError(EnrollmentError):
    """Raised when a course requires a cohort but none was provided."""
    pass


class InvalidStateTransitionError(EnrollmentError):
    """Raised when an enrollment transition is illegal."""
    pass


class EnrollmentEngine:
    """
    Authoritative, atomic enrollment engine enforcing:
    1. select_for_update cohort capacity locks.
    2. Zero over-enrollment concurrency races.
    3. Directed Acyclic Graph (DAG) prerequisite checks.
    4. Exact state machine transitions (COMPLETED is terminal).
    5. Suspended -> Active re-admission capacity validation.
    """

    @staticmethod
    def get_cohort_live_enrollment_count(tenant_id: uuid.UUID, cohort_id: uuid.UUID) -> int:
        """Counts occupied capacity: ENROLLED and ACTIVE states only."""
        return CourseEnrollment.objects.filter(
            tenant_id=tenant_id,
            cohort_id=cohort_id,
            status__in=[EnrollmentStatus.ENROLLED, EnrollmentStatus.ACTIVE],
        ).count()

    @staticmethod
    def validate_prerequisites(tenant_id: uuid.UUID, student_id: uuid.UUID, course_id: uuid.UUID) -> None:
        """
        Validates that all prerequisite courses have been COMPLETED by the student.
        """
        required_prereqs = list(
            CoursePrerequisite.objects.filter(
                tenant_id=tenant_id,
                course_id=course_id,
            ).values_list("prerequisite_course_id", flat=True)
        )
        if not required_prereqs:
            return

        completed_prereqs = set(
            CourseEnrollment.objects.filter(
                tenant_id=tenant_id,
                student_id=student_id,
                course_id__in=required_prereqs,
                status=EnrollmentStatus.COMPLETED,
            ).values_list("course_id", flat=True)
        )

        missing = set(required_prereqs) - completed_prereqs
        if missing:
            raise PrerequisiteNotMetError(
                f"Student has not completed required prerequisites: {[str(m) for m in missing]}"
            )

    @staticmethod
    @transaction.atomic
    def enroll_student(
        tenant_id: uuid.UUID,
        student_id: uuid.UUID,
        course_id: uuid.UUID,
        cohort_id: Optional[uuid.UUID] = None,
        idempotency_key: Optional[str] = None,
    ) -> CourseEnrollment:
        """
        Atomically enrolls a student in a course and optionally a cohort.
        """
        # 1. Idempotency check
        if idempotency_key:
            existing = CourseEnrollment.objects.filter(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
            ).first()
            if existing:
                return existing

        # 2. Existing enrollment check (CourseEnrollment UNIQUE tenant, student, course)
        existing_enrollment = CourseEnrollment.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
            course_id=course_id,
        ).first()
        if existing_enrollment:
            return existing_enrollment

        # 3. Course validation
        course = Course.objects.filter(tenant_id=tenant_id, id=course_id).first()
        if not course:
            raise ValidationError("Course does not exist.")

        if course.is_cohort_mandatory and not cohort_id:
            raise CohortMandatoryError("This course requires selecting an active cohort.")

        # 4. Prerequisite DAG validation
        EnrollmentEngine.validate_prerequisites(tenant_id, student_id, course_id)

        # 5. Cohort capacity validation with select_for_update row lock
        cohort = None
        if cohort_id:
            cohort = Cohort.objects.select_for_update().filter(
                tenant_id=tenant_id,
                course_id=course_id,
                id=cohort_id,
                is_active=True,
            ).first()
            if not cohort:
                raise ValidationError("Cohort does not exist or is inactive.")

            current_count = CourseEnrollment.objects.filter(
                tenant_id=tenant_id,
                cohort_id=cohort_id,
                status__in=[EnrollmentStatus.ENROLLED, EnrollmentStatus.ACTIVE],
            ).count()

            if current_count >= cohort.max_capacity:
                raise CohortCapacityExceededError(
                    f"Cohort {cohort.code} is full (Capacity: {cohort.max_capacity}/{cohort.max_capacity})."
                )

        enrollment = CourseEnrollment.objects.create(
            tenant_id=tenant_id,
            student_id=student_id,
            course=course,
            cohort=cohort,
            status=EnrollmentStatus.ENROLLED,
            idempotency_key=idempotency_key,
        )
        return enrollment

    @staticmethod
    @transaction.atomic
    def activate_enrollment(enrollment_id: uuid.UUID, tenant_id: uuid.UUID) -> CourseEnrollment:
        """
        Transitions ENROLLED -> ACTIVE or SUSPENDED -> ACTIVE.
        If returning from SUSPENDED, re-validates cohort capacity under lock.
        """
        enrollment = CourseEnrollment.objects.select_for_update().filter(
            id=enrollment_id,
            tenant_id=tenant_id,
        ).first()
        if not enrollment:
            raise ValidationError("Enrollment not found.")

        if enrollment.status == EnrollmentStatus.COMPLETED:
            raise InvalidStateTransitionError("COMPLETED is a terminal state. Cannot re-activate.")

        if enrollment.status == EnrollmentStatus.ACTIVE:
            return enrollment

        if enrollment.status == EnrollmentStatus.SUSPENDED:
            # Re-admission: If cohort is attached, must re-validate capacity under select_for_update
            if enrollment.cohort_id:
                cohort = Cohort.objects.select_for_update().filter(
                    id=enrollment.cohort_id,
                    tenant_id=tenant_id,
                    is_active=True,
                ).first()
                if not cohort:
                    raise ValidationError("Attached cohort is no longer active.")

                current_count = CourseEnrollment.objects.filter(
                    tenant_id=tenant_id,
                    cohort_id=enrollment.cohort_id,
                    status__in=[EnrollmentStatus.ENROLLED, EnrollmentStatus.ACTIVE],
                ).count()

                if current_count >= cohort.max_capacity:
                    raise CohortCapacityExceededError(
                        f"Cannot reactivate: Cohort {cohort.code} is currently full."
                    )

        enrollment.status = EnrollmentStatus.ACTIVE
        if not enrollment.activated_at:
            enrollment.activated_at = timezone.now()
        enrollment.save(update_fields=["status", "activated_at", "updated_at"])
        return enrollment

    @staticmethod
    @transaction.atomic
    def suspend_enrollment(enrollment_id: uuid.UUID, tenant_id: uuid.UUID) -> CourseEnrollment:
        """
        Transitions ACTIVE or ENROLLED -> SUSPENDED, releasing occupied capacity.
        """
        enrollment = CourseEnrollment.objects.select_for_update().filter(
            id=enrollment_id,
            tenant_id=tenant_id,
        ).first()
        if not enrollment:
            raise ValidationError("Enrollment not found.")

        if enrollment.status == EnrollmentStatus.COMPLETED:
            raise InvalidStateTransitionError("Cannot suspend a completed enrollment.")

        enrollment.status = EnrollmentStatus.SUSPENDED
        enrollment.save(update_fields=["status", "updated_at"])
        return enrollment

    @staticmethod
    @transaction.atomic
    def complete_enrollment(enrollment_id: uuid.UUID, tenant_id: uuid.UUID) -> CourseEnrollment:
        """
        Transitions ACTIVE -> COMPLETED (Terminal state).
        Releases cohort capacity permanently.
        """
        enrollment = CourseEnrollment.objects.select_for_update().filter(
            id=enrollment_id,
            tenant_id=tenant_id,
        ).first()
        if not enrollment:
            raise ValidationError("Enrollment not found.")

        if enrollment.status == EnrollmentStatus.COMPLETED:
            return enrollment

        if enrollment.status not in [EnrollmentStatus.ACTIVE, EnrollmentStatus.ENROLLED]:
            raise InvalidStateTransitionError(
                f"Cannot complete enrollment from status '{enrollment.status}'."
            )

        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=["status", "completed_at", "updated_at"])
        return enrollment

import uuid
from decimal import Decimal
from typing import Optional, Dict, Any, List
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Q, Avg
from django.utils import timezone

from modules.learning.models import (
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
)


class CohortSupervisionAccessService:
    """
    Pattern A: Single-path enforcement service for cohort supervision.
    Guarantees strict 404 behavior for unauthorized mentor cohort requests
    to prevent cohort enumeration.
    """

    @classmethod
    def check_access(cls, tenant_id: str, mentor_id: str, cohort_id: str, is_admin: bool = False) -> Cohort:
        if not tenant_id or not cohort_id:
            raise Cohort.DoesNotExist("Missing tenant or cohort context.")

        cohort = Cohort.objects.filter(tenant_id=tenant_id, id=cohort_id).first()
        if not cohort:
            raise Cohort.DoesNotExist("Cohort not found.")

        if is_admin:
            return cohort

        # Verify active supervision mapping
        is_assigned = CohortSupervision.objects.filter(
            tenant_id=tenant_id,
            cohort_id=cohort_id,
            mentor_id=mentor_id,
            is_active=True,
        ).exists()

        if not is_assigned:
            # Pattern A: Raise DoesNotExist (404) rather than 403 to prevent ID enumeration
            raise Cohort.DoesNotExist("Cohort not found or unassigned.")

        return cohort


class CohortSupervisionService:
    """
    Core business logic for Cohort supervision, progress aggregation projection,
    and idempotent student supervision alert management.
    """

    @classmethod
    def assign_mentor(
        cls,
        tenant_id: str,
        cohort_id: str,
        mentor_id: str,
        assigned_by: Optional[str] = None,
        is_lead: bool = False,
    ) -> CohortSupervision:
        cohort = Cohort.objects.get(tenant_id=tenant_id, id=cohort_id)

        with transaction.atomic():
            if is_lead:
                # Deactivate any previous lead
                CohortSupervision.objects.filter(
                    tenant_id=tenant_id,
                    cohort_id=cohort_id,
                    is_lead=True,
                    is_active=True,
                ).update(is_lead=False)

            supervision, created = CohortSupervision.objects.update_or_create(
                tenant_id=tenant_id,
                cohort=cohort,
                mentor_id=mentor_id,
                defaults={
                    "is_active": True,
                    "is_lead": is_lead,
                    "assigned_by": assigned_by,
                    "revoked_at": None,
                    "revoked_by": None,
                },
            )
            return supervision

    @classmethod
    def revoke_mentor(
        cls,
        tenant_id: str,
        cohort_id: str,
        mentor_id: str,
        revoked_by: Optional[str] = None,
    ) -> bool:
        with transaction.atomic():
            updated = CohortSupervision.objects.filter(
                tenant_id=tenant_id,
                cohort_id=cohort_id,
                mentor_id=mentor_id,
                is_active=True,
            ).update(
                is_active=False,
                is_lead=False,
                revoked_at=timezone.now(),
                revoked_by=revoked_by,
            )
            return updated > 0

    @classmethod
    def refresh_cohort_progress_aggregate(
        cls,
        tenant_id: str,
        cohort_id: str,
    ) -> CohortProgressAggregate:
        """
        Calculates and updates the presentation-only projection of cohort progress.
        Authoritative FOR PRESENTATION READS ONLY — state transitions never read from this.
        """
        cohort = Cohort.objects.get(tenant_id=tenant_id, id=cohort_id)

        enrollments = CourseEnrollment.objects.filter(
            tenant_id=tenant_id,
            cohort=cohort,
        )

        total_enrolled = enrollments.count()
        active_students = enrollments.filter(status=EnrollmentStatus.ACTIVE).count()
        completed_students = enrollments.filter(status=EnrollmentStatus.COMPLETED).count()

        student_ids = list(enrollments.values_list("student_id", flat=True))

        # Progress percentages from course progress aggregates
        progress_aggs = CourseProgressAggregate.objects.filter(
            tenant_id=tenant_id,
            course_id=cohort.course_id,
            student_id__in=student_ids,
        )

        avg_progress = Decimal("0.00")
        if progress_aggs.exists():
            val = progress_aggs.aggregate(avg=Avg("progress_percentage"))["avg"]
            if val is not None:
                avg_progress = Decimal(str(round(val, 2)))

        # Average assessment scores
        avg_score = Decimal("0.00")
        results = AssessmentResult.objects.filter(
            tenant_id=tenant_id,
            student_id__in=student_ids,
            is_final=True,
        )
        if results.exists():
            val = results.aggregate(avg=Avg("score"))["avg"]
            if val is not None:
                avg_score = Decimal(str(round(val, 2)))

        completion_rate = Decimal("0.00")
        if total_enrolled > 0:
            completion_rate = Decimal(str(round((completed_students / total_enrolled) * 100, 2)))

        with transaction.atomic():
            aggregate, _ = CohortProgressAggregate.objects.update_or_create(
                tenant_id=tenant_id,
                cohort=cohort,
                defaults={
                    "total_enrolled": total_enrolled,
                    "active_students": active_students,
                    "completed_students": completed_students,
                    "average_progress_percentage": avg_progress,
                    "average_assessment_score": avg_score,
                    "completion_rate": completion_rate,
                },
            )
            return aggregate

    @classmethod
    def generate_or_update_alert(
        cls,
        tenant_id: str,
        cohort_id: str,
        student_id: str,
        alert_type: str,
        severity: str,
        details: Optional[Dict[str, Any]] = None,
        date_window: Optional[str] = None,
    ) -> StudentSupervisionAlert:
        """
        Generates or updates student supervision alert idempotently.
        Deduplication key format: f"{tenant_id}:{cohort_id}:{student_id}:{alert_type}:{date_window}"
        """
        if not date_window:
            date_window = timezone.now().strftime("%Y-%m-%d")

        dedup_key = f"{tenant_id}:{cohort_id}:{student_id}:{alert_type}:{date_window}"
        cohort = Cohort.objects.get(tenant_id=tenant_id, id=cohort_id)

        with transaction.atomic():
            alert, created = StudentSupervisionAlert.objects.get_or_create(
                deduplication_key=dedup_key,
                defaults={
                    "tenant_id": tenant_id,
                    "cohort": cohort,
                    "student_id": student_id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "status": StudentSupervisionAlertStatus.ACTIVE,
                    "details": details or {},
                },
            )
            return alert

    @classmethod
    def transition_alert_status(
        cls,
        tenant_id: str,
        alert_id: str,
        target_status: str,
        actor_id: Optional[str] = None,
    ) -> StudentSupervisionAlert:
        """
        FSM Transition logic:
        ACTIVE -> ACKNOWLEDGED (requires non-null actor_id and sets acknowledged_at)
        ACKNOWLEDGED -> RESOLVED (sets resolved_at)
        ACTIVE -> RESOLVED (automatic remediation)
        """
        with transaction.atomic():
            alert = StudentSupervisionAlert.objects.select_for_update().get(
                tenant_id=tenant_id,
                id=alert_id,
            )

            current = alert.status
            now = timezone.now()

            if current == StudentSupervisionAlertStatus.ACTIVE:
                if target_status == StudentSupervisionAlertStatus.ACKNOWLEDGED:
                    if not actor_id:
                        raise ValidationError("Actor ID is required to acknowledge an alert.")
                    alert.status = StudentSupervisionAlertStatus.ACKNOWLEDGED
                    alert.acknowledged_at = now
                    alert.acknowledged_by = actor_id
                elif target_status == StudentSupervisionAlertStatus.RESOLVED:
                    alert.status = StudentSupervisionAlertStatus.RESOLVED
                    alert.resolved_at = now
                    alert.resolved_by = actor_id
                else:
                    raise ValidationError(f"Invalid transition from {current} to {target_status}.")

            elif current == StudentSupervisionAlertStatus.ACKNOWLEDGED:
                if target_status == StudentSupervisionAlertStatus.RESOLVED:
                    alert.status = StudentSupervisionAlertStatus.RESOLVED
                    alert.resolved_at = now
                    alert.resolved_by = actor_id
                else:
                    raise ValidationError(f"Invalid transition from {current} to {target_status}.")

            elif current == StudentSupervisionAlertStatus.RESOLVED:
                raise ValidationError("Resolved alerts cannot be transitioned to another status.")

            alert.save()
            return alert

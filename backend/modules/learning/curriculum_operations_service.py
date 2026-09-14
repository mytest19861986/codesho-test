import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    CurriculumVersion,
    CurriculumVersionStatus,
    CourseRelease,
    ModuleReleaseSnapshot,
    LessonReleaseSnapshot,
    ReleaseApprovalRecord,
    CurriculumReleaseApprovalDecision,
    CurriculumReleaseAuditLog,
    CurriculumReleaseAuditAction,
    CohortSchedule,
    LearningSession,
    LearningSessionStatus,
    SessionOccurrence,
    SessionOccurrenceStatus,
    SessionAttendanceState,
    SessionAttendanceStatus,
    SessionChangeRecord,
    SessionChangeType,
    ProgramDeliveryAggregate,
    CurriculumReleaseCoverage,
    CohortScheduleHealth,
    CohortScheduleHealthStatus,
    DeliveryExceptionQueue,
    DeliveryExceptionSeverity,
    DeliveryExceptionStatus,
)
from modules.platform_event.services import append_outbox_event


class CurriculumOperationsService:
    """
    P3-MACRO-EPIC-20-22: Core service coordinating Curriculum Versioning & Release Governance,
    Cohort Scheduling & Session Orchestration, and Program Delivery Operations.
    """

    # =========================================================================
    # 1. P3-VS20: CURRICULUM VERSIONING & RELEASE GOVERNANCE
    # =========================================================================

    @classmethod
    def create_version(
        cls,
        *,
        tenant_id: UUID,
        course_id: UUID,
        semver_major: int,
        semver_minor: int,
        semver_patch: int,
        version_tag: str,
        actor_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CurriculumVersion:
        with transaction.atomic():
            version = CurriculumVersion.objects.create(
                tenant_id=tenant_id,
                course_id=course_id,
                semver_major=semver_major,
                semver_minor=semver_minor,
                semver_patch=semver_patch,
                version_tag=version_tag,
                status=CurriculumVersionStatus.DRAFT,
                created_by_id=actor_id,
                metadata=metadata or {},
            )

            CurriculumReleaseAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=actor_id or uuid.uuid4(),
                action=CurriculumReleaseAuditAction.VERSION_CREATED,
                curriculum_version=version,
                details={
                    "version_tag": version_tag,
                    "semver": f"{semver_major}.{semver_minor}.{semver_patch}",
                },
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.version.created",
                aggregate_type="CurriculumVersion",
                aggregate_id=str(version.id),
                payload={
                    "version_id": str(version.id),
                    "course_id": str(course_id),
                    "version_tag": version_tag,
                },
            )
            return version

    @classmethod
    def submit_version_for_review(
        cls,
        *,
        tenant_id: UUID,
        version_id: UUID,
        actor_id: Optional[UUID] = None,
    ) -> CurriculumVersion:
        with transaction.atomic():
            version = CurriculumVersion.objects.select_for_update().get(
                tenant_id=tenant_id, id=version_id
            )
            if version.status != CurriculumVersionStatus.DRAFT:
                raise ValidationError(
                    f"Cannot submit version in status {version.status} for review; must be DRAFT."
                )

            version.status = CurriculumVersionStatus.REVIEW
            version.save()

            CurriculumReleaseAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=actor_id or uuid.uuid4(),
                action=CurriculumReleaseAuditAction.VERSION_SUBMITTED,
                curriculum_version=version,
                details={"status": version.status},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.version.submitted_for_review",
                aggregate_type="CurriculumVersion",
                aggregate_id=str(version.id),
                payload={"version_id": str(version.id)},
            )
            return version

    @classmethod
    def record_approval(
        cls,
        *,
        tenant_id: UUID,
        version_id: UUID,
        reviewer_id: UUID,
        decision: str,
        comments: str = "",
    ) -> ReleaseApprovalRecord:
        with transaction.atomic():
            version = CurriculumVersion.objects.select_for_update().get(
                tenant_id=tenant_id, id=version_id
            )
            if version.status != CurriculumVersionStatus.REVIEW:
                raise ValidationError(
                    f"Cannot record approval for version in status {version.status}; must be REVIEW."
                )

            if decision not in (
                CurriculumReleaseApprovalDecision.APPROVED,
                CurriculumReleaseApprovalDecision.REJECTED,
                CurriculumReleaseApprovalDecision.CHANGES_REQUESTED,
            ):
                raise ValidationError(f"Invalid approval decision: {decision}")

            record = ReleaseApprovalRecord.objects.create(
                tenant_id=tenant_id,
                curriculum_version=version,
                reviewer_id=reviewer_id,
                decision=decision,
                review_comments=comments,
            )

            if decision == CurriculumReleaseApprovalDecision.APPROVED:
                version.status = CurriculumVersionStatus.APPROVED
                version.approved_by_id = reviewer_id
                action_type = CurriculumReleaseAuditAction.VERSION_APPROVED
            else:
                version.status = CurriculumVersionStatus.DRAFT
                action_type = CurriculumReleaseAuditAction.VERSION_REJECTED

            version.save()

            CurriculumReleaseAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=reviewer_id,
                action=action_type,
                curriculum_version=version,
                details={"decision": decision, "comments": comments},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.version.approval_recorded",
                aggregate_type="ReleaseApprovalRecord",
                aggregate_id=str(record.id),
                payload={
                    "version_id": str(version.id),
                    "decision": decision,
                    "reviewer_id": str(reviewer_id),
                },
            )
            return record

    @classmethod
    def publish_version(
        cls,
        *,
        tenant_id: UUID,
        version_id: UUID,
        actor_id: Optional[UUID] = None,
    ) -> CurriculumVersion:
        with transaction.atomic():
            version = CurriculumVersion.objects.select_for_update().get(
                tenant_id=tenant_id, id=version_id
            )
            if version.status != CurriculumVersionStatus.APPROVED:
                raise ValidationError(
                    f"Cannot publish version in status {version.status}; must be APPROVED."
                )

            now = timezone.now()
            version.status = CurriculumVersionStatus.PUBLISHED
            version.published_at = now
            version.save()

            CurriculumReleaseAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=actor_id or uuid.uuid4(),
                action=CurriculumReleaseAuditAction.VERSION_PUBLISHED,
                curriculum_version=version,
                details={"published_at": now.isoformat()},
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.version.published",
                aggregate_type="CurriculumVersion",
                aggregate_id=str(version.id),
                payload={
                    "version_id": str(version.id),
                    "course_id": str(version.course_id),
                    "published_at": now.isoformat(),
                },
            )
            return version

    @classmethod
    def create_course_release(
        cls,
        *,
        tenant_id: UUID,
        course_id: UUID,
        curriculum_version_id: UUID,
        release_title: str,
        release_notes: str = "",
        is_active_default: bool = False,
        actor_id: Optional[UUID] = None,
    ) -> CourseRelease:
        with transaction.atomic():
            version = CurriculumVersion.objects.get(
                tenant_id=tenant_id, id=curriculum_version_id
            )
            if version.status != CurriculumVersionStatus.PUBLISHED:
                raise ValidationError(
                    "Cannot create CourseRelease for non-PUBLISHED curriculum version."
                )

            if is_active_default:
                CourseRelease.objects.filter(
                    tenant_id=tenant_id, course_id=course_id, is_active_default=True
                ).update(is_active_default=False)

            release = CourseRelease.objects.create(
                tenant_id=tenant_id,
                course_id=course_id,
                curriculum_version=version,
                release_title=release_title,
                release_notes=release_notes,
                is_active_default=is_active_default,
            )

            CurriculumReleaseAuditLog.objects.create(
                tenant_id=tenant_id,
                actor_id=actor_id or uuid.uuid4(),
                action=CurriculumReleaseAuditAction.RELEASE_CREATED,
                course_release=release,
                details={
                    "release_title": release_title,
                    "is_active_default": is_active_default,
                },
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="curriculum.release.created",
                aggregate_type="CourseRelease",
                aggregate_id=str(release.id),
                payload={
                    "release_id": str(release.id),
                    "course_id": str(course_id),
                    "version_id": str(version.id),
                },
            )
            return release

    # =========================================================================
    # 2. P3-VS21: COHORT SCHEDULE & LEARNING SESSION ORCHESTRATION
    # =========================================================================

    @classmethod
    def create_cohort_schedule(
        cls,
        *,
        tenant_id: UUID,
        cohort_id: UUID,
        course_release_id: UUID,
        schedule_title: str,
        start_date: datetime,
        end_date: datetime,
        recurrence_rule: str = "WEEKLY",
        is_active: bool = True,
    ) -> CohortSchedule:
        with transaction.atomic():
            if start_date > end_date:
                raise ValidationError("start_date must be before or equal to end_date.")

            if is_active:
                CohortSchedule.objects.filter(
                    tenant_id=tenant_id, cohort_id=cohort_id, is_active=True
                ).update(is_active=False)

            schedule = CohortSchedule.objects.create(
                tenant_id=tenant_id,
                cohort_id=cohort_id,
                course_release_id=course_release_id,
                schedule_title=schedule_title,
                start_date=start_date,
                end_date=end_date,
                recurrence_rule=recurrence_rule,
                is_active=is_active,
            )

            CohortScheduleHealth.objects.create(
                tenant_id=tenant_id,
                cohort_schedule=schedule,
                health_status=CohortScheduleHealthStatus.ON_TRACK,
                pending_sessions_count=0,
                delayed_sessions_count=0,
                missed_occurrences_count=0,
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="cohort.schedule.created",
                aggregate_type="CohortSchedule",
                aggregate_id=str(schedule.id),
                payload={
                    "schedule_id": str(schedule.id),
                    "cohort_id": str(cohort_id),
                },
            )
            return schedule

    @classmethod
    def schedule_learning_session(
        cls,
        *,
        tenant_id: UUID,
        cohort_schedule_id: UUID,
        session_title: str,
        scheduled_start: datetime,
        scheduled_end: datetime,
        session_order: int = 1,
        lesson_snapshot_id: Optional[UUID] = None,
        assigned_mentor_id: Optional[UUID] = None,
    ) -> LearningSession:
        with transaction.atomic():
            if scheduled_start >= scheduled_end:
                raise ValidationError("scheduled_start must be before scheduled_end.")

            session = LearningSession.objects.create(
                tenant_id=tenant_id,
                cohort_schedule_id=cohort_schedule_id,
                lesson_snapshot_id=lesson_snapshot_id,
                session_title=session_title,
                session_order=session_order,
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                status=LearningSessionStatus.SCHEDULED,
                assigned_mentor_id=assigned_mentor_id,
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.session.scheduled",
                aggregate_type="LearningSession",
                aggregate_id=str(session.id),
                payload={
                    "session_id": str(session.id),
                    "cohort_schedule_id": str(cohort_schedule_id),
                    "scheduled_start": scheduled_start.isoformat(),
                },
            )
            return session

    @classmethod
    def reschedule_session(
        cls,
        *,
        tenant_id: UUID,
        session_id: UUID,
        new_start: datetime,
        new_end: datetime,
        changed_by_id: UUID,
        reason: str,
    ) -> LearningSession:
        with transaction.atomic():
            if new_start >= new_end:
                raise ValidationError("new_start must be before new_end.")

            session = LearningSession.objects.select_for_update().get(
                tenant_id=tenant_id, id=session_id
            )
            if session.status not in (
                LearningSessionStatus.SCHEDULED,
                LearningSessionStatus.RESCHEDULED,
            ):
                raise ValidationError(
                    f"Cannot reschedule session in status {session.status}."
                )

            orig_start = session.scheduled_start
            session.scheduled_start = new_start
            session.scheduled_end = new_end
            session.status = LearningSessionStatus.RESCHEDULED
            session.save()

            SessionChangeRecord.objects.create(
                tenant_id=tenant_id,
                learning_session=session,
                changed_by_id=changed_by_id,
                change_type=SessionChangeType.RESCHEDULED,
                original_start=orig_start,
                new_start=new_start,
                reason=reason,
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="learning.session.rescheduled",
                aggregate_type="LearningSession",
                aggregate_id=str(session.id),
                payload={
                    "session_id": str(session.id),
                    "new_start": new_start.isoformat(),
                    "reason": reason,
                },
            )
            return session

    @classmethod
    def record_occurrence(
        cls,
        *,
        tenant_id: UUID,
        session_id: UUID,
        actual_start: datetime,
        actual_end: Optional[datetime],
        occurrence_status: str,
        operational_notes: str = "",
    ) -> SessionOccurrence:
        with transaction.atomic():
            if occurrence_status not in (
                SessionOccurrenceStatus.CONDUCTED,
                SessionOccurrenceStatus.SUBSTITUTE_CONDUCTED,
                SessionOccurrenceStatus.MISSED,
            ):
                raise ValidationError(f"Invalid occurrence status: {occurrence_status}")

            if actual_end and actual_start > actual_end:
                raise ValidationError("actual_start must be before or equal to actual_end.")

            occurrence = SessionOccurrence.objects.create(
                tenant_id=tenant_id,
                learning_session_id=session_id,
                actual_start=actual_start,
                actual_end=actual_end,
                occurrence_status=occurrence_status,
                operational_notes=operational_notes,
            )

            session = LearningSession.objects.select_for_update().get(
                tenant_id=tenant_id, id=session_id
            )
            if occurrence_status in (
                SessionOccurrenceStatus.CONDUCTED,
                SessionOccurrenceStatus.SUBSTITUTE_CONDUCTED,
            ):
                session.status = LearningSessionStatus.COMPLETED
            elif occurrence_status == SessionOccurrenceStatus.MISSED:
                session.status = LearningSessionStatus.CANCELLED
            session.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="session.occurrence.recorded",
                aggregate_type="SessionOccurrence",
                aggregate_id=str(occurrence.id),
                payload={
                    "occurrence_id": str(occurrence.id),
                    "session_id": str(session_id),
                    "status": occurrence_status,
                },
            )
            return occurrence

    # =========================================================================
    # 3. P3-VS22: PROGRAM DELIVERY OPERATIONS & EXCEPTION MANAGEMENT
    # =========================================================================

    @classmethod
    def log_delivery_exception(
        cls,
        *,
        tenant_id: UUID,
        cohort_id: UUID,
        exception_type: str,
        severity: str,
        description: str,
        learning_session_id: Optional[UUID] = None,
    ) -> DeliveryExceptionQueue:
        with transaction.atomic():
            item = DeliveryExceptionQueue.objects.create(
                tenant_id=tenant_id,
                cohort_id=cohort_id,
                learning_session_id=learning_session_id,
                exception_type=exception_type,
                severity=severity,
                status=DeliveryExceptionStatus.OPEN,
                description=description,
            )

            append_outbox_event(
                tenant_id=tenant_id,
                topic="program.delivery.exception_logged",
                aggregate_type="DeliveryExceptionQueue",
                aggregate_id=str(item.id),
                payload={
                    "exception_id": str(item.id),
                    "cohort_id": str(cohort_id),
                    "severity": severity,
                },
            )
            return item

    @classmethod
    def resolve_delivery_exception(
        cls,
        *,
        tenant_id: UUID,
        exception_id: UUID,
        resolved_by_id: UUID,
        new_status: str = DeliveryExceptionStatus.RESOLVED,
    ) -> DeliveryExceptionQueue:
        with transaction.atomic():
            if new_status not in (
                DeliveryExceptionStatus.RESOLVED,
                DeliveryExceptionStatus.IGNORED,
            ):
                raise ValidationError("Resolution status must be RESOLVED or IGNORED.")

            item = DeliveryExceptionQueue.objects.select_for_update().get(
                tenant_id=tenant_id, id=exception_id
            )
            item.status = new_status
            item.resolved_by_id = resolved_by_id
            item.resolved_at = timezone.now()
            item.save()

            append_outbox_event(
                tenant_id=tenant_id,
                topic="program.delivery.exception_resolved",
                aggregate_type="DeliveryExceptionQueue",
                aggregate_id=str(item.id),
                payload={
                    "exception_id": str(item.id),
                    "status": new_status,
                    "resolved_by_id": str(resolved_by_id),
                },
            )
            return item

    @classmethod
    def refresh_program_delivery_aggregate(
        cls,
        *,
        tenant_id: UUID,
        cohort_id: UUID,
        active_release_version: str = "v1.0",
    ) -> ProgramDeliveryAggregate:
        with transaction.atomic():
            total_sessions = LearningSession.objects.filter(
                tenant_id=tenant_id, cohort_schedule__cohort_id=cohort_id
            ).count()
            completed_sessions = LearningSession.objects.filter(
                tenant_id=tenant_id,
                cohort_schedule__cohort_id=cohort_id,
                status=LearningSessionStatus.COMPLETED,
            ).count()
            cancelled_sessions = LearningSession.objects.filter(
                tenant_id=tenant_id,
                cohort_schedule__cohort_id=cohort_id,
                status=LearningSessionStatus.CANCELLED,
            ).count()
            rescheduled_sessions = LearningSession.objects.filter(
                tenant_id=tenant_id,
                cohort_schedule__cohort_id=cohort_id,
                status=LearningSessionStatus.RESCHEDULED,
            ).count()

            aggregate, _ = ProgramDeliveryAggregate.objects.update_or_create(
                tenant_id=tenant_id,
                cohort_id=cohort_id,
                defaults={
                    "total_sessions": total_sessions,
                    "completed_sessions": completed_sessions,
                    "cancelled_sessions": cancelled_sessions,
                    "rescheduled_sessions": rescheduled_sessions,
                    "active_release_version": active_release_version,
                    "is_authoritative": False,
                    "computed_at": timezone.now(),
                },
            )
            return aggregate

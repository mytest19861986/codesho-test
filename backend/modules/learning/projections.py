from __future__ import annotations

import logging
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.learning.events import DomainEvent, LearningDomainEvents
from modules.learning.models import (
    AssignmentSubmissionMetrics,
    Course,
    CourseProgressAggregate,
    Progress,
    ProgressState,
    ProjectionDeadLetterEvent,
    ProjectionWatermark,
    RoleActivityFeed,
    Submission,
    SubmissionState,
)

logger = logging.getLogger(__name__)


class ProjectionApplier:
    """
    Idempotent Projection Applier for P3-VS2.
    Processes canonical DomainEvents and updates derived projections safely.
    Zero-State-Drift: Aggregates strictly reflect authoritative tables.
    Includes Watermark monotonicity and Dead-Letter Event capture.
    """

    @classmethod
    @transaction.atomic
    def apply_event(cls, event: DomainEvent) -> bool:
        """
        Applies a DomainEvent idempotently.
        Returns True if applied, False if deduplicated or dead-lettered.
        """
        tenant_id = event.tenant_id
        event_id = event.event_id
        event_type = event.event_type
        payload = event.payload
        occurred_at = event.occurred_at

        # Watermark check for replay and monotonicity
        watermark = ProjectionWatermark.objects.filter(
            tenant_id=tenant_id,
            projection_name="learning_projections",
        ).first()

        if watermark:
            if watermark.last_event_id == event_id:
                # Direct event replay - safe deduplication
                return False
            if watermark.last_occurred_at and occurred_at < watermark.last_occurred_at:
                # Older out-of-order event, deduplicated to preserve monotonicity
                return False

        try:
            applied = False
            if event_type == LearningDomainEvents.LESSON_COMPLETED:
                applied = cls._apply_lesson_completed(tenant_id, event_id, payload, occurred_at)
            elif event_type == LearningDomainEvents.SUBMISSION_RECEIVED:
                applied = cls._apply_submission_received(tenant_id, event_id, payload, occurred_at)
            elif event_type == LearningDomainEvents.FEEDBACK_AVAILABLE:
                applied = cls._apply_feedback_available(tenant_id, event_id, payload, occurred_at)
            else:
                # Unknown event type captured into Dead Letter Queue
                ProjectionDeadLetterEvent.objects.update_or_create(
                    tenant_id=tenant_id,
                    event_id=event_id,
                    defaults={
                        "event_type": event_type,
                        "reason": f"Unknown event type: {event_type}",
                        "raw_payload_zero_pii": {k: str(v) for k, v in payload.items() if "name" not in k and "email" not in k},
                    },
                )
                return False

            if applied:
                ProjectionWatermark.objects.update_or_create(
                    tenant_id=tenant_id,
                    projection_name="learning_projections",
                    defaults={
                        "last_event_id": event_id,
                        "last_occurred_at": occurred_at,
                    },
                )
            return applied
        except Exception as exc:
            logger.exception("Failed to apply projection event %s: %s", event_id, exc)
            ProjectionDeadLetterEvent.objects.update_or_create(
                tenant_id=tenant_id,
                event_id=event_id,
                defaults={
                    "event_type": event_type,
                    "reason": str(exc)[:250],
                    "raw_payload_zero_pii": {k: str(v) for k, v in payload.items() if "name" not in k and "email" not in k},
                },
            )
            return False

    @classmethod
    def _apply_lesson_completed(
        cls, tenant_id: UUID, event_id: UUID, payload: dict, occurred_at: timezone.datetime
    ) -> bool:
        student_id = UUID(payload["student_id"])
        course_id = UUID(payload["course_id"])

        # Dedup: check if feed entry already exists for this event
        if RoleActivityFeed.objects.filter(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.STUDENT,
        ).exists():
            return False

        # Calculate authoritative progress numbers from source-of-truth tables
        total_lessons = (
            Course.objects.filter(tenant_id=tenant_id, id=course_id)
            .values_list("modules__lessons__id", flat=True)
            .distinct()
            .count()
        )
        completed_lessons = Progress.objects.filter(
            tenant_id=tenant_id,
            student_id=student_id,
            lesson__module__course_id=course_id,
            state=ProgressState.COMPLETED,
        ).count()

        percentage = int(completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        CourseProgressAggregate.objects.update_or_create(
            tenant_id=tenant_id,
            student_id=student_id,
            course_id=course_id,
            defaults={
                "total_lessons": total_lessons,
                "completed_lessons": completed_lessons,
                "progress_percentage": percentage,
                "last_event_id": event_id,
            },
        )

        # Append to RoleActivityFeed for student
        RoleActivityFeed.objects.create(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.STUDENT,
            user_id=student_id,
            activity_type="lesson_completed",
            summary="یک درس را با موفقیت تکمیل کردید",
            occurred_at=occurred_at,
        )

        # Also append to Parent feed
        RoleActivityFeed.objects.create(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.PARENT,
            user_id=student_id,  # references child
            activity_type="child_lesson_completed",
            summary="فرزند شما یک درس را تکمیل کرد",
            occurred_at=occurred_at,
        )
        return True

    @classmethod
    def _apply_submission_received(
        cls, tenant_id: UUID, event_id: UUID, payload: dict, occurred_at: timezone.datetime
    ) -> bool:
        student_id = UUID(payload["student_id"])
        assignment_id = UUID(payload["assignment_id"])

        if RoleActivityFeed.objects.filter(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.MENTOR,
        ).exists():
            return False

        # Compute authoritative counts for this assignment
        submitted_count = Submission.objects.filter(
            tenant_id=tenant_id, assignment_id=assignment_id, state=SubmissionState.SUBMITTED
        ).count()
        under_review_count = Submission.objects.filter(
            tenant_id=tenant_id, assignment_id=assignment_id, state=SubmissionState.UNDER_REVIEW
        ).count()
        reviewed_count = Submission.objects.filter(
            tenant_id=tenant_id, assignment_id=assignment_id, state=SubmissionState.REVIEWED
        ).count()

        AssignmentSubmissionMetrics.objects.update_or_create(
            tenant_id=tenant_id,
            assignment_id=assignment_id,
            defaults={
                "submitted_count": submitted_count,
                "under_review_count": under_review_count,
                "reviewed_count": reviewed_count,
                "last_event_id": event_id,
            },
        )

        # Add mentor feed
        RoleActivityFeed.objects.create(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.MENTOR,
            user_id=None,
            activity_type="submission_received",
            summary="تمرین جدید جهت بررسی دریافت شد",
            occurred_at=occurred_at,
        )

        # Add student feed
        RoleActivityFeed.objects.create(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.STUDENT,
            user_id=student_id,
            activity_type="assignment_submitted",
            summary="تمرین خود را با موفقیت ارسال کردید",
            occurred_at=occurred_at,
        )
        return True

    @classmethod
    def _apply_feedback_available(
        cls, tenant_id: UUID, event_id: UUID, payload: dict, occurred_at: timezone.datetime
    ) -> bool:
        student_id = UUID(payload["student_id"])
        mentor_id = UUID(payload["mentor_id"])

        if RoleActivityFeed.objects.filter(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.STUDENT,
        ).exists():
            return False

        RoleActivityFeed.objects.create(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.STUDENT,
            user_id=student_id,
            activity_type="feedback_received",
            summary="بازخورد مربی برای تمرین شما ثبت شد",
            occurred_at=occurred_at,
        )

        RoleActivityFeed.objects.create(
            tenant_id=tenant_id,
            source_event_id=event_id,
            target_role=RoleActivityFeed.ActivityRole.MENTOR,
            user_id=mentor_id,
            activity_type="feedback_delivered",
            summary="بازخورد شما برای دانش‌آموز ثبت گردید",
            occurred_at=occurred_at,
        )
        return True

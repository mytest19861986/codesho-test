from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from modules.learning.events import DomainEvent, LearningDomainEvents
from modules.learning.models import NotificationDeliveryState, NotificationItem
from modules.platform_tenant.context import current_tenant_id

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """
    Unified Outbox & Domain Event Notification Dispatcher for P3-VS3.
    Guarantees idempotent delivery effects, role-partitioned dispatching,
    and strict Zero-PII compliance.
    """

    MAX_RETRIES = 3

    @classmethod
    def dispatch_domain_event(cls, event: DomainEvent) -> list[NotificationItem]:
        """
        Dispatches domain events to role-specific in-app notifications idempotently.
        """
        tenant_id = event.tenant_id
        event_id = event.event_id
        event_type = event.event_type
        payload = event.payload or {}

        notifications: list[NotificationItem] = []

        with transaction.atomic():
            if event_type == LearningDomainEvents.ASSIGNMENT_PUBLISHED:
                assignment_id = event.aggregate_id
                course_id = payload.get("course_id")
                student_ids = payload.get("target_student_ids", [])
                title = "تکلیف جدید منتشر شد"
                message = f"تکلیف جدید در دوره آموزشی آماده انجام است."

                for student_id in student_ids:
                    idempotency_key = f"notif:{tenant_id}:{student_id}:{event_id}:assignment_published"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(student_id)),
                        role="student",
                        title=title,
                        message=message,
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=idempotency_key,
                    )
                    if item:
                        notifications.append(item)

            elif event_type == LearningDomainEvents.SUBMISSION_RECEIVED:
                submission_id = event.aggregate_id
                mentor_ids = payload.get("target_mentor_ids", [])
                title = "پاسخ تکلیف جدید دریافت شد"
                message = "یک پاسخ تکلیف جدید در صف بررسی مربی قرار گرفت."

                for mentor_id in mentor_ids:
                    idempotency_key = f"notif:{tenant_id}:{mentor_id}:{event_id}:submission_received"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(mentor_id)),
                        role="mentor",
                        title=title,
                        message=message,
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=idempotency_key,
                    )
                    if item:
                        notifications.append(item)

            elif event_type == LearningDomainEvents.FEEDBACK_AVAILABLE:
                student_id = payload.get("student_id")
                parent_id = payload.get("parent_id")
                title = "بازخورد مربی ثبت شد"
                message = "بازخورد و ارزیابی مربی برای تکلیف شما ثبت گردید."

                if student_id:
                    idempotency_key = f"notif:{tenant_id}:{student_id}:{event_id}:feedback_student"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(student_id)),
                        role="student",
                        title=title,
                        message=message,
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=idempotency_key,
                    )
                    if item:
                        notifications.append(item)

                if parent_id:
                    p_idempotency_key = f"notif:{tenant_id}:{parent_id}:{event_id}:feedback_parent"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(parent_id)),
                        role="parent",
                        title="گزارش بازخورد تحصیلی فرزند",
                        message="بازخورد جدیدی برای فعالیت آموزشی فرزند شما ثبت شد.",
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=p_idempotency_key,
                    )
                    if item:
                        notifications.append(item)

            elif event_type == LearningDomainEvents.LESSON_COMPLETED:
                student_id = payload.get("student_id")
                parent_id = payload.get("parent_id")
                title = "درس با موفقیت تکمیل شد"
                message = "پیشرفت تحصیلی جدید در درس ثبت شد."

                if student_id:
                    idempotency_key = f"notif:{tenant_id}:{student_id}:{event_id}:lesson_completed_student"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(student_id)),
                        role="student",
                        title=title,
                        message=message,
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=idempotency_key,
                    )
                    if item:
                        notifications.append(item)

                if parent_id:
                    p_idempotency_key = f"notif:{tenant_id}:{parent_id}:{event_id}:lesson_completed_parent"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(parent_id)),
                        role="parent",
                        title="پیشرفت تحصیلی فرزند",
                        message="فرزند شما یک درس آموزشی را با موفقیت به پایان رساند.",
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=p_idempotency_key,
                    )
                    if item:
                        notifications.append(item)

            elif event_type == LearningDomainEvents.MEDIA_ATTACHED:
                student_ids = payload.get("target_student_ids", [])
                title = "رسانه آموزشی جدید اضافه شد"
                message = "یک پیوست یا ویدیوی آموزشی جدید به درس متصل گردید."

                for student_id in student_ids:
                    idempotency_key = f"notif:{tenant_id}:{student_id}:{event_id}:media_attached"
                    item = cls._create_or_get_notification(
                        tenant_id=tenant_id,
                        user_id=UUID(str(student_id)),
                        role="student",
                        title=title,
                        message=message,
                        notification_type=event_type,
                        event_id=event_id,
                        idempotency_key=idempotency_key,
                    )
                    if item:
                        notifications.append(item)

        return notifications

    @classmethod
    def _create_or_get_notification(
        cls,
        tenant_id: UUID,
        user_id: UUID,
        role: str,
        title: str,
        message: str,
        notification_type: str,
        event_id: UUID,
        idempotency_key: str,
    ) -> NotificationItem | None:
        """
        Creates or updates NotificationItem adhering strictly to state machine.
        Idempotent: Duplicate executions return existing delivered item.
        """
        existing = NotificationItem.objects.filter(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        ).first()

        if existing:
            if existing.state == NotificationDeliveryState.DELIVERED:
                # Already delivered safely, no duplicate delivery
                return existing
            if existing.state == NotificationDeliveryState.FAILED and existing.retry_count >= cls.MAX_RETRIES:
                # Poisoned/exhausted
                return existing

        now = timezone.now()
        item, created = NotificationItem.objects.get_or_create(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            defaults={
                "user_id": user_id,
                "role": role,
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "event_id": event_id,
                "state": NotificationDeliveryState.DISPATCHING,
                "retry_count": 0,
            },
        )

        if not created:
            item.retry_count += 1
            item.state = NotificationDeliveryState.DISPATCHING

        # Mark delivered atomically
        item.state = NotificationDeliveryState.DELIVERED
        item.delivered_at = now
        item.save(update_fields=["state", "delivered_at", "retry_count"])
        return item

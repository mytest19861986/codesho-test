from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from django.utils import timezone


class DomainEvent:
    def __init__(
        self,
        event_type: str,
        tenant_id: UUID,
        aggregate_id: UUID,
        payload: dict[str, Any],
        event_id: UUID | None = None,
    ) -> None:
        self.event_id = event_id or uuid.uuid4()
        self.event_type = event_type
        self.tenant_id = tenant_id
        self.aggregate_id = aggregate_id
        self.payload = payload
        self.occurred_at = timezone.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "tenant_id": str(self.tenant_id),
            "aggregate_id": str(self.aggregate_id),
            "schema_version": 1,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self.payload,
        }


class LearningDomainEvents:
    ASSIGNMENT_PUBLISHED = "learning.assignment.published"
    SUBMISSION_RECEIVED = "learning.submission.received"
    SUBMISSION_REVIEW_STARTED = "learning.submission.review_started"
    SUBMISSION_REVIEWED = "learning.submission.reviewed"
    FEEDBACK_AVAILABLE = "learning.feedback.available"
    LESSON_COMPLETED = "learning.lesson.completed"
    MEDIA_ATTACHED = "learning.media.attached"

    @classmethod
    def media_attached(
        cls,
        tenant_id: UUID,
        media_id: UUID,
        lesson_id: UUID,
        title: str,
        storage_key: str,
    ) -> DomainEvent:
        # Enforce G3: Zero PII in event payload
        return DomainEvent(
            event_type=cls.MEDIA_ATTACHED,
            tenant_id=tenant_id,
            aggregate_id=media_id,
            payload={
                "lesson_id": str(lesson_id),
                "media_title": title,
                "storage_key": storage_key,
                "data_classification": "SYNTHETIC",
            },
        )

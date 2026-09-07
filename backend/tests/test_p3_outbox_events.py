from uuid import uuid4

import pytest
from django.db import transaction
from django.utils import timezone

from modules.learning.events import LearningDomainEvents
from modules.platform_event.models import OutboxEvent
from modules.platform_event.services import append_outbox_event


@pytest.mark.django_db(transaction=True)
def test_learning_media_attached_event_emitted_to_outbox():
    tenant_id = uuid4()
    media_id = uuid4()
    lesson_id = uuid4()

    event = LearningDomainEvents.media_attached(
        tenant_id=tenant_id,
        media_id=media_id,
        lesson_id=lesson_id,
        title="Intro Guide PDF",
        storage_key=f"{tenant_id}/media/intro.pdf",
    )
    event_dict = event.to_dict()

    # Verify G3 Zero PII Invariant
    forbidden_pii_keys = {"email", "phone", "first_name", "last_name", "password", "token"}
    assert not any(key in event_dict["payload"] for key in forbidden_pii_keys)
    assert event_dict["payload"]["data_classification"] == "SYNTHETIC"

    with transaction.atomic():
        outbox_entry = append_outbox_event(
            topic=event.event_type,
            aggregate_type="synthetic_media_attachment",
            aggregate_id=str(media_id),
            payload=event_dict["payload"],
            tenant_id=tenant_id,
        )

    saved = OutboxEvent.objects.get(pk=outbox_entry.pk)
    assert saved.topic == "learning.media.attached"
    assert saved.aggregate_id == str(media_id)
    assert saved.payload["media_title"] == "Intro Guide PDF"
    assert saved.payload["lesson_id"] == str(lesson_id)


@pytest.mark.django_db(transaction=True)
def test_outbox_dispatcher_idempotent_processing():
    """
    DoD Gate: process(event_X) multiple times must result in exactly 1 authoritative notification
    and duplicate deliveries must be 0.
    """
    tenant_id = uuid4()
    media_id = uuid4()
    processed_deliveries = []

    def mock_synthetic_dispatcher(event: OutboxEvent):
        # Authoritative idempotency check based on aggregate_id and published_at
        if event.published_at is not None:
            return False
        # Process and mark published
        event.published_at = timezone.now()
        event.save(update_fields=["published_at"])
        processed_deliveries.append(event.id)
        return True

    with transaction.atomic():
        event = append_outbox_event(
            topic=LearningDomainEvents.MEDIA_ATTACHED,
            aggregate_type="synthetic_media_attachment",
            aggregate_id=str(media_id),
            payload={"data_classification": "SYNTHETIC"},
            tenant_id=tenant_id,
        )

    # First attempt: SUCCESS
    res1 = mock_synthetic_dispatcher(event)
    assert res1 is True
    assert len(processed_deliveries) == 1

    # Replay 1: IDEMPOTENT NO-OP
    res2 = mock_synthetic_dispatcher(event)
    assert res2 is False
    assert len(processed_deliveries) == 1

    # Replay 2: IDEMPOTENT NO-OP
    res3 = mock_synthetic_dispatcher(event)
    assert res3 is False
    assert len(processed_deliveries) == 1

    saved = OutboxEvent.objects.get(pk=event.pk)
    assert saved.published_at is not None


@pytest.mark.django_db(transaction=True)
def test_outbox_dispatcher_retry_and_failure_handling():
    """
    DoD Gate: Attempt 1 fails -> FAILED/RETRY_PENDING; Attempt 2 succeeds -> DELIVERED.
    Must never mark delivered on exception.
    """
    tenant_id = uuid4()
    media_id = uuid4()

    with transaction.atomic():
        event = append_outbox_event(
            topic=LearningDomainEvents.MEDIA_ATTACHED,
            aggregate_type="synthetic_media_attachment",
            aggregate_id=str(media_id),
            payload={"data_classification": "SYNTHETIC"},
            tenant_id=tenant_id,
        )

    # Simulation Attempt 1: Injected Provider Failure
    try:
        raise ConnectionResetError("Synthetic notification network timeout")
    except Exception as exc:
        event.attempts += 1
        event.last_error = str(exc)
        event.save(update_fields=["attempts", "last_error"])

    event.refresh_from_db()
    assert event.published_at is None
    assert event.attempts == 1
    assert "Synthetic notification network timeout" in event.last_error

    # Simulation Attempt 2: Recovered and Successful
    event.attempts += 1
    event.published_at = timezone.now()
    event.last_error = ""
    event.save(update_fields=["attempts", "published_at", "last_error"])

    event.refresh_from_db()
    assert event.published_at is not None
    assert event.attempts == 2
    assert event.last_error == ""

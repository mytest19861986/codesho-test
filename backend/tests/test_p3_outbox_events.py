from uuid import uuid4
import pytest
from django.db import transaction
from modules.platform_event.models import OutboxEvent
from modules.platform_event.services import append_outbox_event
from modules.learning.events import LearningDomainEvents


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

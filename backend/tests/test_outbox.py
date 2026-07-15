from uuid import uuid4

import pytest
from django.db import transaction

from modules.platform_event.models import OutboxEvent
from modules.platform_event.services import append_outbox_event


@pytest.mark.django_db(transaction=True)
def test_outbox_requires_business_transaction():
    with pytest.raises(RuntimeError, match="business transaction"):
        append_outbox_event(
            topic="course.enrolled",
            aggregate_type="enrollment",
            aggregate_id="1",
            payload={},
            tenant_id=uuid4(),
        )


@pytest.mark.django_db(transaction=True)
def test_outbox_is_written_atomically():
    with transaction.atomic():
        event = append_outbox_event(
            topic="course.enrolled",
            aggregate_type="enrollment",
            aggregate_id="1",
            payload={"version": 1},
            tenant_id=uuid4(),
        )
    assert OutboxEvent.objects.get(pk=event.pk).payload == {"version": 1}

from uuid import uuid4

import pytest
from django.db import transaction

from modules.platform_event.models import OutboxEvent
from modules.platform_event.services import append_outbox_event
from modules.platform_tenant.context import tenant_atomic


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
    tenant_id = uuid4()
    with tenant_atomic(tenant_id):
        event = append_outbox_event(
            topic="course.enrolled",
            aggregate_type="enrollment",
            aggregate_id="1",
            payload={"version": 1},
            tenant_id=tenant_id,
        )
    assert OutboxEvent.objects.get(pk=event.pk).payload == {"version": 1}


@pytest.mark.django_db(transaction=True)
def test_tenant_outbox_event_requires_matching_context():
    with transaction.atomic(), pytest.raises(RuntimeError, match="matching tenant context"):
        append_outbox_event(
            topic="course.enrolled",
            aggregate_type="enrollment",
            aggregate_id="1",
            payload={},
            tenant_id=uuid4(),
        )


@pytest.mark.django_db(transaction=True)
def test_tenant_outbox_event_rejects_different_context():
    with tenant_atomic(uuid4()), pytest.raises(RuntimeError, match="matching tenant context"):
        append_outbox_event(
            topic="course.enrolled",
            aggregate_type="enrollment",
            aggregate_id="1",
            payload={},
            tenant_id=uuid4(),
        )

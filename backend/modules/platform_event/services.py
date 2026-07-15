from typing import Any
from uuid import UUID

from django.db import transaction

from .models import OutboxEvent


def append_outbox_event(
    *,
    topic: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    tenant_id: UUID | None,
) -> OutboxEvent:
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("Outbox events must be appended inside a business transaction")
    return OutboxEvent.objects.create(
        topic=topic,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        tenant_id=tenant_id,
    )

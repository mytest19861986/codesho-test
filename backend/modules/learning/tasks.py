from typing import Any
from uuid import UUID

from celery import shared_task

from modules.learning.events import DomainEvent
from modules.learning.notifications import NotificationDispatcher
from modules.platform_tenant.tasks import BaseTenantTask


class OutboxNotificationDispatcherTask(BaseTenantTask):
    """
    Tenant-aware Celery task for processing outbox events and delivering in-app notifications.
    Inherits from BaseTenantTask, strictly establishing fail-closed tenant context.
    """

    name = "learning.dispatch_outbox_notifications"
    atomic_run = True

    def run(self, event_data: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        tenant_id = kwargs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id must be provided in context")

        # Reconstruct DomainEvent
        event = DomainEvent(
            event_type=event_data["event_type"],
            tenant_id=UUID(str(tenant_id)),
            aggregate_id=UUID(str(event_data["aggregate_id"])),
            payload=event_data.get("payload", {}),
            event_id=UUID(str(event_data["event_id"])),
        )

        delivered_items = NotificationDispatcher.dispatch_domain_event(event)
        return {
            "status": "success",
            "delivered_count": len(delivered_items),
            "event_id": str(event.event_id),
        }

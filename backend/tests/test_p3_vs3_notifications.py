import uuid
import pytest
from django.utils import timezone

from modules.learning.events import DomainEvent, LearningDomainEvents
from modules.learning.models import NotificationDeliveryState, NotificationItem
from modules.learning.notifications import NotificationDispatcher
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_notification_dispatcher_lifecycle_and_idempotency():
    tenant = Tenant.objects.create(name="T1")
    student_id = uuid.uuid4()
    parent_id = uuid.uuid4()
    event_id = uuid.uuid4()

    event = DomainEvent(
        event_type=LearningDomainEvents.FEEDBACK_AVAILABLE,
        tenant_id=tenant.id,
        aggregate_id=uuid.uuid4(),
        payload={
            "student_id": str(student_id),
            "parent_id": str(parent_id),
        },
        event_id=event_id,
    )

    with tenant_atomic(tenant.id):
        # 1. First Dispatch
        items_1 = NotificationDispatcher.dispatch_domain_event(event)
        assert len(items_1) == 2

        student_notif = NotificationItem.objects.get(
            tenant=tenant, user_id=student_id, role="student"
        )
        parent_notif = NotificationItem.objects.get(
            tenant=tenant, user_id=parent_id, role="parent"
        )

        assert student_notif.state == NotificationDeliveryState.DELIVERED
        assert student_notif.delivered_at is not None
        assert student_notif.retry_count == 0

        assert parent_notif.state == NotificationDeliveryState.DELIVERED
        assert parent_notif.delivered_at is not None

        # 2. Duplicate Dispatch (Idempotent replay)
        items_2 = NotificationDispatcher.dispatch_domain_event(event)
        assert len(items_2) == 2

        # Assert no duplicate rows created
        total_student_items = NotificationItem.objects.filter(
            tenant=tenant, user_id=student_id
        ).count()
        assert total_student_items == 1

        total_parent_items = NotificationItem.objects.filter(
            tenant=tenant, user_id=parent_id
        ).count()
        assert total_parent_items == 1


@pytest.mark.django_db(transaction=True)
def test_notification_mark_as_read_workflow():
    tenant = Tenant.objects.create(name="T2")
    user_id = uuid.uuid4()

    with tenant_atomic(tenant.id):
        item = NotificationItem.objects.create(
            tenant=tenant,
            user_id=user_id,
            role="student",
            title="تست اعلان",
            message="متن تست",
            notification_type="test",
            state=NotificationDeliveryState.DELIVERED,
        )

        assert item.read_at is None

        now = timezone.now()
        item.read_at = now
        item.save(update_fields=["read_at"])

        refreshed = NotificationItem.objects.get(id=item.id)
        assert refreshed.read_at is not None

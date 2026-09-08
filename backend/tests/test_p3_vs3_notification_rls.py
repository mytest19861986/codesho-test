import uuid
import pytest
from django.core.exceptions import ValidationError

from modules.learning.models import NotificationDeliveryState, NotificationItem
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_notification_cross_tenant_isolation_negative():
    tenant1 = Tenant.objects.create(name="T1", slug=f"t1-{uuid.uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="T2", slug=f"t2-{uuid.uuid4().hex[:6]}")

    user1 = uuid.uuid4()
    user2 = uuid.uuid4()

    with tenant_atomic(tenant1.id):
        item1 = NotificationItem.objects.create(
            tenant=tenant1,
            user_id=user1,
            role="student",
            title="اعلان محرمانه مستأجر اول",
            message="اطلاعات درون مستأجر اول",
            notification_type="assignment",
            state=NotificationDeliveryState.DELIVERED,
            idempotency_key=f"t1:notif:{user1}:1",
        )

    # Tenant 2 query must return exactly 0 records
    with tenant_atomic(tenant2.id):
        t2_records = NotificationItem.objects.filter(tenant=tenant2)
        assert t2_records.count() == 0

        # Direct ID query with tenant2 must return nothing
        item_t2 = NotificationItem.objects.filter(tenant=tenant2, id=item1.id).first()
        assert item_t2 is None

        # Cross-tenant update must affect 0 rows
        updated_count = NotificationItem.objects.filter(
            tenant=tenant2, id=item1.id
        ).update(message="تغییر غیرمجاز")
        assert updated_count == 0

        # Cross-tenant delete must delete 0 rows
        deleted_count, _ = NotificationItem.objects.filter(
            tenant=tenant2, id=item1.id
        ).delete()
        assert deleted_count == 0

    # Ensure Tenant 1 data remains pristine
    with tenant_atomic(tenant1.id):
        refreshed = NotificationItem.objects.get(id=item1.id)
        assert refreshed.message == "اطلاعات درون مستأجر اول"

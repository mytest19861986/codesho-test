import uuid
import pytest

from modules.learning.gamification import GamificationEngine
from modules.learning.models import (
    BadgeDefinition,
    StudentBadgeAward,
    StudentProgressionProfile,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db(transaction=True)
def test_gamification_cross_tenant_isolation_negative():
    tenant1 = Tenant.objects.create(name="T1", slug=f"t1-{uuid.uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="T2", slug=f"t2-{uuid.uuid4().hex[:6]}")

    student1 = uuid.uuid4()
    student2 = uuid.uuid4()

    with tenant_atomic(tenant1.id):
        profile1, badges1 = GamificationEngine.handle_learning_event(
            tenant_id=tenant1.id,
            student_id=student1,
            event_type="lesson_completed",
            event_id=uuid.uuid4(),
        )
        award1 = badges1[0]

    # Querying under Tenant 2 MUST leak zero rows
    with tenant_atomic(tenant2.id):
        # 1. Progression profile query
        t2_profiles = StudentProgressionProfile.objects.filter(tenant=tenant2)
        assert t2_profiles.count() == 0

        # Querying tenant1's profile under tenant2
        leaked_profile = StudentProgressionProfile.objects.filter(tenant=tenant2, id=profile1.id).first()
        assert leaked_profile is None

        # 2. Badge awards query
        t2_awards = StudentBadgeAward.objects.filter(tenant=tenant2)
        assert t2_awards.count() == 0

        leaked_award = StudentBadgeAward.objects.filter(tenant=tenant2, id=award1.id).first()
        assert leaked_award is None

        # 3. Cross-tenant update must affect 0 rows
        updated_count = StudentProgressionProfile.objects.filter(
            tenant=tenant2, id=profile1.id
        ).update(total_xp=9999)
        assert updated_count == 0

        # 4. Cross-tenant delete must affect 0 rows
        deleted_count, _ = StudentBadgeAward.objects.filter(
            tenant=tenant2, id=award1.id
        ).delete()
        assert deleted_count == 0

    # Ensure Tenant 1 data remains untouched
    with tenant_atomic(tenant1.id):
        refreshed_profile = StudentProgressionProfile.objects.get(id=profile1.id)
        assert refreshed_profile.total_xp != 9999
        refreshed_award = StudentBadgeAward.objects.get(id=award1.id)
        assert refreshed_award is not None

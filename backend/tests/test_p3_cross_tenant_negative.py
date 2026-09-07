from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError

from modules.learning.models import (
    Course,
    Lesson,
    MediaFSMState,
    SyntheticMediaAttachment,
)
from modules.platform_tenant.models import Tenant


@pytest.mark.django_db
def test_cross_tenant_read_isolation():
    tenant1 = Tenant.objects.create(name="T1", slug=f"t1-{uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="T2", slug=f"t2-{uuid4().hex[:6]}")

    c1 = Course.objects.create(tenant=tenant1, code=f"C1-{uuid4().hex[:4]}", title="Course 1")
    l1 = Lesson.objects.create(
        tenant=tenant1, course=c1, code=f"L1-{uuid4().hex[:4]}", title="Lesson 1", position=1
    )

    SyntheticMediaAttachment.objects.create(
        tenant=tenant1,
        lesson=l1,
        title="T1 Secret Guide",
        storage_key=f"{tenant1.id}/media/guide.pdf",
        mime_type="application/pdf",
        file_size_bytes=1024,
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        state=MediaFSMState.READY,
    )

    # Tenant 2 query must return exactly 0 records
    t2_records = SyntheticMediaAttachment.objects.filter(tenant=tenant2)
    assert t2_records.count() == 0


@pytest.mark.django_db
def test_cross_tenant_update_and_delete_protection():
    tenant1 = Tenant.objects.create(name="T1", slug=f"t1-{uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="T2", slug=f"t2-{uuid4().hex[:6]}")

    c1 = Course.objects.create(tenant=tenant1, code=f"C1-{uuid4().hex[:4]}", title="Course 1")
    l1 = Lesson.objects.create(
        tenant=tenant1, course=c1, code=f"L1-{uuid4().hex[:4]}", title="Lesson 1", position=1
    )

    media = SyntheticMediaAttachment.objects.create(
        tenant=tenant1,
        lesson=l1,
        title="T1 Original Guide",
        storage_key=f"{tenant1.id}/media/guide.pdf",
        mime_type="application/pdf",
        file_size_bytes=1024,
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        state=MediaFSMState.READY,
    )

    # Attempting to mutate media tenant to Tenant 2 must fail composite validation
    media.tenant = tenant2
    with pytest.raises(ValidationError):
        media.clean()

    # Scope of Tenant 2 delete cannot delete Tenant 1 media
    deleted_count, _ = SyntheticMediaAttachment.objects.filter(tenant=tenant2, id=media.id).delete()
    assert deleted_count == 0
    assert SyntheticMediaAttachment.objects.filter(id=media.id).exists()

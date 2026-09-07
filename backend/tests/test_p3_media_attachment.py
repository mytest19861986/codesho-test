from uuid import uuid4
import pytest
from django.core.exceptions import ValidationError
from modules.platform_tenant.models import Tenant
from modules.learning.models import (
    Course,
    Lesson,
    MediaFSMState,
    SyntheticMediaAttachment,
)


@pytest.mark.django_db
def test_synthetic_media_attachment_creation_and_fsm():
    tenant = Tenant.objects.create(name="Tenant Alpha", slug=f"t-alpha-{uuid4().hex[:6]}")
    course = Course.objects.create(
        tenant=tenant,
        code=f"CRS-{uuid4().hex[:4]}",
        title="Intro to Python",
    )
    lesson = Lesson.objects.create(
        tenant=tenant,
        course=course,
        code=f"LSN-{uuid4().hex[:4]}",
        title="Variables",
        position=1,
    )

    valid_key = f"{tenant.id}/media/guide.pdf"
    media = SyntheticMediaAttachment.objects.create(
        tenant=tenant,
        lesson=lesson,
        title="Syntax Cheatsheet",
        storage_key=valid_key,
        mime_type="application/pdf",
        file_size_bytes=1024,
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        state=MediaFSMState.PENDING,
    )
    assert media.id is not None
    assert media.state == MediaFSMState.PENDING

    # Transition to READY
    media.state = MediaFSMState.READY
    media.save()
    assert media.state == MediaFSMState.READY


@pytest.mark.django_db
def test_storage_key_tenant_prefix_enforcement():
    tenant = Tenant.objects.create(name="Tenant Beta", slug=f"t-beta-{uuid4().hex[:6]}")
    course = Course.objects.create(
        tenant=tenant,
        code=f"CRS-{uuid4().hex[:4]}",
        title="Intro to Rust",
    )
    lesson = Lesson.objects.create(
        tenant=tenant,
        course=course,
        code=f"LSN-{uuid4().hex[:4]}",
        title="Ownership",
        position=1,
    )

    invalid_key = "unprefixed_folder/guide.pdf"
    with pytest.raises(ValidationError) as exc:
        SyntheticMediaAttachment.objects.create(
            tenant=tenant,
            lesson=lesson,
            title="Ownership Guide",
            storage_key=invalid_key,
            mime_type="application/pdf",
            file_size_bytes=2048,
            checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
    assert "storage_key" in exc.value.message_dict


@pytest.mark.django_db
def test_composite_tenant_integrity_rejection():
    tenant1 = Tenant.objects.create(name="Tenant One", slug=f"t-one-{uuid4().hex[:6]}")
    tenant2 = Tenant.objects.create(name="Tenant Two", slug=f"t-two-{uuid4().hex[:6]}")

    course1 = Course.objects.create(tenant=tenant1, code=f"C-{uuid4().hex[:4]}", title="Course 1")
    lesson1 = Lesson.objects.create(tenant=tenant1, course=course1, code=f"L-{uuid4().hex[:4]}", title="Lesson 1", position=1)

    # Attempt to attach lesson from tenant1 under tenant2
    with pytest.raises(ValidationError) as exc:
        SyntheticMediaAttachment.objects.create(
            tenant=tenant2,
            lesson=lesson1,
            title="Cross Tenant Exploit",
            storage_key=f"{tenant2.id}/media/exploit.pdf",
            mime_type="application/pdf",
            file_size_bytes=512,
            checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
    assert "lesson" in exc.value.message_dict

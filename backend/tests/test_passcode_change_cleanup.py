from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.utils import timezone

from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.identity.passcode_change_cleanup import (
    CleanupResult,
    cleanup_passcode_change_challenges,
)
from modules.identity.tasks import cleanup_passcode_change_challenges_task
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


def make_challenge(*, tenant, state="active", expires_at=None, expired_at=None):
    user = User.objects.create_user(username=str(uuid4()), email=f"{uuid4()}@example.com")
    credential = PasscodeCredential.objects.create(user=user, encoded_hash="x", pepper_id="v1")
    now = timezone.now()
    values = dict(
        selector=uuid4(), tenant=tenant, credential=credential, credential_version=1,
        pepper_id="v1", issued_at=now - timedelta(seconds=600), expires_at=expires_at or now,
        state=state, secret_digest=b"x" * 32,
    )
    if state == "expired":
        values.update(secret_digest=None, expired_at=expired_at or now)
    with tenant_atomic(tenant.id):
        return PasscodeChangeChallenge.objects.create(**values)


@pytest.mark.django_db(transaction=True)
def test_cleanup_expires_rows_and_nulls_digest_before_audit():
    tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T")
    challenge = make_challenge(tenant=tenant, expires_at=timezone.now() - timedelta(seconds=1))
    with patch("modules.identity.passcode_change_cleanup.append_security_event") as audit:
        result = cleanup_passcode_change_challenges(tenant=tenant)
    with tenant_atomic(tenant.id):
        challenge.refresh_from_db()
    assert result.expired == 1
    assert challenge.state == PasscodeChangeChallenge.State.EXPIRED
    assert challenge.secret_digest is None and challenge.expired_at is not None
    audit.assert_called_once()


@pytest.mark.django_db(transaction=True)
def test_cleanup_rolls_back_expiry_when_audit_fails():
    tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T")
    challenge = make_challenge(tenant=tenant, expires_at=timezone.now() - timedelta(seconds=1))
    with (
        patch(
            "modules.identity.passcode_change_cleanup.append_security_event",
            side_effect=RuntimeError,
        ),
        pytest.raises(RuntimeError),
    ):
        cleanup_passcode_change_challenges(tenant=tenant)
    with tenant_atomic(tenant.id):
        challenge.refresh_from_db()
    assert challenge.state == PasscodeChangeChallenge.State.ACTIVE
    assert challenge.secret_digest is not None


@pytest.mark.django_db(transaction=True)
def test_cleanup_never_deletes_active_rows_even_after_retention_cutoff():
    tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T")
    challenge = make_challenge(tenant=tenant, expires_at=timezone.now() + timedelta(days=1))
    cleanup_passcode_change_challenges(tenant=tenant)
    with tenant_atomic(tenant.id):
        assert PasscodeChangeChallenge.objects.filter(pk=challenge.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_cleanup_respects_batch_limit_and_deletes_only_old_terminal_metadata():
    tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T")
    first = make_challenge(tenant=tenant, expires_at=timezone.now() - timedelta(seconds=2))
    second = make_challenge(tenant=tenant, expires_at=timezone.now() - timedelta(seconds=1))
    old_terminal = make_challenge(
        tenant=tenant,
        state="expired",
        expired_at=timezone.now() - timedelta(days=31),
    )
    with patch("modules.identity.passcode_change_cleanup.append_security_event"):
        result = cleanup_passcode_change_challenges(tenant=tenant, batch_size=1)
    with tenant_atomic(tenant.id):
        first.refresh_from_db()
        second.refresh_from_db()
        assert not PasscodeChangeChallenge.objects.filter(pk=old_terminal.pk).exists()
    assert result.expired == 1 and result.deleted == 1
    assert first.state == PasscodeChangeChallenge.State.EXPIRED
    assert second.state == PasscodeChangeChallenge.State.ACTIVE


@pytest.mark.django_db(transaction=True)
def test_cleanup_is_tenant_scoped():
    first_tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T1")
    second_tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T2")
    own = make_challenge(tenant=first_tenant, expires_at=timezone.now() - timedelta(seconds=1))
    other = make_challenge(tenant=second_tenant, expires_at=timezone.now() - timedelta(seconds=1))
    with patch("modules.identity.passcode_change_cleanup.append_security_event"):
        cleanup_passcode_change_challenges(tenant=first_tenant)
    with tenant_atomic(first_tenant.id):
        own.refresh_from_db()
    with tenant_atomic(second_tenant.id):
        other.refresh_from_db()
    assert own.state == PasscodeChangeChallenge.State.EXPIRED
    assert other.state == PasscodeChangeChallenge.State.ACTIVE


@pytest.mark.django_db(transaction=True)
def test_cleanup_task_inherits_and_clears_tenant_context():
    tenant = Tenant.objects.create(slug=f"t-{uuid4()}", name="T")
    expected = {"expired": 0, "deleted": 0}
    with patch(
        "modules.identity.tasks.cleanup_passcode_change_challenges",
        return_value=CleanupResult(**expected),
    ) as cleanup:
        assert cleanup_passcode_change_challenges_task(tenant_id=str(tenant.id)) == expected
    cleanup.assert_called_once_with(tenant=tenant, batch_size=None)

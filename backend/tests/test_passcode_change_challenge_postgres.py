from datetime import timedelta
from uuid import uuid4

import pytest
from django.db import IntegrityError, connection
from django.utils import timezone
from psycopg.errors import CheckViolation, InsufficientPrivilege

from modules.identity.challenge import digest_challenge_secret, generate_challenge_material
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


def require_postgres() -> None:
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific passcode-change foundation contract")


def challenge_factory(**overrides):
    tenant = overrides.pop("tenant", Tenant.objects.create(slug=f"tenant-{uuid4()}", name="Tenant"))
    user = User.objects.create_user(username=f"user-{uuid4()}", email=f"{uuid4()}@example.com")
    credential = overrides.pop(
        "credential",
        PasscodeCredential.objects.create(
            user=user,
            encoded_hash="unused-for-challenge-foundation",
            pepper_id="test-v1",
        ),
    )
    material = generate_challenge_material()
    values = {
        "selector": material.selector,
        "tenant": tenant,
        "credential": credential,
        "credential_version": credential.credential_version,
        "purpose": PasscodeChangeChallenge.Purpose.FORCED_PASSCODE_CHANGE,
        "secret_digest": digest_challenge_secret(material.secret, "test-v1"),
        "pepper_id": "test-v1",
        "state": PasscodeChangeChallenge.State.ACTIVE,
    }
    values.update(overrides)
    with tenant_atomic(tenant.pk):
        return PasscodeChangeChallenge.objects.create(**values)


@pytest.mark.django_db(transaction=True)
def test_exact_database_ttl_invariant_rejects_non_600_second_expiry():
    require_postgres()
    now = timezone.now()
    with pytest.raises((CheckViolation, IntegrityError)):
        challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=599))


@pytest.mark.django_db(transaction=True)
def test_database_rejects_non_sha256_digest_size():
    require_postgres()
    now = timezone.now()
    with pytest.raises((CheckViolation, IntegrityError)):
        challenge_factory(
            secret_digest=b"wrong-length",
            issued_at=now,
            expires_at=now + timedelta(seconds=600),
        )


@pytest.mark.django_db(transaction=True)
def test_challenge_rls_fails_closed_and_does_not_leak_across_reused_connection():
    require_postgres()
    now = timezone.now()
    first = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    second = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    with tenant_atomic(first.tenant_id):
        assert PasscodeChangeChallenge.objects.filter(pk=first.pk).count() == 1
        assert PasscodeChangeChallenge.objects.filter(pk=second.pk).count() == 0
    assert PasscodeChangeChallenge.objects.filter(pk=first.pk).count() == 0
    with tenant_atomic(second.tenant_id):
        assert PasscodeChangeChallenge.objects.filter(pk=first.pk).count() == 0
        assert PasscodeChangeChallenge.objects.filter(pk=second.pk).count() == 1


@pytest.mark.django_db(transaction=True)
def test_runtime_role_has_no_delete_truncate_ddl_or_bypass_rls_capability():
    require_postgres()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT has_table_privilege("
            "current_user, 'identity_passcodechangechallenge', 'DELETE'), "
            "has_table_privilege("
            "current_user, 'identity_passcodechangechallenge', 'TRUNCATE')"
        )
        assert cursor.fetchone() == (False, False)
        cursor.execute(
            "SELECT has_schema_privilege("
            "'codesho_runtime', current_schema(), 'CREATE')"
        )
        assert cursor.fetchone()[0] is False
        cursor.execute("SET row_security = off")
        with pytest.raises(InsufficientPrivilege):
            cursor.execute("SELECT count(*) FROM identity_passcodechangechallenge")


@pytest.mark.django_db(transaction=True)
def test_challenge_table_is_migrator_owned_and_runtime_is_not_bypassrls():
    require_postgres()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT tableowner FROM pg_tables WHERE schemaname = current_schema() "
            "AND tablename = 'identity_passcodechangechallenge'"
        )
        assert cursor.fetchone()[0] == "codesho_migrator"
        cursor.execute(
            "SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = 'codesho_runtime'"
        )
        assert cursor.fetchone()[0] is False

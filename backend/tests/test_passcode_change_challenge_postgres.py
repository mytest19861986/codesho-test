import os
from datetime import timedelta
from threading import Barrier, Thread
from uuid import uuid4

import pytest
from django.db import IntegrityError, close_old_connections, connection
from django.utils import timezone
from psycopg import connect
from psycopg.errors import CheckViolation, InsufficientPrivilege

from config.passcode_change_issuance import issue_forced_passcode_change_challenge
from modules.identity.challenge import digest_challenge_secret, generate_challenge_material
from modules.identity.models import PasscodeChangeChallenge, PasscodeCredential, User
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant


def require_postgres() -> None:
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific passcode-change foundation contract")


@pytest.fixture
def runtime_connection():
    require_postgres()
    runtime_url = os.environ.get("DATABASE_RUNTIME_TEST_URL")
    if not runtime_url:
        pytest.skip("explicit runtime test URL is not configured")
    with connect(runtime_url, autocommit=False) as runtime:
        with runtime.cursor() as cursor:
            cursor.execute("SELECT current_user")
            assert cursor.fetchone()[0] == "codesho_runtime"
        with connection.cursor() as lifecycle:
            lifecycle.execute("SELECT current_user")
            assert lifecycle.fetchone()[0] == "codesho_migrator"
        yield runtime
        runtime.rollback()


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
def test_challenge_rls_fails_closed_and_does_not_leak_across_reused_connection(runtime_connection):
    require_postgres()
    now = timezone.now()
    first = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    second = challenge_factory(issued_at=now, expires_at=now + timedelta(seconds=600))
    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM identity_passcodechangechallenge")
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(first.tenant_id)])
        cursor.execute(
            "SELECT count(*) FROM identity_passcodechangechallenge WHERE id = %s", [first.pk]
        )
        assert cursor.fetchone()[0] == 1
        cursor.execute(
            "SELECT count(*) FROM identity_passcodechangechallenge WHERE id = %s", [second.pk]
        )
        assert cursor.fetchone()[0] == 0
    runtime_connection.rollback()
    with runtime_connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM identity_passcodechangechallenge")
        assert cursor.fetchone()[0] == 0


@pytest.mark.django_db(transaction=True)
def test_runtime_role_has_no_delete_truncate_ddl_or_bypass_rls_capability(runtime_connection):
    with runtime_connection.cursor() as cursor:
        cursor.execute(
            "SELECT has_table_privilege("
            "current_user, 'identity_passcodechangechallenge', 'DELETE'), "
            "has_table_privilege("
            "current_user, 'identity_passcodechangechallenge', 'TRUNCATE'), "
            "has_column_privilege("
            "current_user, 'identity_passcodechangechallenge', 'state', 'UPDATE'), "
            "has_column_privilege("
            "current_user, 'identity_passcodechangechallenge', 'tenant_id', 'UPDATE')"
        )
        assert cursor.fetchone() == (False, False, True, False)
        cursor.execute("SELECT has_schema_privilege('codesho_runtime', current_schema(), 'CREATE')")
        assert cursor.fetchone()[0] is False
        # Runtime has SELECT; FORCE RLS must reject a bypass attempt itself.
        cursor.execute("SET LOCAL row_security = off")
        with pytest.raises(InsufficientPrivilege):
            cursor.execute("SELECT count(*) FROM identity_passcodechangechallenge")


@pytest.mark.django_db(transaction=True)
def test_challenge_table_is_migrator_owned_and_runtime_is_not_bypassrls(runtime_connection):
    with runtime_connection.cursor() as cursor:
        cursor.execute(
            "SELECT tableowner FROM pg_tables WHERE schemaname = current_schema() "
            "AND tablename = 'identity_passcodechangechallenge'"
        )
        assert cursor.fetchone()[0] == "codesho_migrator"
        cursor.execute(
            "SELECT rolsuper OR rolbypassrls FROM pg_roles WHERE rolname = 'codesho_runtime'"
        )
        assert cursor.fetchone()[0] is False


@pytest.mark.django_db(transaction=True)
def test_parallel_issuance_serializes_to_one_active_challenge():
    require_postgres()
    tenant = Tenant.objects.create(slug=f"tenant-{uuid4()}", name="Tenant")
    user = User.objects.create_user(username=f"user-{uuid4()}", email=f"{uuid4()}@example.com")
    credential = PasscodeCredential.objects.create(
        user=user,
        encoded_hash="unused-for-concurrency-test",
        pepper_id="test-v1",
    )
    start = Barrier(2)
    results: list[BaseException | None] = []

    def issue_in_parallel() -> None:
        close_old_connections()
        try:
            local_user = User.objects.get(pk=user.pk)
            local_credential = PasscodeCredential.objects.get(pk=credential.pk)
            start.wait(timeout=10)
            issue_forced_passcode_change_challenge(
                tenant=tenant,
                user=local_user,
                credential=local_credential,
                correlation_id=uuid4(),
            )
            results.append(None)
        except BaseException as exc:  # pragma: no cover - asserted by parent thread
            results.append(exc)
        finally:
            close_old_connections()

    first = Thread(target=issue_in_parallel)
    second = Thread(target=issue_in_parallel)
    first.start()
    second.start()
    first.join(timeout=20)
    second.join(timeout=20)
    assert not first.is_alive() and not second.is_alive()
    assert results == [None, None]
    with tenant_atomic(tenant.id):
        challenges = list(
            PasscodeChangeChallenge.objects.filter(credential=credential).order_by("issued_at")
        )
    assert len(challenges) == 2
    assert [challenge.state for challenge in challenges] == [
        PasscodeChangeChallenge.State.REVOKED,
        PasscodeChangeChallenge.State.ACTIVE,
    ]
    assert challenges[0].secret_digest is None and challenges[0].revoked_at is not None

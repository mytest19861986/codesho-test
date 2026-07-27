from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from threading import Barrier, Thread
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from django.db import DatabaseError, IntegrityError, close_old_connections, connection, transaction
from django.db.migrations.exceptions import IrreversibleError
from psycopg import connect
from psycopg.errors import InsufficientPrivilege, RaiseException

from modules.identity.models import (
    AdultAgeAttestation,
    AdultAttestationProvenance,
    PasscodeCredential,
    SyntheticBootstrapRequest,
    User,
)
from modules.identity.synthetic_bootstrap import (
    SyntheticBootstrapConflict,
    SyntheticBootstrapNotAuthorized,
    bootstrap_synthetic_account,
)
from modules.platform_event.security_audit import AppendAuditResult, SecurityAuditError
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import Tenant, TenantMembership


@dataclass(frozen=True)
class BootstrapInputs:
    tenant_id: UUID
    attestation_id: UUID
    provenance_id: UUID
    idempotency_key: UUID


@pytest.fixture
def bootstrap_inputs(settings, db) -> BootstrapInputs:
    settings.ADULT_SIGNUP_MODE = "internal_test"
    tenant = Tenant.objects.create(slug=f"synthetic-{uuid4().hex[:12]}", name="Synthetic")
    subject_id = uuid4()
    with tenant_atomic(tenant.id):
        attestation = AdultAgeAttestation.objects.create(
            tenant_id=tenant.id,
            subject_id=subject_id,
            policy_version="adult-internal-2026-07-26",
        )
        provenance = AdultAttestationProvenance.objects.create(
            tenant_id=tenant.id,
            attestation=attestation,
        )
    return BootstrapInputs(tenant.id, attestation.id, provenance.id, uuid4())


def append_success(*args, **kwargs) -> AppendAuditResult:
    return AppendAuditResult(event_id=kwargs.get("event_id"), created=True)


@pytest.mark.django_db
def test_same_tenant_bootstrap_is_dormant_and_opaque(bootstrap_inputs):
    with patch(
        "modules.identity.synthetic_bootstrap.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ):
        result = bootstrap_synthetic_account(
            tenant_id=bootstrap_inputs.tenant_id,
            attestation_id=bootstrap_inputs.attestation_id,
            provenance_id=bootstrap_inputs.provenance_id,
            idempotency_key=bootstrap_inputs.idempotency_key,
        )

    user = User.objects.get(pk=result.user_id)
    membership = TenantMembership.objects.get(pk=result.membership_id)
    request = SyntheticBootstrapRequest.objects.get(pk=result.request_id)
    assert user.identity_mode == User.IdentityMode.SYNTHETIC
    assert user.synthetic_handle is not None
    assert user.username is None
    assert user.email is None
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.is_active is False
    assert user.has_usable_password() is False
    assert membership.is_active is False
    assert membership.role is None
    assert membership.is_synthetic_bootstrap is True
    assert request.state == SyntheticBootstrapRequest.State.COMPLETED
    assert PasscodeCredential.objects.filter(user=user).exists() is False


@pytest.mark.django_db
def test_identical_replay_returns_same_terminal_result(bootstrap_inputs):
    with patch(
        "modules.identity.synthetic_bootstrap.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ):
        first = bootstrap_synthetic_account(**bootstrap_inputs.__dict__)
        second = bootstrap_synthetic_account(**bootstrap_inputs.__dict__)

    assert second.replayed is True
    assert second == first.__class__(
        request_id=first.request_id,
        user_id=first.user_id,
        membership_id=first.membership_id,
        audit_event_id=first.audit_event_id,
        replayed=True,
    )
    assert User.objects.filter(identity_mode=User.IdentityMode.SYNTHETIC).count() == 1
    assert SyntheticBootstrapRequest.objects.count() == 1


@pytest.mark.django_db
def test_changed_replay_and_duplicate_attestation_fail_closed(bootstrap_inputs):
    with patch(
        "modules.identity.synthetic_bootstrap.append_security_event",
        return_value=AppendAuditResult(event_id=uuid4(), created=True),
    ):
        bootstrap_synthetic_account(**bootstrap_inputs.__dict__)
        with pytest.raises(SyntheticBootstrapConflict):
            bootstrap_synthetic_account(
                tenant_id=bootstrap_inputs.tenant_id,
                attestation_id=bootstrap_inputs.attestation_id,
                provenance_id=bootstrap_inputs.provenance_id,
                idempotency_key=uuid4(),
            )
        with pytest.raises(SyntheticBootstrapConflict):
            bootstrap_synthetic_account(
                tenant_id=bootstrap_inputs.tenant_id,
                attestation_id=uuid4(),
                provenance_id=bootstrap_inputs.provenance_id,
                idempotency_key=bootstrap_inputs.idempotency_key,
            )


@pytest.mark.django_db
def test_missing_or_cross_tenant_attestation_and_provenance_fail_closed(
    bootstrap_inputs,
):
    with pytest.raises(SyntheticBootstrapConflict):
        bootstrap_synthetic_account(
            tenant_id=bootstrap_inputs.tenant_id,
            attestation_id=uuid4(),
            provenance_id=bootstrap_inputs.provenance_id,
            idempotency_key=bootstrap_inputs.idempotency_key,
        )

    other = Tenant.objects.create(slug=f"other-{uuid4().hex[:12]}", name="Other")
    with tenant_atomic(other.id):
        attestation = AdultAgeAttestation.objects.create(
            tenant_id=other.id,
            subject_id=uuid4(),
            policy_version="adult-internal-2026-07-26",
        )
        provenance = AdultAttestationProvenance.objects.create(
            tenant_id=other.id,
            attestation=attestation,
        )
    with pytest.raises(SyntheticBootstrapConflict):
        bootstrap_synthetic_account(
            tenant_id=bootstrap_inputs.tenant_id,
            attestation_id=attestation.id,
            provenance_id=provenance.id,
            idempotency_key=bootstrap_inputs.idempotency_key,
        )


@pytest.mark.django_db
def test_audit_failure_rolls_back_every_bootstrap_row(bootstrap_inputs):
    with patch(
        "modules.identity.synthetic_bootstrap.append_security_event",
        side_effect=SecurityAuditError("audit unavailable"),
    ), pytest.raises(SecurityAuditError):
        bootstrap_synthetic_account(**bootstrap_inputs.__dict__)

    assert User.objects.count() == 0
    assert TenantMembership.objects.count() == 0
    assert SyntheticBootstrapRequest.objects.count() == 0


@pytest.mark.django_db
def test_internal_mode_is_required(settings, bootstrap_inputs):
    settings.ADULT_SIGNUP_MODE = "disabled"
    with pytest.raises(SyntheticBootstrapNotAuthorized):
        bootstrap_synthetic_account(**bootstrap_inputs.__dict__)


@pytest.mark.django_db
def test_database_constraints_reject_prohibited_identity_and_active_roleless_membership(
    bootstrap_inputs,
):
    with transaction.atomic(), pytest.raises(IntegrityError):
        User.objects.create(
            identity_mode=User.IdentityMode.SYNTHETIC,
            synthetic_handle=uuid4(),
            username="invented",
            email=None,
            is_active=False,
            password="!",
        )

    with transaction.atomic(), pytest.raises(IntegrityError):
        User.objects.create(
            identity_mode=User.IdentityMode.SYNTHETIC,
            synthetic_handle=uuid4(),
            username=None,
            email=None,
            first_name="Invented",
            last_name="Name",
            is_active=False,
            password="!",
        )

    user = User.objects.create_user(username="human", email="human@example.test")
    tenant = Tenant.objects.get(pk=bootstrap_inputs.tenant_id)
    with transaction.atomic(), pytest.raises(IntegrityError):
        TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role=None,
            is_active=True,
        )


@pytest.mark.django_db
def test_rls_contract_is_present_on_postgresql():
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific RLS contract")
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT relrowsecurity, relforcerowsecurity "
            "FROM pg_class WHERE oid = 'codesho.identity_syntheticbootstraprequest'::regclass"
        )
        assert cursor.fetchone() == (True, True)


@pytest.mark.django_db(transaction=True)
def test_postgres_runtime_grants_and_dormancy_guards(bootstrap_inputs):
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific runtime contract")
    runtime_url = os.environ.get("DATABASE_RUNTIME_TEST_URL")
    migrator_url = os.environ.get("DATABASE_MIGRATOR_TEST_URL")
    if not runtime_url or not migrator_url:
        pytest.skip("database role URLs are not configured")

    with patch(
        "modules.identity.synthetic_bootstrap.append_security_event",
        return_value=True,
    ):
        result = bootstrap_synthetic_account(**bootstrap_inputs.__dict__)

    with connect(runtime_url, autocommit=True) as runtime, runtime.cursor() as cursor:
        cursor.execute("RESET app.tenant_id")
        cursor.execute("SELECT count(*) FROM codesho.identity_syntheticbootstraprequest")
        assert cursor.fetchone()[0] == 0
        cursor.execute(
            "SELECT set_config('app.tenant_id', %s, true)",
            [str(bootstrap_inputs.tenant_id)],
        )
        cursor.execute(
            "SELECT count(*) FROM codesho.identity_syntheticbootstraprequest "
            "WHERE id = %s",
            [str(result.request_id)],
        )
        assert cursor.fetchone()[0] == 1
        cursor.execute(
            "SELECT has_table_privilege(current_user, "
            "'codesho.identity_syntheticbootstraprequest', 'SELECT'), "
            "has_table_privilege(current_user, "
            "'codesho.identity_syntheticbootstraprequest', 'INSERT'), "
            "has_table_privilege(current_user, "
            "'codesho.identity_syntheticbootstraprequest', 'UPDATE'), "
            "has_table_privilege(current_user, "
            "'codesho.identity_syntheticbootstraprequest', 'DELETE'), "
            "has_table_privilege(current_user, "
            "'codesho.identity_syntheticbootstraprequest', 'TRUNCATE')"
        )
        assert cursor.fetchone() == (True, True, False, False, False)
        for statement in (
            "UPDATE codesho.identity_syntheticbootstraprequest SET state = 'completed'",
            "DELETE FROM codesho.identity_syntheticbootstraprequest",
            "TRUNCATE codesho.identity_syntheticbootstraprequest",
        ):
            with pytest.raises((InsufficientPrivilege, RaiseException)):
                cursor.execute(statement)

    other = Tenant.objects.create(slug=f"other-{uuid4().hex[:12]}", name="Other")
    with connect(runtime_url, autocommit=True) as runtime, runtime.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(other.id)])
        cursor.execute(
            "SELECT count(*) FROM codesho.identity_syntheticbootstraprequest "
            "WHERE id = %s",
            [str(result.request_id)],
        )
        assert cursor.fetchone()[0] == 0

    with connect(migrator_url, autocommit=True) as migrator, migrator.cursor() as cursor:
        with pytest.raises(RaiseException):
            cursor.execute(
                "UPDATE codesho.identity_user SET password = 'x' WHERE id = %s",
                [str(result.user_id)],
            )
        with pytest.raises(RaiseException):
            cursor.execute(
                "UPDATE codesho.platform_tenant_tenantmembership "
                "SET is_active = true WHERE id = %s",
                [str(result.membership_id)],
            )
        with pytest.raises(RaiseException):
            cursor.execute(
                "UPDATE codesho.platform_tenant_tenantmembership "
                "SET tenant_id = %s WHERE id = %s",
                [str(other.id), str(result.membership_id)],
            )
        for statement, value in (
            ("first_name", "Invented"),
            ("last_name", "Name"),
            ("synthetic_handle", str(uuid4())),
        ):
            with pytest.raises(RaiseException):
                cursor.execute(
                    f"UPDATE codesho.identity_user SET {statement} = %s WHERE id = %s",
                    [value, str(result.user_id)],
                )

        with pytest.raises(RaiseException):
            cursor.execute(
                "INSERT INTO codesho.identity_syntheticbootstraprequest "
                "(id, tenant_id, attestation_id, provenance_id, idempotency_key, "
                "user_id, membership_id, state, audit_event_id, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed', %s, CURRENT_TIMESTAMP)",
                (
                    str(uuid4()),
                    str(other.id),
                    str(bootstrap_inputs.attestation_id),
                    str(bootstrap_inputs.provenance_id),
                    str(uuid4()),
                    str(result.user_id),
                    str(result.membership_id),
                    str(uuid4()),
                ),
            )


@pytest.mark.django_db(transaction=True)
def test_postgres_real_audit_and_all_or_nothing_bootstrap(bootstrap_inputs):
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific audit integration")
    result = bootstrap_synthetic_account(**bootstrap_inputs.__dict__)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT event_type, reason_code FROM audit.identity_security_event "
            "WHERE event_id = %s",
            [str(result.audit_event_id)],
        )
        assert cursor.fetchone() == (
            "synthetic_account_bootstrapped",
            "synthetic_bootstrap_created",
        )


@pytest.mark.django_db(transaction=True)
def test_postgres_concurrent_first_requests_create_one_account(bootstrap_inputs):
    if connection.vendor != "postgresql":
        pytest.skip("PostgreSQL-specific concurrency contract")
    barrier = Barrier(2)
    results = []
    errors = []

    def run_request() -> None:
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            result = bootstrap_synthetic_account(**bootstrap_inputs.__dict__)
            results.append(result)
        except BaseException as exc:  # pragma: no cover - asserted by parent
            errors.append(exc)
        finally:
            close_old_connections()

    first = Thread(target=run_request)
    second = Thread(target=run_request)
    first.start()
    second.start()
    first.join(timeout=20)
    second.join(timeout=20)
    assert not first.is_alive() and not second.is_alive()
    assert errors == []
    assert len(results) == 2
    assert sorted(result.replayed for result in results) == [False, True]
    assert SyntheticBootstrapRequest.objects.count() == 1
    assert User.objects.filter(identity_mode=User.IdentityMode.SYNTHETIC).count() == 1


@pytest.mark.django_db
def test_migration_contract_is_forward_only_and_password_pattern_is_driver_safe():
    migration = importlib.import_module(
        "modules.identity.migrations.0010_synthetic_account_bootstrap"
    )
    assert "password LIKE '!%%'" in migration.BOOTSTRAP_CONTRACT_SQL
    with pytest.raises(IrreversibleError, match="irreversible"):
        migration.irreversible(None, None)


@pytest.mark.django_db
def test_late_request_failure_rolls_back_rows_and_audit_boundary(bootstrap_inputs):
    with (
        patch(
            "modules.identity.synthetic_bootstrap.append_security_event",
            return_value=True,
        ),
        patch(
            "modules.identity.synthetic_bootstrap.SyntheticBootstrapRequest.objects.create",
            side_effect=DatabaseError("request contract rejected"),
        ),
        pytest.raises(Exception, match="database contract rejected"),
    ):
        bootstrap_synthetic_account(**bootstrap_inputs.__dict__)
    assert User.objects.filter(identity_mode=User.IdentityMode.SYNTHETIC).count() == 0
    assert TenantMembership.objects.filter(is_synthetic_bootstrap=True).count() == 0

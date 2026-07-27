"""Internal, synthetic-only account bootstrap workflow.

This module intentionally exposes no HTTP or authentication surface.  The
single service transaction creates only an inactive, unusable-password User,
an inactive roleless membership, an immutable terminal request, and one
bounded security-audit event.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from django.conf import settings
from django.db import DatabaseError, IntegrityError, connection

from modules.platform_event.security_audit import (
    SecurityAuditError,
    append_security_event,
    synthetic_account_bootstrapped,
)
from modules.platform_tenant.context import tenant_atomic
from modules.platform_tenant.models import TenantMembership

from .models import (
    AdultAgeAttestation,
    AdultAttestationProvenance,
    SyntheticBootstrapRequest,
    User,
)


class SyntheticBootstrapError(RuntimeError):
    """Base error for fail-closed synthetic bootstrap failures."""


class SyntheticBootstrapNotAuthorized(SyntheticBootstrapError):
    """Raised when the internal synthetic mode is not explicitly enabled."""


class SyntheticBootstrapConflict(SyntheticBootstrapError):
    """Raised for changed replays, duplicate attestations, or invalid linkage."""


@dataclass(frozen=True, slots=True)
class SyntheticBootstrapResult:
    request_id: UUID
    user_id: UUID
    membership_id: UUID
    audit_event_id: UUID
    replayed: bool


def _require_uuid(value: UUID, name: str) -> UUID:
    if not isinstance(value, UUID):
        raise SyntheticBootstrapConflict(f"{name} must be an opaque UUID")
    return value


def bootstrap_synthetic_account(
    *,
    tenant_id: UUID,
    attestation_id: UUID,
    provenance_id: UUID,
    idempotency_key: UUID,
) -> SyntheticBootstrapResult:
    """Create or replay one dormant synthetic account within one tenant transaction."""

    if settings.ADULT_SIGNUP_MODE != "internal_test":
        raise SyntheticBootstrapNotAuthorized("internal synthetic mode is disabled")

    tenant_id = _require_uuid(tenant_id, "tenant_id")
    attestation_id = _require_uuid(attestation_id, "attestation_id")
    provenance_id = _require_uuid(provenance_id, "provenance_id")
    idempotency_key = _require_uuid(idempotency_key, "idempotency_key")

    try:
        with tenant_atomic(tenant_id):
            existing = (
                SyntheticBootstrapRequest.objects.select_related("user", "membership")
                .filter(tenant_id=tenant_id, idempotency_key=idempotency_key)
                .first()
            )
            if existing is not None:
                if (
                    existing.attestation_id != attestation_id
                    or existing.provenance_id != provenance_id
                    or existing.state != SyntheticBootstrapRequest.State.COMPLETED
                ):
                    raise SyntheticBootstrapConflict("changed synthetic bootstrap replay")
                return SyntheticBootstrapResult(
                    request_id=existing.id,
                    user_id=existing.user_id,
                    membership_id=existing.membership_id,
                    audit_event_id=existing.audit_event_id,
                    replayed=True,
                )

            attestation = (
                AdultAgeAttestation.objects.select_for_update()
                .filter(
                    id=attestation_id,
                    tenant_id=tenant_id,
                    status=AdultAgeAttestation.Status.ADULT_ATTESTED,
                )
                .first()
            )
            if attestation is None:
                raise SyntheticBootstrapConflict("attestation is missing or cross-tenant")

            if connection.vendor != "postgresql":
                provenance = (
                    AdultAttestationProvenance.objects.select_for_update()
                    .filter(id=provenance_id, tenant_id=tenant_id, attestation_id=attestation.id)
                    .first()
                )
                if provenance is None:
                    raise SyntheticBootstrapConflict("provenance is missing or cross-tenant")

            prior = (
                SyntheticBootstrapRequest.objects.filter(
                    tenant_id=tenant_id, attestation_id=attestation.id
                )
                .select_related("user", "membership")
                .first()
            )
            if prior is not None:
                raise SyntheticBootstrapConflict("attestation already has an account")

            user = User(
                identity_mode=User.IdentityMode.SYNTHETIC,
                synthetic_handle=uuid4(),
                username=None,
                email=None,
                is_active=False,
            )
            user.set_unusable_password()
            user.save(force_insert=True)

            membership = TenantMembership.objects.create(
                tenant_id=tenant_id,
                user_id=user.id,
                role=None,
                is_active=False,
                is_synthetic_bootstrap=True,
            )

            audit_event_id = uuid4()
            audit_result = append_security_event(
                synthetic_account_bootstrapped(
                    audit_event_id,
                    uuid4(),
                    tenant_id,
                    user.id,
                    f"synthetic-bootstrap:{tenant_id}:{idempotency_key}",
                )
            )
            if not audit_result.created:
                raise SyntheticBootstrapConflict("synthetic bootstrap audit key already exists")

            request = SyntheticBootstrapRequest.objects.create(
                tenant_id=tenant_id,
                attestation_id=attestation.id,
                provenance_id=provenance_id,
                idempotency_key=idempotency_key,
                user_id=user.id,
                membership_id=membership.id,
                state=SyntheticBootstrapRequest.State.COMPLETED,
                audit_event_id=audit_event_id,
            )
            return SyntheticBootstrapResult(
                request_id=request.id,
                user_id=user.id,
                membership_id=membership.id,
                audit_event_id=audit_event_id,
                replayed=False,
            )
    except IntegrityError as exc:
        raise SyntheticBootstrapConflict("synthetic bootstrap uniqueness conflict") from exc
    except DatabaseError as exc:
        raise SyntheticBootstrapConflict("synthetic bootstrap database contract rejected") from exc
    except SecurityAuditError:
        raise

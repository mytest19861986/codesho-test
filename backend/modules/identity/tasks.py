from contextlib import suppress
from dataclasses import asdict
from uuid import UUID

from celery import shared_task

from config.cleanup_claims import begin_claim, complete_claim, fail_claim
from config.passcode_change_cleanup import BaseTenantTask, cleanup_current_tenant, tenant_atomic


class CleanupClaimTenantTask(BaseTenantTask):
    atomic_run = False


@shared_task(  # type: ignore[untyped-decorator]
    base=BaseTenantTask, bind=True, name="identity.cleanup_passcode_change_challenges"
)
def cleanup_passcode_change_challenges_task(
    self: BaseTenantTask, *, batch_size: int | None = None
) -> dict[str, int]:
    """Explicit tenant task only; no production beat schedule is registered."""
    return asdict(cleanup_current_tenant(batch_size=batch_size))


@shared_task(  # type: ignore[untyped-decorator]
    base=CleanupClaimTenantTask, bind=True, name="identity.run_cleanup_claim"
)
def run_cleanup_claim_task(
    self: CleanupClaimTenantTask,
    *,
    tenant_id: UUID,
    claim_id: str,
    fencing_generation: int,
    owner_token: str,
) -> dict[str, object]:
    tenant_uuid = tenant_id
    claim_uuid = UUID(str(claim_id))
    owner_uuid = UUID(str(owner_token))
    if not begin_claim(
        claim_id=claim_uuid,
        tenant_id=tenant_uuid,
        owner_token=owner_uuid,
        generation=fencing_generation,
    ):
        return {"status": "stale_or_terminal"}
    try:
        with tenant_atomic(tenant_uuid):
            result = cleanup_current_tenant()
    except Exception:
        with suppress(Exception):
            fail_claim(
                claim_id=claim_uuid,
                tenant_id=tenant_uuid,
                owner_token=owner_uuid,
                generation=fencing_generation,
                failure_code="cleanup_error",
            )
        raise
    completed = complete_claim(
        claim_id=claim_uuid,
        tenant_id=tenant_uuid,
        owner_token=owner_uuid,
        generation=fencing_generation,
    )
    return {
        "status": "succeeded" if completed else "stale",
        "expired": result.expired,
        "deleted": result.deleted,
    }

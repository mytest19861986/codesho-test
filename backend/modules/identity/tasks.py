from dataclasses import asdict
from uuid import UUID

from celery import shared_task

from config.cleanup_claims import begin_claim, complete_claim, current_claim_tenant_id
from config.passcode_change_cleanup import BaseTenantTask, cleanup_current_tenant


@shared_task(  # type: ignore[untyped-decorator]
    base=BaseTenantTask, bind=True, name="identity.cleanup_passcode_change_challenges"
)
def cleanup_passcode_change_challenges_task(
    self: BaseTenantTask, *, batch_size: int | None = None
) -> dict[str, int]:
    """Explicit tenant task only; no production beat schedule is registered."""
    return asdict(cleanup_current_tenant(batch_size=batch_size))


@shared_task(  # type: ignore[untyped-decorator]
    base=BaseTenantTask, bind=True, name="identity.run_cleanup_claim"
)
def run_cleanup_claim_task(
    self: BaseTenantTask,
    *,
    claim_id: str,
    fencing_generation: int,
    owner_token: str,
) -> dict[str, object]:
    tenant_uuid = current_claim_tenant_id()
    if tenant_uuid is None:
        raise RuntimeError("tenant context is required for cleanup claim task")
    claim_uuid = UUID(str(claim_id))
    owner_uuid = UUID(str(owner_token))
    if not begin_claim(
        claim_id=claim_uuid,
        tenant_id=tenant_uuid,
        owner_token=owner_uuid,
        generation=fencing_generation,
    ):
        return {"status": "stale_or_terminal"}
    result = cleanup_current_tenant()
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

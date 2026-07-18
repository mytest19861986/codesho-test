from dataclasses import asdict

from celery import shared_task

from modules.identity.passcode_change_cleanup import cleanup_passcode_change_challenges
from modules.platform_tenant.context import current_tenant_id
from modules.platform_tenant.models import Tenant
from modules.platform_tenant.tasks import BaseTenantTask


@shared_task(  # type: ignore[untyped-decorator]
    base=BaseTenantTask, bind=True, name="identity.cleanup_passcode_change_challenges"
)
def cleanup_passcode_change_challenges_task(
    self: BaseTenantTask, *, batch_size: int | None = None
) -> dict[str, int]:
    """Explicit tenant task only; no production beat schedule is registered."""
    tenant_id = current_tenant_id()
    if tenant_id is None:  # Defensive; BaseTenantTask establishes it before run().
        raise RuntimeError("tenant context is required")
    tenant = Tenant.objects.get(pk=tenant_id)
    return asdict(cleanup_passcode_change_challenges(tenant=tenant, batch_size=batch_size))

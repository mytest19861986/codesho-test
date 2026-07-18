from dataclasses import asdict

from celery import shared_task

from config.passcode_change_cleanup import BaseTenantTask, cleanup_current_tenant


@shared_task(  # type: ignore[untyped-decorator]
    base=BaseTenantTask, bind=True, name="identity.cleanup_passcode_change_challenges"
)
def cleanup_passcode_change_challenges_task(
    self: BaseTenantTask, *, batch_size: int | None = None
) -> dict[str, int]:
    """Explicit tenant task only; no production beat schedule is registered."""
    return asdict(cleanup_current_tenant(batch_size=batch_size))

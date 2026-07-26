from __future__ import annotations

from typing import TYPE_CHECKING

from modules.identity.models import PlatformOperatorPolicy

if TYPE_CHECKING:
    from modules.identity.models import User


def evaluate_admin_policy(
    user: User | None,
    model_label: str,
    action: str,
    scope_kind: str,
) -> bool:
    """Evaluate whether an administrative action is authorized for a platform operator.

    Preconditions:
    - User must be authenticated, active, and staff.
    - superuser status NEVER bypasses policy evaluation.
    - Must match exactly one active PlatformOperatorPolicy.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False

    if not getattr(user, "is_active", False) or not getattr(user, "is_staff", False):
        return False

    try:
        active_policies = PlatformOperatorPolicy.objects.filter(
            operator_user=user,
            active=True,
            model_label=model_label,
            action=action,
            scope_kind=scope_kind,
        )
        return active_policies.count() == 1
    except Exception:
        return False

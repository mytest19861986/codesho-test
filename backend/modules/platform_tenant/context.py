from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from uuid import UUID

from django.core.exceptions import ImproperlyConfigured
from django.db import connection, transaction

_tenant_id: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)


def current_tenant_id() -> UUID | None:
    return _tenant_id.get()


def _set_database_context(tenant_id: UUID) -> None:
    if connection.vendor != "postgresql":
        return
    if not connection.in_atomic_block:
        raise ImproperlyConfigured("Tenant context requires an active transaction")
    with connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(tenant_id)])


@contextmanager
def tenant_atomic(tenant_id: UUID) -> Iterator[None]:
    """Set request/task tenant context for exactly one DB transaction."""
    token: Token[UUID | None] | None = None
    with transaction.atomic():
        _set_database_context(tenant_id)
        token = _tenant_id.set(tenant_id)
        try:
            yield
        finally:
            if token is not None:
                _tenant_id.reset(token)

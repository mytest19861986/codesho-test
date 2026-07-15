from abc import abstractmethod
from typing import Any
from uuid import UUID

from celery import Task

from .context import tenant_atomic


class BaseTenantTask(Task):
    abstract = True

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raw_tenant_id = kwargs.pop("tenant_id", None)
        if raw_tenant_id is None:
            raise ValueError("tenant_id is required for tenant-aware tasks")
        try:
            tenant_id = UUID(str(raw_tenant_id))
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError("tenant_id must be a valid UUID") from exc
        with tenant_atomic(tenant_id):
            return self.run(*args, **kwargs)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

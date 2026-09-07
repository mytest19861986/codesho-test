from uuid import uuid4

import pytest

from modules.platform_tenant.context import current_tenant_id
from modules.platform_tenant.tasks import BaseTenantTask


class EchoTenantTask(BaseTenantTask):
    name = "tests.echo_tenant"

    def run(self, value):  # type: ignore[no-untyped-def]
        return value, current_tenant_id()


@pytest.mark.django_db(transaction=True)
def test_base_tenant_task_requires_tenant_id():
    with pytest.raises(ValueError, match="tenant_id is required"):
        EchoTenantTask()("value")


@pytest.mark.django_db(transaction=True)
def test_base_tenant_task_rejects_invalid_tenant_id():
    with pytest.raises(ValueError, match="valid UUID"):
        EchoTenantTask()("value", tenant_id="not-a-uuid")


@pytest.mark.django_db(transaction=True)
def test_base_tenant_task_sets_and_resets_context():
    tenant_id = uuid4()
    value, observed_id = EchoTenantTask()("value", tenant_id=str(tenant_id))
    assert value == "value"
    assert observed_id == tenant_id
    assert current_tenant_id() is None


@pytest.mark.django_db(transaction=True)
def test_base_tenant_task_sequential_execution_no_leakage():
    first_tenant = uuid4()
    second_tenant = uuid4()

    val1, obs1 = EchoTenantTask()("run1", tenant_id=str(first_tenant))
    assert val1 == "run1"
    assert obs1 == first_tenant
    assert current_tenant_id() is None

    val2, obs2 = EchoTenantTask()("run2", tenant_id=str(second_tenant))
    assert val2 == "run2"
    assert obs2 == second_tenant
    assert current_tenant_id() is None

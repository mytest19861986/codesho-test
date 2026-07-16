from django.http import HttpResponse
from django.test import RequestFactory

from modules.identity.models import User
from modules.platform_tenant.context import current_tenant_id, tenant_atomic
from modules.platform_tenant.middleware import (
    TenantCandidateMiddleware,
    TenantTransactionMiddleware,
)
from modules.platform_tenant.models import Tenant, TenantMembership


def test_candidate_is_only_single_subdomain(settings):
    settings.TENANT_BASE_DOMAIN = "localhost"
    resolve = TenantCandidateMiddleware._candidate_from_host
    assert resolve("alpha.localhost:8000") == "alpha"
    assert resolve("localhost") is None
    assert resolve("deep.alpha.localhost") is None
    assert resolve("alpha.example.com") is None


def test_tenant_bypass_paths_are_exact(settings):
    settings.TENANT_BYPASS_PATHS = ("/health/live/",)
    middleware = TenantTransactionMiddleware(lambda request: HttpResponse("ok"))
    request = RequestFactory().get("/health/live/extra", HTTP_HOST="localhost")
    request.user = User()
    assert middleware(request).status_code == 400


def test_session_epoch_precedes_tenant_authorization_in_settings():
    from django.conf import settings

    epoch_middleware = "modules.platform_tenant.middleware.SessionEpochMiddleware"
    tenant_middleware = "modules.platform_tenant.middleware.TenantTransactionMiddleware"
    epoch_index = settings.MIDDLEWARE.index(epoch_middleware)
    tenant_index = settings.MIDDLEWARE.index(tenant_middleware)
    assert epoch_index < tenant_index
    assert settings.SESSION_COOKIE_DOMAIN is None
    assert settings.CSRF_COOKIE_DOMAIN is None


def test_tenant_middleware_authorizes_inside_context(db, settings):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost"]
    tenant = Tenant.objects.create(slug="alpha", name="Alpha")
    user = User.objects.create_user(username="member", email="member@example.com")
    with tenant_atomic(tenant.id):
        TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role=TenantMembership.Role.LEARNER,
        )

    def endpoint(request):  # type: ignore[no-untyped-def]
        assert request.tenant == tenant
        assert current_tenant_id() == tenant.id
        return HttpResponse("ok")

    middleware = TenantCandidateMiddleware(TenantTransactionMiddleware(endpoint))
    request = RequestFactory().get("/api/me/", HTTP_HOST="alpha.localhost")
    request.user = user
    response = middleware(request)

    assert response.status_code == 200
    assert current_tenant_id() is None


def test_tenant_middleware_rejects_non_member(db, settings):
    settings.TENANT_BASE_DOMAIN = "localhost"
    settings.ALLOWED_HOSTS = [".localhost"]
    Tenant.objects.create(slug="alpha", name="Alpha")
    user = User.objects.create_user(username="outsider", email="outsider@example.com")

    inner_middleware = TenantTransactionMiddleware(lambda request: HttpResponse())
    middleware = TenantCandidateMiddleware(inner_middleware)
    request = RequestFactory().get("/api/me/", HTTP_HOST="alpha.localhost")
    request.user = user

    assert middleware(request).status_code == 403

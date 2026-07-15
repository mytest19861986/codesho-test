from collections.abc import Callable
from typing import cast
from uuid import UUID

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from .context import tenant_atomic
from .models import Tenant, TenantMembership


class TenantRequest(HttpRequest):
    tenant_candidate_slug: str | None
    tenant: Tenant
    tenant_membership: TenantMembership


class TenantCandidateMiddleware:
    """Resolve an untrusted slug only; this middleware never grants access."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tenant_request = cast(TenantRequest, request)
        tenant_request.tenant_candidate_slug = self._candidate_from_host(request.get_host())
        return self.get_response(request)

    @staticmethod
    def _candidate_from_host(host: str) -> str | None:
        hostname = host.partition(":")[0].lower()
        base_domain = settings.TENANT_BASE_DOMAIN.lower()
        if hostname == base_domain or not hostname.endswith(f".{base_domain}"):
            return None
        candidate = hostname[: -(len(base_domain) + 1)]
        return candidate if candidate and "." not in candidate else None


class TenantTransactionMiddleware:
    """Set DB context first, then authorize membership inside that transaction."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path.startswith(settings.TENANT_BYPASS_PATHS):
            return self.get_response(request)

        tenant_request = cast(TenantRequest, request)
        slug = getattr(tenant_request, "tenant_candidate_slug", None)
        if slug is None:
            return JsonResponse({"detail": "Tenant is required."}, status=400)

        tenant_id = self._resolve_global_tenant_id(slug)
        if tenant_id is None:
            return JsonResponse({"detail": "Tenant not found."}, status=404)

        with tenant_atomic(tenant_id):
            tenant = Tenant.objects.filter(id=tenant_id, status=Tenant.Status.ACTIVE).first()
            if tenant is None:
                return JsonResponse({"detail": "Tenant not found."}, status=404)
            if not request.user.is_authenticated:
                return JsonResponse({"detail": "Authentication required."}, status=401)
            membership = TenantMembership.objects.filter(
                tenant_id=tenant_id,
                user_id=request.user.pk,
                is_active=True,
            ).first()
            if membership is None:
                return JsonResponse({"detail": "Tenant access denied."}, status=403)
            tenant_request.tenant = tenant
            tenant_request.tenant_membership = membership
            return self.get_response(request)

    @staticmethod
    def _resolve_global_tenant_id(slug: str) -> UUID | None:
        # Tenant is a global routing registry. Tenant-owned rows remain RLS-protected.
        return Tenant.objects.filter(slug=slug).values_list("id", flat=True).first()

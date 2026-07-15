from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health_live(request):  # type: ignore[no-untyped-def]
    return JsonResponse({"status": "ok"})


@require_GET
def health_ready(request):  # type: ignore[no-untyped-def]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ready"})

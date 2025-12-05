
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .services.ev_advisor import EVAdvisorClient

@require_GET
def charger_lookup_by_serial(request, serial: str):
    """
    Proxy endpoint for testing with Postman.
    - Calls EV Advisor preprod using EVAdvisorClient.
    - Returns upstream JSON or appropriate error code.
    - No authentication required in this tiny increment to simplify testing; secure later.
    """
    client = EVAdvisorClient.from_settings()
    try:
        data = client.get_chargers_by_serial(serial)
        return JsonResponse(data, safe=False, status=200)
    except ValueError as ve:
        return JsonResponse({"error": str(ve)}, status=400)
    except PermissionError as pe:
        return JsonResponse({"error": str(pe)}, status=403)
    except FileNotFoundError as nf:
        return JsonResponse({"error": str(nf)}, status=404)
    except RuntimeError as re:
        return JsonResponse({"error": str(re)}, status=502)  # Bad Gateway proxy error

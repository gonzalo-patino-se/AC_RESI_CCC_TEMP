
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .services.ev_advisor import EVAdvisorClient
import logging


log = logging.getLogger(__name__)



#@login_required(login_url='login')
@require_GET
def charger_by_id(request, charger_id: str):
    """
    Authenticated proxy for EV Advisor 'Get Charger information by chargerId'.
    """
    user = request.user
    log.info("charger_by_id: user=%s charger_id=%s", user.get_username(), charger_id)

    client = EVAdvisorClient.from_settings()
    try:
        data = client.get_charger_by_id(charger_id)
        return JsonResponse(data, safe=False, status=200)
    except ValueError as ve:
        return JsonResponse({"error": str(ve)}, status=400)
    except PermissionError as pe:
        return JsonResponse({"error": str(pe)}, status=403)
    except FileNotFoundError as nf:
        return JsonResponse({"error": str(nf)}, status=404)
    except RuntimeError as re:
        return JsonResponse({"error": str(re)}, status=502)
    
    


#@login_required(login_url='login')
@require_GET
def charger_lookup_by_serial(request, serial: str):
    """
    Authenticated proxy endpoint for EV Advisor serial lookup.
    - Requires user to be logged in (session-based).
    - Adds a minimal audit log entry (who called, serial).
    """
    user = request.user
    log.info("charger_lookup_by_serial: user=%s serial=%s", user.get_username(), serial)

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
        return JsonResponse({"error": str(re)}, status=502)





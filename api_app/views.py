
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .services.ev_advisor import EVAdvisorClient
import logging
from django.http import StreamingHttpResponse, JsonResponse

log = logging.getLogger(__name__)



#OCPP LOGS LATEST




@require_GET
def charger_ocpp_logs_latest(request, charger_id: str):
    client = EVAdvisorClient.from_settings()
    try:
        upstream = client.download_latest_ocpp_logs(str(charger_id))

        content_type = upstream.headers.get("Content-Type", "application/octet-stream")

        filename = None
        cd = upstream.headers.get("Content-Disposition", "")
        if "filename=" in cd:
            try:
                filename = cd.split("filename=", 1)[1].strip().strip('"')
            except Exception:
                filename = None
        if not filename:
            filename = f"ocpp-logs-{charger_id}-latest.zip"

        body = upstream.content
        resp = HttpResponse(body, content_type=content_type)
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        resp["Content-Length"] = str(len(body))
        resp["Cache-Control"] = "no-cache"
        # Do NOT set Connection header (WSGI forbids hop-by-hop headers)
        return resp

    except ValueError as ve:
        return JsonResponse({"error": str(ve)}, status=400)
    except PermissionError as pe:
        return JsonResponse({"error": str(pe)}, status=403)
    except FileNotFoundError as nf:
        return JsonResponse({"error": str(nf)}, status=404)
    except RuntimeError as re:
        return JsonResponse({"error": str(re)}, status=502)



#Charge history

@require_GET
def charger_charge_history(request, charger_id: str):
    """
    Proxy: Ended charges history for a chargerId.
    Query params:
    - startDate (required)
    - endDate (required)
    - idTag (optional)
    """
    start_date = request.GET.get("startDate", "")
    end_date = request.GET.get("endDate", "")
    id_tag = request.GET.get("idTag", None)

    client = EVAdvisorClient.from_settings()
    try:
        data = client.get_charge_history(str(charger_id), start_date, end_date, id_tag)
        return JsonResponse(data, safe=False, status=200)
    except ValueError as ve:
        # Includes upstream 400 mapping and our own input validation errors
        return JsonResponse({"error": str(ve)}, status=400)
    except PermissionError as pe:
        return JsonResponse({"error": str(pe)}, status=403)
    except FileNotFoundError as nf:
        return JsonResponse({"error": str(nf)}, status=404)
    except RuntimeError as re:
        return JsonResponse({"error": str(re)}, status=502)



#Cloud Status
#@login_required(login_url='login')
@require_GET
def charger_cloudstatus(request, charger_id: str):
    """
    Proxy: Cloud/Charger status for a chargerId.
    """
    client = EVAdvisorClient.from_settings()
    try:
        data = client.get_cloud_status(str(charger_id))
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
def charger_capabilities(request, charger_id: str):
    client = EVAdvisorClient.from_settings()
    try:
        data = client.get_capabilities(str(charger_id))
        return JsonResponse(data, safe=False, status=200)
    except ValueError as ve:
        return JsonResponse({"error": str(ve)}, status=400)
    except PermissionError as pe:
        return JsonResponse({"error": str(pe)}, status=403)
    except RuntimeError as re:
        return JsonResponse({"error": str(re)}, status=502)



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





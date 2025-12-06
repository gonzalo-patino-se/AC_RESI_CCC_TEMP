
"""
EV Advisor service client.

Responsibility:
- Encapsulate outbound calls to the EV Advisor preprod API.
- Provide small, typed methods (one per endpoint).
- Enforce security (timeouts, sanitized path variables).
- Read configuration from Django settings (dotenv).

References:
- Upstream endpoint spec: ccc/api/v1.0/chargerserial/:serialNumber (header: ApiKey)  # see project docs or Postman file
"""

from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings

log = logging.getLogger(__name__)

# Strictly allow safe path characters to avoid path injection.
_SERIAL_SAFE_RE = re.compile(r"^[A-Za-z0-9._\-]+$")


class EVAdvisorClient:
    """
    Thin HTTP client for EV Advisor.

    Usage:
        client = EVAdvisorClient.from_settings()
        data = client.get_chargers_by_serial("ABC123")
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 10,
        retries: int = 2,
        session: Optional[requests.Session] = None
    ) -> None:
        if not base_url or not api_key:
            raise ValueError("EVAdvisorClient requires base_url and api_key")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.retries = max(0, retries)
        self.session = session or requests.Session()
        # Default headers: Accept JSON, ApiKey for upstream auth.
        self.session.headers.update({
            "Accept": "application/json",
            "ApiKey": self.api_key,
        })

    @classmethod
    def from_settings(cls) -> "EVAdvisorClient":
        return cls(
            base_url=settings.EXTERNAL_API_BASE_URL,
            api_key=settings.EXTERNAL_API_KEY,
            timeout=settings.EXTERNAL_API_TIMEOUT,
            retries=settings.EXTERNAL_API_RETRIES,
        )

    def _safe_serial(self, serial: str) -> str:
        """Sanitize serial to a safe path segment (defense-in-depth)."""
        s = (serial or "").strip()
        if not s or not _SERIAL_SAFE_RE.match(s):
            raise ValueError("Invalid serial number format")
        return s

    def _get(self, url: str) -> requests.Response:
        """
        Perform a GET with small retry loop for transient 5xx/connectivity issues.
        Retries are conservative to avoid hammering upstream.
        """
        last_exc: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                return resp
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                log.warning("EVAdvisor GET retry %s failed: %s", attempt + 1, exc)
        # If we reach here, all attempts failed.
        raise RuntimeError(f"EVAdvisor GET failed after {self.retries + 1} attempts: {last_exc}")

    def get_chargers_by_serial(self, serial: str) -> List[Dict[str, Any]]:
        """
        Call EV Advisor: GET /ccc/api/v1.0/chargerserial/:serialNumber

        Returns:
            List of charger records (JSON objects).

        Raises:
            ValueError: for invalid serial format.
            PermissionError: for 403 Forbidden.
            FileNotFoundError: for 404 Not Found.
            RuntimeError: for 5xx or unexpected status codes.
        """
        safe_serial = self._safe_serial(serial)
        url = f"{self.base_url}/ccc/api/v1.0/chargerserial/{safe_serial}"  # upstream path
        resp = self._get(url)

        if resp.status_code == 200:
            # upstream returns JSON array
            return resp.json()
        elif resp.status_code == 403:
            raise PermissionError("Forbidden (invalid or missing ApiKey)")
        elif resp.status_code == 404:
            raise FileNotFoundError("Charger not found")
        elif 500 <= resp.status_code < 600:
            raise RuntimeError(f"Upstream server error ({resp.status_code})")
        else:
            raise RuntimeError(f"Unexpected status: {resp.status_code} - {resp.text[:200]}")


    def get_charger_by_id(self, charger_id: str) -> Dict[str, Any]:
        """
        Call EV Advisor: GET /ccc/api/v1.0/{chargerId}
        Header: ApiKey

        Returns:
            Charger record (JSON object).

        Errors:
            PermissionError: 403
            FileNotFoundError: 404
            RuntimeError: 5xx or unexpected code
        """
        cid = (charger_id or "").strip()
        # UUIDs contain hex + dashes; keep simple sanity check.
        if not cid or len(cid) < 8:
            raise ValueError("Invalid chargerId format")

        url = f"{self.base_url}/ccc/api/v1.0/{cid}"
        resp = self._get(url)

        if resp.status_code == 200:
            return resp.json()  # upstream is a JSON object for this endpoint
        elif resp.status_code == 403:
            raise PermissionError("Forbidden (invalid or missing ApiKey)")
        elif resp.status_code == 404:
            raise FileNotFoundError("Charger not found")
        elif 500 <= resp.status_code < 600:
            raise RuntimeError(f"Upstream server error ({resp.status_code})")
        else:
            raise RuntimeError(f"Unexpected status: {resp.status_code} - {resp.text[:200]}")

    
    def get_capabilities(self, charger_id: str) -> Dict[str, Any]:
        """
        EV Advisor: GET /controller/api/v1.0/charger/{chargerId}/capabilities
        Returns a capabilities object (flags and limits).
        """
        cid = (charger_id or "").strip()
        if not cid or len(cid) < 8:
            raise ValueError("Invalid chargerId format")

        url = f"{self.base_url}/controller/api/v1.0/charger/{cid}/capabilities"
        resp = self._get(url)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 403:
            raise PermissionError("Forbidden (invalid or missing ApiKey)")
        elif resp.status_code == 500:
            raise RuntimeError("Upstream server error (500)")
        else:
            raise RuntimeError(f"Unexpected status: {resp.status_code} - {resp.text[:200]}")

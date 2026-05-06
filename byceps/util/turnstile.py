"""
byceps.util.turnstile
~~~~~~~~~~~~~~~~~~~~~

Strict Cloudflare Turnstile integration (no legacy fallbacks).
"""

from __future__ import annotations
import json, math
from typing import Any, Dict, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import current_app, request as flask_request

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def _get_cfg_raw() -> Dict[str, Any]:
    """Read the nested Cloudflare Turnstile block as set on app.config."""
    # This is expected to be injected by config conversion (converter.py).
    return current_app.config.get("cloudflare_turnstile") or {}


def get_public_options() -> Dict[str, Any]:
    """Expose only what templates need to render the widget (no secrets)."""
    cfg = _get_cfg_raw()
    return {
        "enabled": bool(cfg.get("enabled", False)),
        "sitekey": cfg.get("sitekey") or "",
    }


def is_enabled() -> bool:
    """Convenience: is Turnstile feature toggled on?"""
    cfg = _get_cfg_raw()
    return bool(cfg.get("enabled", False))


def best_remote_ip(req: Optional[object] = None) -> str:
    """
    Try to determine the original client IP.
    Prefers CF-Connecting-IP, falls back to first X-Forwarded-For, then remote_addr.
    """
    r = req or flask_request
    xff = (r.headers.get("X-Forwarded-For") or "").split(",")
    xff_first = (xff[0].strip() if xff and xff[0].strip() else "")
    return r.headers.get("CF-Connecting-IP") or xff_first or r.remote_addr


def verify_token(
    token: Optional[str],
    *,
    remoteip: Optional[str] = None,
    timeout: float = 3.0,
    expected_action: Optional[str] = None,
) -> bool:
    """
    Strict server-side verification; requires secret_key.
    Returns True if feature is disabled (do not block flows),
    otherwise only when Cloudflare validates the token (and optional action matches).
    """
    cfg = _get_cfg_raw()
    if not bool(cfg.get("enabled", False)):
        return True  # feature off → do not block

    secret_key = cfg.get("secret_key") or ""
    if not secret_key or not token:
        return False

    timeout = float(max(0.5, min(10.0, abs(timeout))))
    data = {"secret": secret_key, "response": token}
    if remoteip:
        data["remoteip"] = remoteip

    body = urlencode(data).encode("utf-8")
    req = Request(VERIFY_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False

    if not bool(payload.get("success")):
        return False

    if expected_action:
        action = payload.get("action")
        if action and action != expected_action:
            return False

    return True

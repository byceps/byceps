from __future__ import annotations
from typing import Optional, Dict, Any
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
from flask import current_app, request as flask_request
import math

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

def _get_cfg() -> Dict[str, Any]:
    cfg = current_app.config.get('turnstile') or {}
    enabled = cfg.get('enabled')
    sitekey = cfg.get('sitekey')
    secret  = cfg.get('secret')

    if enabled is None:
        enabled = current_app.config.get('TURNSTILE_ENABLED')
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() in ('1', 'true', 'yes', 'on')
        if enabled is None:
            enabled = False

    if not sitekey:
        sitekey = (
            current_app.config.get('TURNSTILE_SITEKEY')
            or current_app.config.get('TURNSTILE_SITE_KEY')
            or ""
        )
    if not secret:
        secret = current_app.config.get('TURNSTILE_SECRET') or ""

    return {'enabled': bool(enabled), 'sitekey': sitekey, 'secret': secret}


def get_public_options() -> Dict[str, Any]:
    cfg = _get_cfg()
    return {'enabled': cfg['enabled'], 'sitekey': cfg['sitekey']}


def best_remote_ip(req: Optional[object] = None) -> str:
    """
    Ermittelt die sinnvollste Client-IP (beachtet Proxy-Header).
    - Übergib `request` explizit (bessere Testbarkeit). Fällt auf flask_request zurück.
    - Nimmt die *erste* IP aus X-Forwarded-For, falls vorhanden.
    """
    r = req or flask_request
    xff = (r.headers.get('X-Forwarded-For') or '').split(',')
    xff_first = (xff[0].strip() if xff and xff[0].strip() else '')
    return (
        r.headers.get('CF-Connecting-IP')
        or xff_first
        or r.remote_addr
    )


def verify_token(
    token: Optional[str],
    *,
    remoteip: Optional[str] = None,
    timeout: float = 3.0,
    expected_action: Optional[str] = None,
) -> bool:
    """
    Serverseitige Turnstile-Verifikation.
    - Prüft nur, wenn enabled=True und secret vorhanden.
    - expected_action: wenn gesetzt, wird die von CF zurückgelieferte Aktion geprüft.
    - Gibt True zurück, wenn (a) Feature disabled oder (b) Verifikation erfolgreich.
    """
    cfg = _get_cfg()
    if not cfg['enabled']:
        return True  

    secret = cfg['secret']
    if not secret or not token:
        return False

    timeout = float(max(0.5, min(10.0, math.fabs(timeout))))

    data = {'secret': secret, 'response': token}
    if remoteip:
        data['remoteip'] = remoteip

    body = urlencode(data).encode("utf-8")
    req = Request(VERIFY_URL, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return False

    ok = bool(payload.get("success"))
    if not ok:
        return False

    if expected_action:
        action = payload.get("action")
        if action and action != expected_action:
            return False

    return True

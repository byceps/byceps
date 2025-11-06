"""
byceps.services.external_accounts.steam.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connector to Steam (OpenID 2.0)

:Copyright: 2021-2025 Jan Korneffel
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from urllib import parse

from flask import current_app, g, redirect, request, url_for
import httpx
from sqlalchemy.exc import IntegrityError

from byceps.config.models import SteamConfig
from byceps.services.external_accounts import (
    external_accounts_service,
    signals as external_accounts_signals,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.views import login_required, redirect_to, respond_no_content

blueprint = create_blueprint('connected_external_accounts_steam', __name__)

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
SERVICE_NAME = "steam"


def _get_enabled_steam_configuration() -> SteamConfig | None:
    cfg = getattr(current_app, "byceps_config", None)
    steam = getattr(cfg, "steam", None) if cfg else None
    if not steam or not steam.enabled:
        return None
    return steam


def _realm() -> str:
    verify_url = url_for('.connect_verify', _external=True)
    parts = parse.urlsplit(verify_url)
    return f"{parts.scheme}://{parts.netloc}"

def _get_persona_name(steam_id: str) -> str | None:
    """Liefert den Steam-Personanamen für steam_id (SteamID64) – oder None."""
    cfg = getattr(current_app, "byceps_config", None)
    steam_cfg: SteamConfig | None = getattr(cfg, "steam", None) if cfg else None
    api_key = getattr(steam_cfg, "api_key", None) if steam_cfg else None
    if not api_key:
        return None

    try:
        r = httpx.get(
            "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
            params={"key": api_key, "steamids": steam_id},
            timeout=10,
        )
        if not r.is_success:
            return None
        data = r.json()
        players = data.get("response", {}).get("players", [])
        if players:
            name = players[0].get("personaname")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except httpx.HTTPError:
        return None
    except Exception:
        return None

    return None

@blueprint.get('/connect')
@login_required
def connect():
    if not _get_enabled_steam_configuration():
        flash_error('Verbindung mit Steam derzeit nicht möglich.')
        return redirect_to('user_settings.view')

    return_to = url_for('.connect_verify', _external=True)
    realm = _realm()

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_to,
        "openid.realm": realm,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return redirect(f"{STEAM_OPENID_URL}?{parse.urlencode(params)}")


@blueprint.get('/connect/verify')
@login_required
def connect_verify():
    if not _get_enabled_steam_configuration():
        flash_error('Verbindung mit Steam derzeit nicht möglich.')
        return redirect_to('user_settings.view')

    params = request.args.to_dict()

    if params.get("openid.mode") != "id_res":
        flash_error("Steam-Anmeldung abgebrochen.")
        return redirect_to('user_settings.view')

    verify_params = params.copy()
    verify_params["openid.mode"] = "check_authentication"

    try:
        resp = httpx.post(STEAM_OPENID_URL, data=verify_params, timeout=10)
    except httpx.HTTPError:
        flash_error("Steam-Verifikation derzeit nicht möglich.")
        return redirect_to('user_settings.view')

    verified = resp.is_success and "is_valid:true" in resp.text
    if not verified:
        flash_error("Steam-Verifikation fehlgeschlagen.")
        return redirect_to('user_settings.view')

    claimed = params.get("openid.claimed_id", "")
    steam_id = claimed.rstrip("/").split("/")[-1]
    if not steam_id.isdigit():
        flash_error("Ungültige Steam-ID.")
        return redirect_to('user_settings.view')

    external_id = steam_id
    name = _get_persona_name(steam_id)
    external_name = name if name else steam_id

    now = datetime.utcnow()
    try:
        connection_result = external_accounts_service.connect_external_account(
            now,
            g.user.id,
            SERVICE_NAME,
            external_id=external_id,
            external_name=external_name,
        )
    except IntegrityError:
        already = external_accounts_service.find_connected_external_account_for_user_and_service(
            g.user.id, SERVICE_NAME
        )
        if already and already.external_id == external_id:
            flash_success("Steam-Account ist bereits verbunden.")
        else:
            flash_error("Dieser Steam-Account ist bereits mit einem anderen Benutzer verknüpft.")
        return redirect_to('user_settings.view')

    if connection_result.is_ok():
        _, event = connection_result.unwrap()
        external_accounts_signals.external_account_connected.send(None, event=event)
        flash_success("Steam-Account erfolgreich verbunden.")
    else:
        flash_error("Steam-Account konnte nicht verbunden werden.")

    return redirect_to('user_settings.view')


@blueprint.delete('')
@login_required
@respond_no_content
def remove():
    """Unlink Steam account."""
    acc = external_accounts_service.find_connected_external_account_for_user_and_service(
        g.user.id, SERVICE_NAME
    )
    if not acc:
        return

    result = external_accounts_service.disconnect_external_account(acc.id)
    if result.is_ok():
        event = result.unwrap()
        external_accounts_signals.external_account_disconnected.send(None, event=event)

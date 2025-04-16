"""
byceps.services.external_accounts.discord.blueprints.site.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connector to Discord

:Copyright: 2021-2025 Jan Korneffel
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from urllib import parse

from flask import current_app, g, redirect, request, url_for
import httpx

from byceps.config.models import DiscordConfig
from byceps.services.external_accounts import (
    external_accounts_service,
    signals as external_accounts_signals,
)
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.views import login_required, redirect_to, respond_no_content


blueprint = create_blueprint('connected_external_accounts_discord', __name__)


API_URL_BASE = 'https://discord.com/api/v10'

SERVICE_NAME = 'discord'


@blueprint.get('/connect')
@login_required
def connect():
    """Connect account with Discord via OAuth2."""
    config = _get_enabled_discord_configuration()
    if not config:
        flash_error('Verbindung mit Discord derzeit nicht möglich.')
        return redirect_to('user_settings.view')

    query_string_data = {
        'client_id': config.client_id,
        'redirect_uri': url_for('.connect_verify', _external=True),
        'response_type': 'code',
        'scope': 'identify',
    }
    query_string = parse.urlencode(query_string_data)
    auth_url = API_URL_BASE + '/oauth2/authorize?' + query_string
    return redirect(auth_url)


def error():
    flash_error('Verbindung mit Discord-Account fehlgeschlagen.')
    return redirect_to('user_settings.view')


@blueprint.get('/connect/verify')
@login_required
def connect_verify():
    """Verify signed Discord parameters."""
    params = request.args.to_dict()

    if 'code' not in params:
        return error()

    config = _get_enabled_discord_configuration()
    if not config:
        flash_error('Verbindung mit Discord derzeit nicht möglich.')
        return redirect_to('user_settings.view')

    auth = (config.client_id, config.client_secret)
    token_request_data = {
        'scope': 'identify',
        'redirect_uri': url_for('.connect_verify', _external=True),
        'code': params['code'],
        'grant_type': 'authorization_code',
    }

    # Try to obtain access token with given authorization code.
    token_response = httpx.post(
        API_URL_BASE + '/oauth2/token',
        auth=auth,
        data=token_request_data,
        timeout=10,
    )
    reponse_token = token_response.json()
    if not token_response.is_success or ('access_token' not in reponse_token):
        return error()

    # Get user info.
    access_token = reponse_token['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = httpx.get(
        API_URL_BASE + '/users/@me', headers=headers, timeout=10
    )
    user_response_data = user_response.json()
    if not user_response.is_success:
        return error()

    discord_id = user_response_data['id']
    discord_username = user_response_data['username']
    discord_discriminator = user_response_data['discriminator']

    # Store Discord ID and username.
    now = datetime.utcnow()
    external_id = discord_id
    external_name = f'{discord_username}#{discord_discriminator}'

    connection_result = external_accounts_service.connect_external_account(
        now,
        g.user.id,
        SERVICE_NAME,
        external_id=external_id,
        external_name=external_name,
    )

    _, event = connection_result.unwrap()

    external_accounts_signals.external_account_connected.send(None, event=event)

    flash_success('Discord-Account erfolgreich verbunden.')
    return redirect_to('user_settings.view')


@blueprint.delete('')
@login_required
@respond_no_content
def remove():
    """Unlink Discord account."""
    connected_external_account = external_accounts_service.find_connected_external_account_for_user_and_service(
        g.user.id, SERVICE_NAME
    )
    if not connected_external_account:
        return

    disconnection_result = (
        external_accounts_service.disconnect_external_account(
            connected_external_account.id
        )
    )

    event = disconnection_result.unwrap()

    external_accounts_signals.external_account_disconnected.send(
        None, event=event
    )


def _get_enabled_discord_configuration() -> DiscordConfig | None:
    config = current_app.byceps_config.discord

    if not config or not config.enabled:
        return None

    return config

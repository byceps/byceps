"""
byceps.services.whereabouts.blueprints.api.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2022-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps

from flask import abort, g, request
from werkzeug.datastructures import WWWAuthenticate

from byceps.services.whereabouts import whereabouts_client_service
from byceps.services.whereabouts.models import WhereaboutsClient


def client_token_required(func):
    """Ensure the request is authenticated with a valid client token for
    an approved client.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        client = _find_client()

        if client is None:
            www_authenticate = WWWAuthenticate('Bearer')
            abort(401, www_authenticate=www_authenticate)

        if not client.approved:
            www_authenticate = WWWAuthenticate('Bearer')
            www_authenticate['error'] = 'invalid_client_token'
            abort(401, www_authenticate=www_authenticate)

        g.client = client

        return func(*args, **kwargs)

    return wrapper


def _find_client() -> WhereaboutsClient | None:
    client_token = _get_bearer_token()

    if client_token is None:
        return None

    return whereabouts_client_service.find_client_by_token(client_token)


def _get_bearer_token() -> str | None:
    if request.authorization is None or request.authorization.type != 'bearer':
        return None

    token = request.authorization.token

    if not token:
        return None

    return token

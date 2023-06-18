"""
byceps.blueprints.api.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import wraps

from flask import abort, request
from werkzeug.datastructures import WWWAuthenticate

from byceps.services.authentication.api import authn_api_service
from byceps.services.authentication.api.models import ApiToken


def api_token_required(func):
    """Ensure the request is authenticated via API token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        request_token = _extract_token_from_request()
        if request_token is None:
            return None

        api_token = authn_api_service.find_api_token_by_token(request_token)

        if api_token is None:
            www_authenticate = WWWAuthenticate('Bearer')
            abort(401, www_authenticate=www_authenticate)

        if api_token.suspended:
            www_authenticate = WWWAuthenticate('Bearer')
            www_authenticate['error'] = 'invalid_token'
            abort(401, www_authenticate=www_authenticate)

        return func(*args, **kwargs)

    return wrapper


def _extract_token_from_request() -> str | None:
    if request.authorization is None or request.authorization.type != 'bearer':
        return None

    token = request.authorization.token

    if not token:
        return None

    return token

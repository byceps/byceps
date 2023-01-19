"""
byceps.blueprints.api.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps
from typing import Optional

from flask import abort, request
from werkzeug.datastructures import WWWAuthenticate

from ...services.authentication.api import authn_api_service
from ...services.authentication.api.models import ApiToken


def api_token_required(func):
    """Ensure the request is authenticated via API token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        api_token = _find_valid_api_token()

        if api_token is None:
            www_authenticate = WWWAuthenticate('Bearer')
            abort(401, www_authenticate=www_authenticate)

        if api_token.suspended:
            www_authenticate = WWWAuthenticate('Bearer')
            www_authenticate['error'] = 'invalid_token'
            abort(401, www_authenticate=www_authenticate)

        return func(*args, **kwargs)

    return wrapper


def _find_valid_api_token() -> Optional[ApiToken]:
    request_token = _extract_token_from_request()
    if request_token is None:
        return None

    return authn_api_service.find_api_token_by_token(request_token)


def _extract_token_from_request() -> Optional[str]:
    header_value = request.headers.get('Authorization')
    if header_value is None:
        return None

    return header_value.replace('Bearer ', '', 1)

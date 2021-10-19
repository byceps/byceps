"""
byceps.blueprints.api.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import base64
import binascii
from functools import wraps
import hmac
from typing import Optional

from flask import abort, current_app, request

from ...services.authentication.api import service as api_service


def api_token_required(func):
    """Ensure the request is authenticated via API token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _has_valid_api_token():
            abort(401, www_authenticate='Bearer')
        return func(*args, **kwargs)

    return wrapper


def _has_valid_api_token() -> bool:
    request_token = _extract_token_from_request()
    if request_token is None:
        return False

    return _matches_legacy_token(request_token) or _matches_api_token(
        request_token
    )


def _extract_token_from_request() -> Optional[str]:
    header_value = request.headers.get('Authorization')
    if header_value is None:
        return None

    return header_value.replace('Bearer ', '', 1)


def _matches_legacy_token(request_token: str) -> bool:
    configured_token = current_app.config.get('API_TOKEN')
    if configured_token is None:
        return False

    token_base64decoded = _decode_base64(request_token)
    if token_base64decoded is None:
        return False

    return hmac.compare_digest(token_base64decoded, configured_token.encode())


def _decode_base64(value: str) -> Optional[bytes]:
    try:
        return base64.b64decode(value)
    except (TypeError, ValueError, binascii.Error):
        return None


def _matches_api_token(request_token: str) -> bool:
    api_token = api_service.find_api_token_by_token(request_token)
    return api_token is not None

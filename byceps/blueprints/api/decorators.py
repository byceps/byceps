"""
byceps.blueprints.api.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import base64
import binascii
from functools import wraps
import hmac
from typing import Optional

from flask import abort, current_app, request


def api_token_required(func):
    """Ensure the request is authenticated via API token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _has_valid_api_token():
            abort(401, www_authenticate='Bearer')
        return func(*args, **kwargs)

    return wrapper


def _has_valid_api_token() -> bool:
    configured_token = current_app.config.get('API_TOKEN')
    if configured_token is None:
        return False

    request_token = _extract_api_token_from_request()
    if request_token is None:
        return False

    return hmac.compare_digest(request_token, configured_token.encode())


def _extract_api_token_from_request() -> Optional[bytes]:
    header_value = request.headers.get('Authorization')
    if header_value is None:
        return None

    token_b64 = header_value.replace('Bearer ', '', 1)

    try:
        return base64.b64decode(token_b64)
    except (TypeError, ValueError, binascii.Error):
        return None

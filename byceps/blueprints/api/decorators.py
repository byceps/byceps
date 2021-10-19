"""
byceps.blueprints.api.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps
from typing import Optional

from flask import abort, request

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

    api_token = api_service.find_api_token_by_token(request_token)
    return api_token is not None


def _extract_token_from_request() -> Optional[str]:
    header_value = request.headers.get('Authorization')
    if header_value is None:
        return None

    return header_value.replace('Bearer ', '', 1)

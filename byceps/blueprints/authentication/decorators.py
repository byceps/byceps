"""
byceps.blueprints.authentication.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import base64
import binascii
from functools import wraps
import hmac
from typing import Optional

from flask import current_app, g, request
from werkzeug.exceptions import Unauthorized

from ...util.framework.flash import flash_notice
from ...util.views import redirect_to


# Workaround until Werkzeug 0.15 is released.
# Replace with `abort(401, www_authenticate='Bearer')` then.
class UnauthorizedWithWwwAuthenticateHeader(Unauthorized):

    def get_headers(self, environ=None):
        return super().get_headers(environ) + [
            ('WWW-Authenticate', 'Bearer'),
        ]


def api_token_required(func):
    """Ensure the request is authenticated via API token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _has_valid_api_token():
            raise UnauthorizedWithWwwAuthenticateHeader()
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


def login_required(func):
    """Ensure the current user has logged in."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.current_user.is_active:
            flash_notice('Bitte melde dich an.')
            return redirect_to('authentication.login_form')
        return func(*args, **kwargs)
    return wrapper

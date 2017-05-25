"""
byceps.services.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ..user.models.user import User
from ..user import service as user_service

from .exceptions import AuthenticationFailed
from .password import service as password_service


def authenticate(screen_name: str, password: str) -> User:
    """Try to authenticate the user.

    Return the user object on success, or raise an exception on failure.
    """
    # Look up user.
    user = user_service.find_user_by_screen_name(screen_name)
    if user is None:
        # Screen name is unknown.
        raise AuthenticationFailed()

    # Verify credentials.
    if not password_service.is_password_valid_for_user(user.id, password):
        # Password does not match.
        raise AuthenticationFailed()

    # Account must be active.
    if not user.is_active:
        # User account is disabled.
        raise AuthenticationFailed()

    return user

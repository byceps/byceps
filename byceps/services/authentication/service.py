"""
byceps.services.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ..user import service as user_service
from ..user.transfer.models import User

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

    # Account must be initialized.
    if not user.initialized:
        # User account is not initialized.
        raise AuthenticationFailed()

    # Account must not be suspended.
    if user.suspended:
        # User account is suspended.
        raise AuthenticationFailed()

    # Account must not be deleted.
    if user.deleted:
        # User account has been deleted.
        raise AuthenticationFailed()

    # Verify credentials.
    if not password_service.is_password_valid_for_user(user.id, password):
        # Password does not match.
        raise AuthenticationFailed()

    return user.to_dto()

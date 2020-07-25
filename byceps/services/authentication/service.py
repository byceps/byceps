"""
byceps.services.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ..user import service as user_service
from ..user.transfer.models import User

from .exceptions import AuthenticationFailed
from .password import service as password_service


def authenticate(screen_name_or_email_address: str, password: str) -> User:
    """Try to authenticate the user.

    Return the user object on success, or raise an exception on failure.
    """
    # Look up user.
    user = _find_user_by_screen_name_or_email_address(
        screen_name_or_email_address
    )
    if user is None:
        # Screen name/email address is unknown.
        raise AuthenticationFailed()

    _require_user_account_is_active(user)

    # Verify credentials.
    if not password_service.is_password_valid_for_user(user.id, password):
        # Password does not match.
        raise AuthenticationFailed()

    return user.to_dto()


def _find_user_by_screen_name_or_email_address(
    screen_name_or_email_address: str,
) -> Optional[User]:
    if '@' in screen_name_or_email_address:
        return user_service.find_user_by_email_address(
            screen_name_or_email_address
        )
    else:
        return user_service.find_user_by_screen_name(
            screen_name_or_email_address, case_insensitive=True
        )


def _require_user_account_is_active(user: User) -> None:
    """Raise exception if user account has not been initialized, is
    suspended, or has been deleted.
    """
    if (not user.initialized) or user.suspended or user.deleted:
        raise AuthenticationFailed()

"""
byceps.services.authentication.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...typing import UserID

from ..user import service as user_service
from ..user.transfer.models import User

from .exceptions import AuthenticationFailed
from .password import service as password_service


def authenticate(screen_name_or_email_address: str, password: str) -> User:
    """Try to authenticate the user.

    Return the user object on success, or raise an exception on failure.
    """
    # Look up user by screen name or email address.
    user_id = _find_user_id_by_screen_name_or_email_address(
        screen_name_or_email_address
    )
    if user_id is None:
        # Screen name/email address is unknown.
        raise AuthenticationFailed()

    # Ensure account is initialized, not suspended, and not deleted.
    user = user_service.find_active_user(user_id)
    if user is None:
        # Should not happen as the user has been looked up before.
        raise AuthenticationFailed()

    # Verify credentials.
    if not password_service.is_password_valid_for_user(user.id, password):
        # Password does not match.
        raise AuthenticationFailed()

    password_service.migrate_password_hash_if_outdated(user.id, password)

    return user


def _find_user_id_by_screen_name_or_email_address(
    screen_name_or_email_address: str,
) -> Optional[UserID]:
    if '@' in screen_name_or_email_address:
        user = user_service.find_user_by_email_address(
            screen_name_or_email_address
        )
    else:
        user = user_service.find_user_by_screen_name(
            screen_name_or_email_address, case_insensitive=True
        )

    if user is None:
        return None

    return user.id

"""
byceps.services.authentication.authn_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ..user import user_service
from ..user.transfer.models import User

from .exceptions import (
    AccountDeleted,
    AccountNotInitialized,
    AccountSuspended,
    AuthenticationFailed,
    WrongPassword,
)
from .password import authn_password_service


def authenticate(screen_name_or_email_address: str, password: str) -> User:
    """Try to authenticate the user.

    Return the user object on success, or raise an exception on failure.
    """
    # Look up user by screen name or email address.
    user = _find_user_by_screen_name_or_email_address(
        screen_name_or_email_address
    )
    if user is None:
        # Screen name/email address is unknown.
        raise AuthenticationFailed()

    db_user = user_service.get_db_user(user.id)
    if not db_user.initialized:
        raise AccountNotInitialized()

    if user.suspended:
        raise AccountSuspended()

    if user.deleted:
        raise AccountDeleted()

    # Verify credentials.
    if not authn_password_service.is_password_valid_for_user(user.id, password):
        raise WrongPassword()

    authn_password_service.migrate_password_hash_if_outdated(user.id, password)

    return user


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

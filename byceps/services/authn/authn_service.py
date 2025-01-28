"""
byceps.services.authn.authn_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from .errors import AuthenticationFailedError
from .password import authn_password_service


def authenticate(
    screen_name_or_email_address: str, password: str
) -> Result[User, AuthenticationFailedError]:
    """Try to authenticate the user.

    Return the user object on success and an error on failure.
    """
    # Look up user by screen name or email address.
    user = _find_user_by_screen_name_or_email_address(
        screen_name_or_email_address
    )
    if user is None:
        # Screen name/email address is unknown.
        return Err(AuthenticationFailedError.UsernameUnknown)

    if not user.initialized:
        return Err(AuthenticationFailedError.AccountNotInitialized)

    if user.suspended:
        return Err(AuthenticationFailedError.AccountSuspended)

    if user.deleted:
        return Err(AuthenticationFailedError.AccountDeleted)

    # Verify credentials.
    if not authn_password_service.is_password_valid_for_user(user.id, password):
        return Err(AuthenticationFailedError.WrongPassword)

    authn_password_service.migrate_password_hash_if_outdated(user.id, password)

    return Ok(user)


def _find_user_by_screen_name_or_email_address(
    screen_name_or_email_address: str,
) -> User | None:
    if '@' in screen_name_or_email_address:
        return user_service.find_user_by_email_address(
            screen_name_or_email_address
        )
    else:
        return user_service.find_user_by_screen_name(
            screen_name_or_email_address
        )

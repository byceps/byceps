"""
byceps.services.authn.authn_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.user import user_service
from byceps.services.user.models.user import Password, User
from byceps.util.result import Err, Ok, Result

from .errors import (
    UserAccountDeletedError,
    UserAccountNotInitializedError,
    UserAccountSuspendedError,
    UserAuthenticationFailedError,
    UsernameUnknownError,
    WrongPasswordError,
)
from .password import authn_password_service


def authenticate(
    screen_name_or_email_address: str, password: Password
) -> Result[User, UserAuthenticationFailedError]:
    """Try to authenticate the user.

    Return the user object on success and an error on failure.
    """

    def check_password(
        user: User,
    ) -> Result[User, UserAuthenticationFailedError]:
        return _check_password(user, password)

    return (
        _identify_account(screen_name_or_email_address)
        .and_then(_check_account)
        .and_then(check_password)
    )


def _identify_account(
    screen_name_or_email_address: str,
) -> Result[User, UserAuthenticationFailedError]:
    user = _find_user_by_screen_name_or_email_address(
        screen_name_or_email_address
    )

    if user is None:
        return Err(UsernameUnknownError())

    return Ok(user)


def _check_account(user: User) -> Result[User, UserAuthenticationFailedError]:
    if not user.initialized:
        return Err(UserAccountNotInitializedError())

    if user.suspended:
        return Err(UserAccountSuspendedError())

    if user.deleted:
        return Err(UserAccountDeletedError())

    return Ok(user)


def _check_password(
    user: User, password: Password
) -> Result[User, UserAuthenticationFailedError]:
    if not authn_password_service.is_password_valid_for_user(user.id, password):
        return Err(WrongPasswordError())

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

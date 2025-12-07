"""
byceps.services.authn.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserAuthenticationFailedError:
    """Indicate a generic user authentication error."""


@dataclass(frozen=True)
class UsernameUnknownError(UserAuthenticationFailedError):
    pass


@dataclass(frozen=True)
class UserAccountNotInitializedError(UserAuthenticationFailedError):
    pass


@dataclass(frozen=True)
class UserAccountSuspendedError(UserAuthenticationFailedError):
    pass


@dataclass(frozen=True)
class UserAccountDeletedError(UserAuthenticationFailedError):
    pass


@dataclass(frozen=True)
class WrongPasswordError(UserAuthenticationFailedError):
    pass

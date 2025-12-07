"""
byceps.services.authn.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UsernameUnknownError:
    pass


@dataclass(frozen=True)
class UserAccountNotInitializedError:
    pass


@dataclass(frozen=True)
class UserAccountSuspendedError:
    pass


@dataclass(frozen=True)
class UserAccountDeletedError:
    pass


@dataclass(frozen=True)
class WrongPasswordError:
    pass


UserAuthenticationFailedError = (
    UsernameUnknownError
    | UserAccountNotInitializedError
    | UserAccountSuspendedError
    | UserAccountDeletedError
    | WrongPasswordError
)

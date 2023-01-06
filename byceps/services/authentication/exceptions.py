"""
byceps.services.authentication.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


class AuthenticationFailed(Exception):
    """User authentication failed."""


class UsernameUnknown(AuthenticationFailed):
    """User authentication failed because the username is unknown."""


class AccountNotInitialized(AuthenticationFailed):
    """User authentication failed because the account has not been
    initialized yet.
    """


class AccountSuspended(AuthenticationFailed):
    """User authentication failed because the account is suspended."""


class AccountDeleted(AuthenticationFailed):
    """User authentication failed because the account has been deleted."""


class WrongPassword(AuthenticationFailed):
    """User authentication failed due to wrong password."""

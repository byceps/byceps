"""
byceps.services.authentication.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


class AuthenticationFailed(Exception):
    """User authentication failed"""


class WrongPassword(AuthenticationFailed):
    """User authentication failed due to wrong password"""

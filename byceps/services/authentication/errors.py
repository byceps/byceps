"""
byceps.services.authentication.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum


AuthenticationFailedError = Enum(
    'AuthenticationFailedError',
    [
        'UsernameUnknown',
        'AccountNotInitialized',
        'AccountSuspended',
        'AccountDeleted',
        'WrongPassword',
    ],
)

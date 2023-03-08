"""
byceps.services.authentication.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum


AuthenticationFailed = Enum(
    'AuthenticationFailed',
    [
        'UsernameUnknown',
        'AccountNotInitialized',
        'AccountSuspended',
        'AccountDeleted',
        'WrongPassword',
    ],
)

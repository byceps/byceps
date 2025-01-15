"""
byceps.services.authn.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
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

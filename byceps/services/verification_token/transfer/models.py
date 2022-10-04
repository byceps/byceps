"""
byceps.services.verification_token.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ....typing import UserID


Purpose = Enum(
    'Purpose',
    [
        'consent',
        'email_address_change',
        'email_address_confirmation',
        'password_reset',
    ],
)


@dataclass(frozen=True)
class VerificationToken:
    token: str
    created_at: datetime
    user_id: UserID
    purpose: Purpose
    data: dict[str, str]

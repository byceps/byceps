"""
byceps.services.authn.password.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime

from byceps.services.user.models.user import UserID


@dataclass(frozen=True)
class Credential:
    user_id: UserID
    password_hash: str
    updated_at: datetime

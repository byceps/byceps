"""
byceps.services.authn.password.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime

from byceps.services.user.models import PasswordHash, UserID


@dataclass(frozen=True, kw_only=True)
class Credential:
    user_id: UserID
    password_hash: PasswordHash
    updated_at: datetime

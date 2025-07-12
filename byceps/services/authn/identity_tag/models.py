"""
byceps.services.authn.identity_tag.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class UserIdentityTag:
    id: UUID
    created_at: datetime
    creator: User
    identifier: str
    user: User
    note: str | None
    suspended: bool

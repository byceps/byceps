"""
byceps.services.user_group.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.services.party.models import PartyID
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True, slots=True)
class UserGroup:
    id: UUID
    party_id: PartyID
    created_at: datetime
    creator: User
    title: str
    description: str | None

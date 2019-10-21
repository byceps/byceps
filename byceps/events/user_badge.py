"""
byceps.events.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ..services.user_badge.transfer.models import BadgeID
from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class UserBadgeAwarded(_BaseEvent):
    user_id: UserID
    badge_id: BadgeID
    initiator_id: Optional[UserID]

"""
byceps.events.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
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
    user_screen_name: Optional[str]
    badge_id: BadgeID
    badge_label: str

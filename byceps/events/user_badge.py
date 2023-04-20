"""
byceps.events.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from byceps.services.user_badge.models import BadgeID
from byceps.typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class UserBadgeAwarded(_BaseEvent):
    user_id: UserID
    user_screen_name: Optional[str]
    badge_id: BadgeID
    badge_label: str

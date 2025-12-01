"""
byceps.services.user_badge.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent
from byceps.services.user_badge.models import BadgeID
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class UserBadgeAwardedEvent(BaseEvent):
    badge_id: BadgeID
    badge_label: str
    awardee: User

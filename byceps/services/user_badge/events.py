"""
byceps.services.user_badge.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventUser
from byceps.services.user_badge.models import BadgeID


@dataclass(frozen=True)
class UserBadgeAwardedEvent(_BaseEvent):
    badge_id: BadgeID
    badge_label: str
    awardee: EventUser

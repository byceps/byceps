"""
byceps.events.user_badge
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.user_badge.models import BadgeID
from byceps.typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class UserBadgeAwardedEvent(_BaseEvent):
    badge_id: BadgeID
    badge_label: str
    awardee_id: UserID
    awardee_screen_name: str | None

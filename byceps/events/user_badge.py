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
    user_id: UserID
    user_screen_name: str | None
    badge_id: BadgeID
    badge_label: str

"""
byceps.events.base
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from byceps.services.user.models.user import User, UserID


@dataclass(frozen=True)
class EventUser:
    id: UserID
    screen_name: str | None

    @classmethod
    def from_user(cls, user: User) -> EventUser:
        return cls(
            id=user.id,
            screen_name=user.screen_name,
        )


@dataclass(frozen=True)
class _BaseEvent:
    occurred_at: datetime
    initiator: EventUser | None

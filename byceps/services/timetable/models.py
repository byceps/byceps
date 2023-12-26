"""
byceps.services.timetable.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.party.models import PartyID


TimetableID = NewType('TimetableID', UUID)

TimetableItemID = NewType('TimetableItemID', UUID)


@dataclass(frozen=True)
class Timetable:
    id: TimetableID
    party_id: PartyID
    hidden: bool
    items: list[TimetableItem]


@dataclass(frozen=True)
class TimetableItem:
    id: TimetableItemID
    timetable_id: TimetableID
    scheduled_at: datetime
    description: str
    location: str | None
    hidden: bool

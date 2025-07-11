"""
byceps.services.timetable.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import NewType
from uuid import UUID

from byceps.services.party.models import PartyID


TimetableID = NewType('TimetableID', UUID)

TimetableItemID = NewType('TimetableItemID', UUID)


@dataclass(frozen=True, kw_only=True, slots=True)
class Timetable:
    id: TimetableID
    party_id: PartyID
    hidden: bool
    items: list[TimetableItem]


@dataclass(frozen=True, kw_only=True, slots=True)
class TimetableGroupedByDay:
    id: TimetableID
    party_id: PartyID
    hidden: bool
    items: list[tuple[date, list[TimetableItem]]]


@dataclass(frozen=True, kw_only=True, slots=True)
class TimetableItem:
    id: TimetableItemID
    timetable_id: TimetableID
    scheduled_at: datetime
    description: str
    location: str | None
    link_target: str | None
    link_label: str | None
    hidden: bool

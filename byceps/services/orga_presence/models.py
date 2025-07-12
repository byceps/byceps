"""
byceps.services.orga_presence.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Self
from uuid import UUID

from byceps.services.party.models import Party
from byceps.services.user.models.user import User
from byceps.util.datetime.range import DateTimeRange


TimeSlotType = Enum('TimeSlotType', ['party', 'presence', 'task'])


@dataclass(frozen=True, kw_only=True)
class TimeSlot:
    type: TimeSlotType
    starts_at: datetime
    ends_at: datetime

    @property
    def range(self) -> DateTimeRange:
        return DateTimeRange(self.starts_at, self.ends_at)


@dataclass(frozen=True, kw_only=True)
class PartyTimeSlot(TimeSlot):
    party: Party

    @classmethod
    def from_party(cls, party: Party) -> Self:
        return cls(
            type=TimeSlotType.party,
            starts_at=party.starts_at,
            ends_at=party.ends_at,
            party=party,
        )


@dataclass(frozen=True, kw_only=True)
class PresenceTimeSlot(TimeSlot):
    id: UUID
    orga: User

    @classmethod
    def from_(
        cls,
        time_slot_id: UUID,
        orga: User,
        starts_at: datetime,
        ends_at: datetime,
    ) -> Self:
        return cls(
            id=time_slot_id,
            type=TimeSlotType.presence,
            starts_at=starts_at,
            ends_at=ends_at,
            orga=orga,
        )


@dataclass(frozen=True, kw_only=True)
class TaskTimeSlot(TimeSlot):
    id: UUID
    title: str

    @classmethod
    def from_(
        cls,
        time_slot_id: UUID,
        title: str,
        starts_at: datetime,
        ends_at: datetime,
    ) -> Self:
        return cls(
            id=time_slot_id,
            type=TimeSlotType.task,
            starts_at=starts_at,
            ends_at=ends_at,
            title=title,
        )

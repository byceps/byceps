"""
byceps.services.orga_presence.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ...party.transfer.models import Party
from ...user.transfer.models import User

from ....util.datetime.range import DateTimeRange


TimeSlotType = Enum('TimeSlotType', ['party', 'presence', 'task'])


@dataclass(frozen=True)
class TimeSlot:
    type: TimeSlotType
    starts_at: datetime
    ends_at: datetime

    @property
    def range(self) -> DateTimeRange:
        return DateTimeRange(self.starts_at, self.ends_at)


@dataclass(frozen=True)
class PartyTimeSlot(TimeSlot):
    party: Party

    @classmethod
    def from_party(cls, party: Party) -> PartyTimeSlot:
        return cls(
            type=TimeSlotType.party,
            starts_at=party.starts_at,
            ends_at=party.ends_at,
            party=party,
        )


@dataclass(frozen=True)
class PresenceTimeSlot(TimeSlot):
    orga: User

    @classmethod
    def from_(
        cls, orga: User, starts_at: datetime, ends_at: datetime
    ) -> PresenceTimeSlot:
        return cls(
            type=TimeSlotType.presence,
            starts_at=starts_at,
            ends_at=ends_at,
            orga=orga,
        )


@dataclass(frozen=True)
class TaskTimeSlot(TimeSlot):
    title: str

    @classmethod
    def from_(
        cls, title: str, starts_at: datetime, ends_at: datetime
    ) -> TaskTimeSlot:
        return cls(
            type=TimeSlotType.task,
            starts_at=starts_at,
            ends_at=ends_at,
            title=title,
        )

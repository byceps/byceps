"""
byceps.services.orga_presence.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from enum import Enum

from attr import attrs

from ...party.transfer.models import Party
from ...user.transfer.models import User

from ....util.datetime.range import DateTimeRange


TimeSlotType = Enum('TimeSlotType', ['party', 'presence', 'task'])


@attrs(auto_attribs=True, frozen=True, slots=True)
class TimeSlot:
    type: TimeSlotType
    starts_at: datetime
    ends_at: datetime

    @property
    def range(self) -> DateTimeRange:
        return DateTimeRange(self.starts_at, self.ends_at)


@attrs(auto_attribs=True, frozen=True, slots=True)
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


@attrs(auto_attribs=True, frozen=True, slots=True)
class PresenceTimeSlot(TimeSlot):
    orga: User

    @classmethod
    def from_(cls, orga: User, starts_at: datetime, ends_at: datetime) -> PresenceTimeSlot:
        return cls(
            type=TimeSlotType.presence,
            starts_at=starts_at,
            ends_at=ends_at,
            orga=orga,
        )


@attrs(auto_attribs=True, frozen=True, slots=True)
class TaskTimeSlot(TimeSlot):
    title: str

    @classmethod
    def from_(cls, title: str, starts_at: datetime, ends_at: datetime) -> TaskTimeSlot:
        return cls(
            type=TimeSlotType.task,
            starts_at=starts_at,
            ends_at=ends_at,
            title=title,
        )

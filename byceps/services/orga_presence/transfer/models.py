"""
byceps.services.orga_presence.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from enum import Enum

from attr import attrib, attrs

from ...party.transfer.models import Party
from ...user.models.user import UserTuple

from ....util.datetime.range import DateTimeRange


TimeSlotType = Enum('TimeSlotType', ['party', 'presence', 'task'])


@attrs(frozen=True, slots=True)
class TimeSlot:
    type = attrib(type=TimeSlotType)
    starts_at = attrib(type=datetime)
    ends_at = attrib(type=datetime)

    @property
    def range(self) -> DateTimeRange:
        return DateTimeRange(self.starts_at, self.ends_at)


@attrs(frozen=True, slots=True)
class PartyTimeSlot(TimeSlot):
    party = attrib(type=Party)

    @classmethod
    def from_party(cls, party: Party):
        return cls(
            type=TimeSlotType.party,
            starts_at=party.starts_at,
            ends_at=party.ends_at,
            party=party,
        )


@attrs(frozen=True, slots=True)
class PresenceTimeSlot(TimeSlot):
    orga = attrib(type=UserTuple)

    @classmethod
    def from_(cls, orga: UserTuple, starts_at: datetime, ends_at: datetime):
        return cls(
            type=TimeSlotType.presence,
            starts_at=starts_at,
            ends_at=ends_at,
            orga=orga,
        )


@attrs(frozen=True, slots=True)
class TaskTimeSlot(TimeSlot):
    title = attrib(type=str)

    @classmethod
    def from_(cls, title: str, starts_at: datetime, ends_at: datetime):
        return cls(
            type=TimeSlotType.task,
            starts_at=starts_at,
            ends_at=ends_at,
            title=title,
        )

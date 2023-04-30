"""
byceps.services.attendance.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.seating.models import SeatingArea, SeatID
from byceps.services.ticketing.models.ticket import TicketID
from byceps.services.user.models.user import User


@dataclass(frozen=True)
class AttendeeSeat:
    id: SeatID
    area: SeatingArea
    label: str | None


@dataclass(frozen=True)
class AttendeeTicket:
    id: TicketID
    seat: AttendeeSeat | None
    checked_in: bool


@dataclass(frozen=True)
class Attendee:
    user: User
    is_orga: bool
    tickets: list[AttendeeTicket]

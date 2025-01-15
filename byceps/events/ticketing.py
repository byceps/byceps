"""
byceps.events.ticketing
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.seating.models import SeatID
from byceps.services.ticketing.models.ticket import TicketCode, TicketID

from .base import _BaseEvent, EventParty, EventUser


@dataclass(frozen=True)
class _TicketEvent(_BaseEvent):
    ticket_id: TicketID


@dataclass(frozen=True)
class TicketCheckedInEvent(_TicketEvent):
    ticket_code: TicketCode
    occupied_seat_id: SeatID | None
    user: EventUser | None


@dataclass(frozen=True)
class TicketsSoldEvent(_BaseEvent):
    party: EventParty
    owner: EventUser | None
    quantity: int

"""
byceps.services.ticketing.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent, EventParty
from byceps.services.seating.models import SeatID
from byceps.services.ticketing.models.ticket import TicketCode, TicketID
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class _TicketEvent(BaseEvent):
    ticket_id: TicketID


@dataclass(frozen=True, kw_only=True)
class TicketCheckedInEvent(_TicketEvent):
    ticket_code: TicketCode
    occupied_seat_id: SeatID | None
    user: User | None


@dataclass(frozen=True, kw_only=True)
class TicketsSoldEvent(BaseEvent):
    party: EventParty
    owner: User | None
    quantity: int

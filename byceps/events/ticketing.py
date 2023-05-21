"""
byceps.events.ticketing
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.seating.models import SeatID
from byceps.services.ticketing.models.ticket import TicketCode, TicketID
from byceps.typing import PartyID, UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _TicketEvent(_BaseEvent):
    ticket_id: TicketID


@dataclass(frozen=True)
class TicketCheckedInEvent(_TicketEvent):
    ticket_code: TicketCode
    occupied_seat_id: SeatID | None
    user_id: UserID | None
    user_screen_name: str | None


@dataclass(frozen=True)
class TicketsSoldEvent(_BaseEvent):
    party_id: PartyID
    owner_id: UserID | None
    owner_screen_name: str | None
    quantity: int

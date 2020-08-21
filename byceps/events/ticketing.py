"""
byceps.events.ticketing
~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ..services.seating.transfer.models import SeatID
from ..services.ticketing.transfer.models import TicketCode, TicketID
from ..typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _TicketEvent(_BaseEvent):
    ticket_id: TicketID


@dataclass(frozen=True)
class TicketCheckedIn(_TicketEvent):
    ticket_code: TicketCode
    occupied_seat_id: Optional[SeatID]
    user_id: Optional[UserID]
    user_screen_name: Optional[str]

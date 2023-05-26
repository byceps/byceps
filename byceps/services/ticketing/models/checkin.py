"""
byceps.services.ticketing.models.checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.services.seating.models import SeatID
from byceps.typing import UserID

from .ticket import TicketCode, TicketID


@dataclass(frozen=True)
class TicketValidForCheckIn:
    id: TicketID
    code: TicketCode
    used_by_id: UserID
    occupied_seat_id: SeatID | None


@dataclass(frozen=True)
class TicketCheckIn:
    id: UUID
    occurred_at: datetime
    ticket_id: TicketID
    initiator_id: UserID

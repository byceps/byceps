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
from byceps.services.user.models.user import User
from byceps.typing import PartyID, UserID

from .ticket import TicketCode, TicketID


@dataclass(frozen=True)
class TicketForCheckIn:
    id: TicketID
    party_id: PartyID
    code: TicketCode
    occupied_seat_id: SeatID | None
    used_by: User | None
    revoked: bool
    user_checked_in: bool


@dataclass(frozen=True)
class TicketValidForCheckIn:
    id: TicketID
    code: TicketCode
    used_by: User
    occupied_seat_id: SeatID | None


@dataclass(frozen=True)
class TicketCheckIn:
    id: UUID
    occurred_at: datetime
    ticket_id: TicketID
    initiator_id: UserID

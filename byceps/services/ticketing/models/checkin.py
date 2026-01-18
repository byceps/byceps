"""
byceps.services.ticketing.models.checkin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from byceps.services.party.models import PartyID
from byceps.services.seating.models import SeatID
from byceps.services.user.models.user import User, UserID

from .ticket import TicketCode, TicketID


@dataclass(frozen=True, kw_only=True)
class PotentialTicketForCheckIn:
    id: TicketID
    party_id: PartyID
    code: TicketCode
    occupied_seat_id: SeatID | None
    used_by: User | None
    revoked: bool
    user_checked_in: bool


@dataclass(frozen=True, kw_only=True)
class ValidTicketForCheckIn:
    id: TicketID
    code: TicketCode
    used_by: User
    occupied_seat_id: SeatID | None


@dataclass(frozen=True, kw_only=True)
class TicketCheckIn:
    id: UUID
    occurred_at: datetime
    ticket_id: TicketID
    initiator_id: UserID

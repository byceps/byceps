"""
byceps.services.ticketing.ticket_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from byceps.database import generate_uuid7
from byceps.events.ticketing import TicketCheckedInEvent
from byceps.services.user.models.user import User
from byceps.typing import PartyID
from byceps.util.result import Err, Ok, Result

from .dbmodels.ticket import DbTicket
from .errors import (
    TicketBelongsToDifferentPartyError,
    TicketingError,
    TicketIsRevokedError,
    TicketLacksUserError,
    UserAlreadyCheckedInError,
)
from .models.checkin import TicketCheckIn, TicketValidForCheckIn


def validate_ticket_for_check_in(
    party_id: PartyID, db_ticket: DbTicket
) -> Result[TicketValidForCheckIn, TicketingError]:
    ticket_id = db_ticket.id

    if db_ticket.party_id != party_id:
        return Err(
            TicketBelongsToDifferentPartyError(
                f'Ticket {ticket_id} belongs to another party ({db_ticket.party_id}).'
            )
        )

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    if db_ticket.used_by_id is None:
        return Err(
            TicketLacksUserError(f'Ticket {ticket_id} has no user assigned.')
        )

    if db_ticket.user_checked_in:
        return Err(
            UserAlreadyCheckedInError(
                f'Ticket {ticket_id} has already been used to check in a user.'
            )
        )

    return Ok(
        TicketValidForCheckIn(
            id=ticket_id,
            code=db_ticket.code,
            used_by_id=db_ticket.used_by_id,
            occupied_seat_id=db_ticket.occupied_seat_id,
        )
    )


def check_in_user(
    ticket: TicketValidForCheckIn, user: User, initiator: User
) -> Result[tuple[TicketCheckIn, TicketCheckedInEvent], TicketingError]:
    check_in_id = generate_uuid7()
    occurred_at = datetime.utcnow()

    check_in = TicketCheckIn(
        id=check_in_id,
        occurred_at=occurred_at,
        ticket_id=ticket.id,
        initiator_id=initiator.id,
    )

    event = TicketCheckedInEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        ticket_id=ticket.id,
        ticket_code=ticket.code,
        occupied_seat_id=ticket.occupied_seat_id,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    return Ok((check_in, event))

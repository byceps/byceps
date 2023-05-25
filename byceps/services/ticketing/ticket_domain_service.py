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
from byceps.util.result import Ok, Result

from .dbmodels.ticket import DbTicket
from .errors import TicketingError
from .models.ticket import TicketCheckIn


def check_in_user(
    db_ticket: DbTicket, user: User, initiator: User
) -> Result[tuple[TicketCheckIn, TicketCheckedInEvent], TicketingError]:
    check_in_id = generate_uuid7()
    occurred_at = datetime.utcnow()

    check_in = TicketCheckIn(
        id=check_in_id,
        occurred_at=occurred_at,
        ticket_id=db_ticket.id,
        initiator_id=initiator.id,
    )

    event = TicketCheckedInEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        ticket_id=db_ticket.id,
        ticket_code=db_ticket.code,
        occupied_seat_id=db_ticket.occupied_seat_id,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )

    return Ok((check_in, event))

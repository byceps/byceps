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

from .errors import (
    TicketBelongsToDifferentPartyError,
    TicketingError,
    TicketIsRevokedError,
    TicketLacksUserError,
    UserAccountDeletedError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
)
from .models.checkin import (
    TicketCheckIn,
    TicketForCheckIn,
    TicketValidForCheckIn,
)
from .models.log import TicketLogEntry, TicketLogEntryData
from .models.ticket import TicketID


def check_in_user(
    party_id: PartyID, ticket: TicketForCheckIn, initiator: User
) -> Result[
    tuple[TicketCheckIn, TicketCheckedInEvent, TicketLogEntry], TicketingError
]:
    ticket_id = ticket.id

    if ticket.party_id != party_id:
        return Err(
            TicketBelongsToDifferentPartyError(
                f'Ticket {ticket_id} belongs to another party ({ticket.party_id}).'
            )
        )

    if ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    if ticket.used_by is None:
        return Err(
            TicketLacksUserError(f'Ticket {ticket_id} has no user assigned.')
        )

    if ticket.user_checked_in:
        return Err(
            UserAlreadyCheckedInError(
                f'Ticket {ticket_id} has already been used to check in a user.'
            )
        )

    user = ticket.used_by

    if user.deleted:
        return Err(
            UserAccountDeletedError(
                f'User account {user.screen_name} has been deleted.'
            )
        )

    if user.suspended:
        return Err(
            UserAccountSuspendedError(
                f'User account {user.screen_name} is suspended.'
            )
        )

    valid_ticket = TicketValidForCheckIn(
        id=ticket_id,
        code=ticket.code,
        used_by=ticket.used_by,
        occupied_seat_id=ticket.occupied_seat_id,
    )

    occurred_at = datetime.utcnow()

    check_in = _build_check_in(occurred_at, valid_ticket, initiator)
    event = _build_check_in_event(occurred_at, valid_ticket, initiator)
    log_entry = _build_check_in_log_entry(
        occurred_at,
        'user-checked-in',
        ticket_id,
        {
            'checked_in_user_id': str(user.id),
            'initiator_id': str(initiator.id),
        },
    )

    return Ok((check_in, event, log_entry))


def _build_check_in(
    occurred_at: datetime, ticket: TicketValidForCheckIn, initiator: User
) -> TicketCheckIn:
    return TicketCheckIn(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        ticket_id=ticket.id,
        initiator_id=initiator.id,
    )


def _build_check_in_event(
    occurred_at: datetime, ticket: TicketValidForCheckIn, initiator: User
) -> TicketCheckedInEvent:
    return TicketCheckedInEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        ticket_id=ticket.id,
        ticket_code=ticket.code,
        occupied_seat_id=ticket.occupied_seat_id,
        user_id=ticket.used_by.id,
        user_screen_name=ticket.used_by.screen_name,
    )


def _build_check_in_log_entry(
    occurred_at: datetime,
    event_type: str,
    ticket_id: TicketID,
    data: TicketLogEntryData,
) -> TicketLogEntry:
    return TicketLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type=event_type,
        ticket_id=ticket_id,
        data=data.copy(),
    )

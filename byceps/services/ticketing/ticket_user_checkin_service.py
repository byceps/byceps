"""
byceps.services.ticketing.ticket_user_checkin_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import select

from byceps.database import db
from byceps.events.ticketing import TicketCheckedInEvent
from byceps.services.ticketing.dbmodels.checkin import DbTicketCheckIn
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import PartyID, UserID
from byceps.util.result import Err, Ok, Result

from . import ticket_domain_service, ticket_log_service, ticket_service
from .dbmodels.ticket import DbTicket
from .errors import (
    TicketBelongsToDifferentPartyError,
    TicketingError,
    TicketIsRevokedError,
    TicketLacksUserError,
    UserAccountDeletedError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
    UserIdUnknownError,
)
from .models.checkin import TicketCheckIn
from .models.ticket import TicketID


def check_in_user(
    party_id: PartyID, ticket_id: TicketID, initiator_id: UserID
) -> Result[TicketCheckedInEvent, TicketingError]:
    """Record that the ticket was used to check in its user."""
    db_ticket_result = _get_ticket_for_checkin(party_id, ticket_id)

    if db_ticket_result.is_err():
        return Err(db_ticket_result.unwrap_err())

    db_ticket = db_ticket_result.unwrap()

    initiator = user_service.get_user(initiator_id)

    user_result = _get_user_for_checkin(db_ticket.used_by_id)

    if user_result.is_err():
        return Err(user_result.unwrap_err())

    user = user_result.unwrap()

    check_in_result = ticket_domain_service.check_in_user(
        db_ticket, user, initiator
    )

    if check_in_result.is_err():
        return Err(check_in_result.unwrap_err())

    check_in, event = check_in_result.unwrap()

    _persist_check_in(db_ticket, check_in, event)

    return Ok(event)


def _get_ticket_for_checkin(
    party_id: PartyID, ticket_id: TicketID
) -> Result[DbTicket, TicketingError]:
    db_ticket = ticket_service.get_ticket(ticket_id)

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

    return Ok(db_ticket)


def _get_user_for_checkin(user_id: UserID) -> Result[User, TicketingError]:
    user = user_service.find_user(user_id)

    if user is None:
        return Err(UserIdUnknownError(f"Unknown user ID '{user_id}'"))

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

    return Ok(user)


def _persist_check_in(
    db_ticket: DbTicket, check_in: TicketCheckIn, event: TicketCheckedInEvent
) -> None:
    db_ticket.user_checked_in = True

    db_check_in = DbTicketCheckIn(
        event.occurred_at, event.ticket_id, event.initiator_id
    )
    db.session.add(db_check_in)

    db_log_entry = ticket_log_service.build_entry(
        'user-checked-in',
        event.ticket_id,
        {
            'checked_in_user_id': str(event.user_id),
            'initiator_id': str(event.initiator_id),
        },
        occurred_at=event.occurred_at,
    )
    db.session.add(db_log_entry)

    db.session.commit()


def revert_user_check_in(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Revert a user check-in that was done by mistake."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    initiator = user_service.get_user(initiator_id)

    if not db_ticket.user_checked_in:
        raise ValueError(f'User of ticket {ticket_id} has not been checked in.')

    db_ticket.user_checked_in = False

    db_log_entry = ticket_log_service.build_entry(
        'user-check-in-reverted',
        db_ticket.id,
        {
            'checked_in_user_id': str(db_ticket.used_by_id),
            'initiator_id': str(initiator.id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()


def find_check_in_for_ticket(ticket_id: TicketID) -> TicketCheckIn | None:
    db_check_in = db.session.scalar(
        select(DbTicketCheckIn).filter_by(ticket_id=ticket_id)
    )

    if db_check_in is None:
        return None

    return TicketCheckIn(
        id=db_check_in.id,
        occurred_at=db_check_in.occurred_at,
        ticket_id=db_check_in.ticket_id,
        initiator_id=db_check_in.initiator_id,
    )

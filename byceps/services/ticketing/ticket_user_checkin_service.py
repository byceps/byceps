"""
byceps.services.ticketing.ticket_user_checkin_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.events.ticketing import TicketCheckedInEvent
from byceps.services.ticketing.dbmodels.checkin import DbTicketCheckIn
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import PartyID, UserID

from . import ticket_log_service, ticket_service
from .dbmodels.ticket import DbTicket
from .exceptions import (
    TicketBelongsToDifferentPartyError,
    TicketIsRevokedError,
    TicketLacksUserError,
    UserAccountDeletedError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
    UserIdUnknownError,
)
from .models.ticket import TicketCheckIn, TicketID


def check_in_user(
    party_id: PartyID, ticket_id: TicketID, initiator_id: UserID
) -> TicketCheckedInEvent:
    """Record that the ticket was used to check in its user."""
    db_ticket = _get_ticket_for_checkin(party_id, ticket_id)

    occurred_at = datetime.utcnow()
    initiator = user_service.get_user(initiator_id)

    user = _get_user_for_checkin(db_ticket.used_by_id)

    db_ticket.user_checked_in = True

    db_check_in = DbTicketCheckIn(occurred_at, db_ticket.id, initiator.id)
    db.session.add(db_check_in)

    db_log_entry = ticket_log_service.build_entry(
        'user-checked-in',
        db_ticket.id,
        {
            'checked_in_user_id': str(db_ticket.used_by_id),
            'initiator_id': str(initiator.id),
        },
        occurred_at=occurred_at,
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return TicketCheckedInEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        ticket_id=db_ticket.id,
        ticket_code=db_ticket.code,
        occupied_seat_id=db_ticket.occupied_seat_id,
        user_id=user.id,
        user_screen_name=user.screen_name,
    )


def _get_ticket_for_checkin(party_id: PartyID, ticket_id: TicketID) -> DbTicket:
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.party_id != party_id:
        raise TicketBelongsToDifferentPartyError(
            f'Ticket {ticket_id} belongs to another party ({db_ticket.party_id}).'
        )

    if db_ticket.revoked:
        raise TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')

    if db_ticket.used_by_id is None:
        raise TicketLacksUserError(f'Ticket {ticket_id} has no user assigned.')

    if db_ticket.user_checked_in:
        raise UserAlreadyCheckedInError(
            f'Ticket {ticket_id} has already been used to check in a user.'
        )

    return db_ticket


def _get_user_for_checkin(user_id: UserID) -> User:
    user = user_service.find_user(user_id)

    if user is None:
        raise UserIdUnknownError(f"Unknown user ID '{user_id}'")

    if user.deleted:
        raise UserAccountDeletedError(
            f'User account {user.screen_name} has been deleted.'
        )

    if user.suspended:
        raise UserAccountSuspendedError(
            f'User account {user.screen_name} is suspended.'
        )

    return user


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

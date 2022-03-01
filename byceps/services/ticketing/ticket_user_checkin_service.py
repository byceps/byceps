"""
byceps.services.ticketing.ticket_user_checkin_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...database import db
from ...events.ticketing import TicketCheckedIn
from ...typing import PartyID, UserID

from ..user import service as user_service
from ..user.transfer.models import User

from . import log_service
from .exceptions import (
    TicketBelongsToDifferentParty,
    TicketIsRevoked,
    TicketLacksUser,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAlreadyCheckedIn,
    UserIdUnknown,
)
from .dbmodels.ticket import Ticket as DbTicket
from . import ticket_service
from .transfer.models import TicketID


def check_in_user(
    party_id: PartyID, ticket_id: TicketID, initiator_id: UserID
) -> TicketCheckedIn:
    """Record that the ticket was used to check in its user."""
    db_ticket = _get_ticket_for_checkin(party_id, ticket_id)

    initiator = user_service.get_user(initiator_id)

    user = _get_user_for_checkin(db_ticket.used_by_id)

    db_ticket.user_checked_in = True

    db_log_entry = log_service.build_log_entry(
        'user-checked-in',
        db_ticket.id,
        {
            'checked_in_user_id': str(db_ticket.used_by_id),
            'initiator_id': str(initiator.id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return TicketCheckedIn(
        occurred_at=db_log_entry.occurred_at,
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
        raise TicketBelongsToDifferentParty(
            f'Ticket {ticket_id} belongs to another party ({db_ticket.party_id}).'
        )

    if db_ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    if db_ticket.used_by_id is None:
        raise TicketLacksUser(f'Ticket {ticket_id} has no user assigned.')

    if db_ticket.user_checked_in:
        raise UserAlreadyCheckedIn(
            f'Ticket {ticket_id} has already been used to check in a user.'
        )

    return db_ticket


def _get_user_for_checkin(user_id: UserID) -> User:
    user = user_service.find_user(user_id)

    if user is None:
        raise UserIdUnknown(f"Unknown user ID '{user_id}'")

    if user.deleted:
        raise UserAccountDeleted(
            f'User account {user.screen_name} has been deleted.'
        )

    if user.suspended:
        raise UserAccountSuspended(
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

    db_log_entry = log_service.build_log_entry(
        'user-check-in-reverted',
        db_ticket.id,
        {
            'checked_in_user_id': str(db_ticket.used_by_id),
            'initiator_id': str(initiator.id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

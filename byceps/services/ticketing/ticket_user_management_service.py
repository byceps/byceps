"""
byceps.services.ticketing.ticket_user_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.user import user_service
from byceps.typing import UserID

from . import ticket_log_service, ticket_service
from .exceptions import (
    TicketIsRevoked,
    UserAccountSuspended,
    UserAlreadyCheckedIn,
    UserIdUnknown,
)
from .models.ticket import TicketID


def appoint_user_manager(
    ticket_id: TicketID, manager_id: UserID, initiator_id: UserID
) -> None:
    """Appoint the user as the ticket's user manager."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    db_ticket.user_managed_by_id = manager_id

    db_log_entry = ticket_log_service.build_entry(
        'user-manager-appointed',
        db_ticket.id,
        {
            'appointed_user_manager_id': str(manager_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()


def withdraw_user_manager(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's custom user manager."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    db_ticket.user_managed_by_id = None

    db_log_entry = ticket_log_service.build_entry(
        'user-manager-withdrawn',
        db_ticket.id,
        {
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()


def appoint_user(
    ticket_id: TicketID, user_id: UserID, initiator_id: UserID
) -> None:
    """Appoint the user as the ticket's user."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    if db_ticket.user_checked_in:
        raise UserAlreadyCheckedIn('Ticket user has already been checked in.')

    user = user_service.find_user(user_id)
    if user is None:
        raise UserIdUnknown(f"Unknown user ID '{user_id}'")

    if user.suspended:
        raise UserAccountSuspended(
            f'User account {user.screen_name} is suspended.'
        )

    db_ticket.used_by_id = user_id

    db_log_entry = ticket_log_service.build_entry(
        'user-appointed',
        db_ticket.id,
        {
            'appointed_user_id': str(user_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()


def withdraw_user(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's user."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    if db_ticket.user_checked_in:
        raise UserAlreadyCheckedIn('Ticket user has already been checked in.')

    db_ticket.used_by_id = None

    db_log_entry = ticket_log_service.build_entry(
        'user-withdrawn',
        db_ticket.id,
        {
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

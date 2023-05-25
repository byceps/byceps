"""
byceps.services.ticketing.ticket_user_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.user import user_service
from byceps.typing import UserID
from byceps.util.result import Err, Ok, Result

from . import ticket_log_service, ticket_service
from .errors import (
    TicketingError,
    TicketIsRevokedError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
    UserIdUnknownError,
)
from .models.ticket import TicketID


def appoint_user_manager(
    ticket_id: TicketID, manager_id: UserID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Appoint the user as the ticket's user manager."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

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

    return Ok(None)


def withdraw_user_manager(
    ticket_id: TicketID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Withdraw the ticket's custom user manager."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

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

    return Ok(None)


def appoint_user(
    ticket_id: TicketID, user_id: UserID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Appoint the user as the ticket's user."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    if db_ticket.user_checked_in:
        return Err(
            UserAlreadyCheckedInError(
                'Ticket user has already been checked in.'
            )
        )

    user = user_service.find_user(user_id)
    if user is None:
        return Err(UserIdUnknownError(f"Unknown user ID '{user_id}'"))

    if user.suspended:
        return Err(
            UserAccountSuspendedError(
                f'User account {user.screen_name} is suspended.'
            )
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

    return Ok(None)


def withdraw_user(
    ticket_id: TicketID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Withdraw the ticket's user."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    if db_ticket.user_checked_in:
        return Err(
            UserAlreadyCheckedInError(
                'Ticket user has already been checked in.'
            )
        )

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

    return Ok(None)

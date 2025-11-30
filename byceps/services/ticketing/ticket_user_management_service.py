"""
byceps.services.ticketing.ticket_user_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import ticket_service
from .errors import (
    TicketingError,
    TicketIsRevokedError,
    UserAccountSuspendedError,
    UserAlreadyCheckedInError,
)
from .log import ticket_log_domain_service, ticket_log_service
from .models.ticket import TicketID


def appoint_user_manager(
    ticket_id: TicketID, manager: User, initiator: User
) -> Result[None, TicketingError]:
    """Appoint the user as the ticket's user manager."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    db_ticket.user_managed_by_id = manager.id

    log_entry = ticket_log_domain_service.build_user_manager_appointed_entry(
        db_ticket.id, manager, initiator
    )
    db_log_entry = ticket_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def withdraw_user_manager(
    ticket_id: TicketID, initiator: User
) -> Result[None, TicketingError]:
    """Withdraw the ticket's custom user manager."""
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    db_ticket.user_managed_by_id = None

    log_entry = ticket_log_domain_service.build_user_manager_withdrawn_entry(
        db_ticket.id, initiator
    )
    db_log_entry = ticket_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def appoint_user(
    ticket_id: TicketID, user: User, initiator: User
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

    if user.suspended:
        return Err(
            UserAccountSuspendedError(
                f'User account {user.screen_name} is suspended.'
            )
        )

    db_ticket.used_by_id = user.id

    log_entry = ticket_log_domain_service.build_user_appointed_entry(
        db_ticket.id, user, initiator
    )
    db_log_entry = ticket_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def withdraw_user(
    ticket_id: TicketID, initiator: User
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

    log_entry = ticket_log_domain_service.build_user_withdrawn_entry(
        db_ticket.id, initiator
    )
    db_log_entry = ticket_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)

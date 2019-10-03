"""
byceps.services.ticketing.ticket_user_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...typing import UserID

from ..user import service as user_service

from . import event_service
from .exceptions import TicketIsRevoked, UserAccountSuspended, \
    UserAlreadyCheckedIn, UserIdUnknown
from . import ticket_service
from .transfer.models import TicketID


def appoint_user_manager(
    ticket_id: TicketID, manager_id: UserID, initiator_id: UserID
) -> None:
    """Appoint the user as the ticket's user manager."""
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    ticket.user_managed_by_id = manager_id

    event = event_service.build_event('user-manager-appointed', ticket.id, {
        'appointed_user_manager_id': str(manager_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def withdraw_user_manager(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's custom user manager."""
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    ticket.user_managed_by_id = None

    event = event_service.build_event('user-manager-withdrawn', ticket.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def appoint_user(
    ticket_id: TicketID, user_id: UserID, initiator_id: UserID
) -> None:
    """Appoint the user as the ticket's user."""
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    if ticket.user_checked_in:
        raise UserAlreadyCheckedIn('Ticket user has already been checked in.')

    user = user_service.find_user(user_id)
    if user is None:
        raise UserIdUnknown("Unknown user ID '{}'.".format(user_id))

    if user.suspended:
        raise UserAccountSuspended(
            'User account {} is suspended.'.format(user.screen_name))

    ticket.used_by_id = user_id

    event = event_service.build_event('user-appointed', ticket.id, {
        'appointed_user_id': str(user_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def withdraw_user(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's user."""
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    if ticket.user_checked_in:
        raise UserAlreadyCheckedIn('Ticket user has already been checked in.')

    ticket.used_by_id = None

    event = event_service.build_event('user-withdrawn', ticket.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()

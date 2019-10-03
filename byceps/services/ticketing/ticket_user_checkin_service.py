"""
byceps.services.ticketing.ticket_user_checkin_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...typing import UserID

from ..user import service as user_service

from . import event_service
from .exceptions import (
    TicketIsRevoked,
    TicketLacksUser,
    UserAccountDeleted,
    UserAccountSuspended,
    UserAlreadyCheckedIn,
    UserIdUnknown,
)
from . import ticket_service
from .transfer.models import TicketID


def check_in_user(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Record that the ticket was used to check in its user."""
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    if ticket.used_by_id is None:
        raise TicketLacksUser(
            'Ticket {} has no user assigned.'.format(ticket_id))

    if ticket.user_checked_in:
        raise UserAlreadyCheckedIn(
            'Ticket {} has already been used to check in a user.'
                .format(ticket_id))

    user = user_service.find_user(ticket.used_by_id)
    if user is None:
        raise UserIdUnknown("Unknown user ID '{}'.".format(ticket.used_by_id))

    if user.deleted:
        raise UserAccountDeleted(
            'User account {} has been deleted.'.format(user.screen_name))

    if user.suspended:
        raise UserAccountSuspended(
            'User account {} is suspended.'.format(user.screen_name))

    ticket.user_checked_in = True

    event = event_service.build_event('user-checked-in', ticket.id, {
        'checked_in_user_id': str(ticket.used_by_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def revert_user_check_in(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Revert a user check-in that was done by mistake."""
    ticket = ticket_service.find_ticket(ticket_id)

    if not ticket.user_checked_in:
        raise ValueError(
            'User of ticket {} has not been checked in.'.format(ticket_id))

    ticket.user_checked_in = False

    event = event_service.build_event('user-check-in-reverted', ticket.id, {
        'checked_in_user_id': str(ticket.used_by_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()

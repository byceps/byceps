"""
byceps.services.ticketing.ticket_seat_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db
from ...typing import UserID

from ..seating.models.seat import Seat as DbSeat
from ..seating import seat_service
from ..seating.transfer.models import SeatID

from . import event_service
from .exceptions import (
    SeatChangeDeniedForBundledTicket,
    SeatChangeDeniedForGroupSeat,
    TicketCategoryMismatch,
    TicketIsRevoked,
)
from .models.ticket import Ticket as DbTicket
from . import ticket_service
from .transfer.models import TicketID


def appoint_seat_manager(
    ticket_id: TicketID, manager_id: UserID, initiator_id: UserID
) -> None:
    """Appoint the user as the ticket's seat manager."""
    ticket = _get_ticket(ticket_id)

    ticket.seat_managed_by_id = manager_id

    event = event_service.build_event(
        'seat-manager-appointed',
        ticket.id,
        {
            'appointed_seat_manager_id': str(manager_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(event)

    db.session.commit()


def withdraw_seat_manager(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's custom seat manager."""
    ticket = _get_ticket(ticket_id)

    ticket.seat_managed_by_id = None

    event = event_service.build_event(
        'seat-manager-withdrawn',
        ticket.id,
        {
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(event)

    db.session.commit()


def occupy_seat(
    ticket_id: TicketID, seat_id: SeatID, initiator_id: UserID
) -> None:
    """Occupy the seat with this ticket."""
    ticket = _get_ticket(ticket_id)

    _deny_seat_management_if_ticket_belongs_to_bundle(ticket)

    seat = seat_service.find_seat(seat_id)
    if seat is None:
        raise ValueError('Invalid seat ID')

    if seat.category_id != ticket.category_id:
        raise TicketCategoryMismatch(
            'Ticket and seat belong to different categories.'
        )

    _deny_seat_management_if_seat_belongs_to_group(seat)

    previous_seat_id = ticket.occupied_seat_id

    ticket.occupied_seat_id = seat.id

    event_data = {
        'seat_id': str(seat.id),
        'initiator_id': str(initiator_id),
    }
    if previous_seat_id is not None:
        event_data['previous_seat_id'] = str(previous_seat_id)

    event = event_service.build_event('seat-occupied', ticket.id, event_data)
    db.session.add(event)

    db.session.commit()


def release_seat(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Release the seat occupied by this ticket."""
    ticket = _get_ticket(ticket_id)

    _deny_seat_management_if_ticket_belongs_to_bundle(ticket)

    seat = seat_service.find_seat(ticket.occupied_seat_id)
    if seat is None:
        raise ValueError('Ticket does not occupy a seat.')

    _deny_seat_management_if_seat_belongs_to_group(seat)

    ticket.occupied_seat_id = None

    event = event_service.build_event(
        'seat-released',
        ticket.id,
        {
            'seat_id': str(seat.id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(event)

    db.session.commit()


def _get_ticket(ticket_id: TicketID) -> DbTicket:
    """Return the ticket with that ID.

    Raise an exception if the ID is unknown or if the ticket has been
    revoked.
    """
    ticket = ticket_service.find_ticket(ticket_id)

    if ticket is None:
        raise ValueError(f'Unknown ticket ID "{ticket_id}"')

    if ticket.revoked:
        raise TicketIsRevoked(f'Ticket {ticket_id} has been revoked.')

    return ticket


def _deny_seat_management_if_ticket_belongs_to_bundle(ticket: DbTicket) -> None:
    """Raise an exception if this ticket belongs to a bundle.

    A ticket bundle is meant to occupy a matching seat group with the
    appropriate mechanism, not to separately occupy single seats.
    """
    if ticket.belongs_to_bundle:
        raise SeatChangeDeniedForBundledTicket(
            f"Ticket '{ticket.code}' belongs to a bundle and, thus, "
            'must not be used to occupy or release a single seat.'
        )


def _deny_seat_management_if_seat_belongs_to_group(seat: DbSeat) -> None:
    if seat.assignment is not None:
        raise SeatChangeDeniedForGroupSeat(
            f"Seat '{seat.label}' belongs to a group and, thus, "
            'cannot be occupied by a single ticket, or removed separately.'
        )

"""
byceps.services.ticketing.ticket_seat_management_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.database import db
from byceps.services.seating import seat_group_service, seat_service
# Load `Seat.assignment` backref.
from byceps.services.seating.dbmodels.seat_group import DbSeatGroup  # noqa: F401
from byceps.services.seating.models import Seat, SeatID
from byceps.typing import UserID
from byceps.util.result import Err, Ok, Result

from . import ticket_log_service, ticket_service
from .dbmodels.ticket import DbTicket
from .errors import (
    SeatChangeDeniedForBundledTicketError,
    SeatChangeDeniedForGroupSeatError,
    TicketCategoryMismatchError,
    TicketingError,
    TicketIsRevokedError,
)
from .models.ticket import TicketID


def appoint_seat_manager(
    ticket_id: TicketID, manager_id: UserID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Appoint the user as the ticket's seat manager."""
    db_ticket_result = _get_ticket(ticket_id)
    if db_ticket_result.is_err():
        return Err(db_ticket_result.unwrap_err())

    db_ticket = db_ticket_result.unwrap()

    db_ticket.seat_managed_by_id = manager_id

    db_log_entry = ticket_log_service.build_db_entry(
        'seat-manager-appointed',
        db_ticket.id,
        {
            'appointed_seat_manager_id': str(manager_id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def withdraw_seat_manager(
    ticket_id: TicketID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Withdraw the ticket's custom seat manager."""
    db_ticket_result = _get_ticket(ticket_id)
    if db_ticket_result.is_err():
        return Err(db_ticket_result.unwrap_err())

    db_ticket = db_ticket_result.unwrap()

    db_ticket.seat_managed_by_id = None

    db_log_entry = ticket_log_service.build_db_entry(
        'seat-manager-withdrawn',
        db_ticket.id,
        {
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def occupy_seat(
    ticket_id: TicketID, seat_id: SeatID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Occupy the seat with this ticket."""
    db_ticket_result = _get_ticket(ticket_id)
    if db_ticket_result.is_err():
        return Err(db_ticket_result.unwrap_err())

    db_ticket = db_ticket_result.unwrap()

    ticket_belongs_to_bundle_result = (
        _deny_seat_management_if_ticket_belongs_to_bundle(db_ticket)
    )
    if ticket_belongs_to_bundle_result.is_err():
        return Err(ticket_belongs_to_bundle_result.unwrap_err())

    seat = seat_service.get_seat(seat_id)

    if seat.category_id != db_ticket.category_id:
        return Err(
            TicketCategoryMismatchError(
                'Ticket and seat belong to different categories.'
            )
        )

    seat_belongs_to_group_result = (
        _deny_seat_management_if_seat_belongs_to_group(seat)
    )
    if seat_belongs_to_group_result.is_err():
        return Err(seat_belongs_to_group_result.unwrap_err())

    previous_seat_id = db_ticket.occupied_seat_id

    db_ticket.occupied_seat_id = seat.id

    log_entry_data = {
        'seat_id': str(seat.id),
        'initiator_id': str(initiator_id),
    }
    if previous_seat_id is not None:
        log_entry_data['previous_seat_id'] = str(previous_seat_id)

    db_log_entry = ticket_log_service.build_db_entry(
        'seat-occupied', db_ticket.id, log_entry_data
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def release_seat(
    ticket_id: TicketID, initiator_id: UserID
) -> Result[None, TicketingError]:
    """Release the seat occupied by this ticket."""
    db_ticket_result = _get_ticket(ticket_id)
    if db_ticket_result.is_err():
        return Err(db_ticket_result.unwrap_err())

    db_ticket = db_ticket_result.unwrap()

    ticket_belongs_to_bundle_result = (
        _deny_seat_management_if_ticket_belongs_to_bundle(db_ticket)
    )
    if ticket_belongs_to_bundle_result.is_err():
        return Err(ticket_belongs_to_bundle_result.unwrap_err())

    seat = seat_service.find_seat(db_ticket.occupied_seat_id)
    if seat is None:
        raise ValueError('Ticket does not occupy a seat.')

    seat_belongs_to_group_result = (
        _deny_seat_management_if_seat_belongs_to_group(seat)
    )
    if seat_belongs_to_group_result.is_err():
        return Err(seat_belongs_to_group_result.unwrap_err())

    db_ticket.occupied_seat_id = None

    db_log_entry = ticket_log_service.build_db_entry(
        'seat-released',
        db_ticket.id,
        {
            'seat_id': str(seat.id),
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(None)


def _get_ticket(ticket_id: TicketID) -> Result[DbTicket, TicketIsRevokedError]:
    """Return the ticket with that ID.

    Raise an exception if the ID is unknown.

    Return an error if the ticket has been revoked.
    """
    db_ticket = ticket_service.get_ticket(ticket_id)

    if db_ticket.revoked:
        return Err(
            TicketIsRevokedError(f'Ticket {ticket_id} has been revoked.')
        )

    return Ok(db_ticket)


def _deny_seat_management_if_ticket_belongs_to_bundle(
    db_ticket: DbTicket,
) -> Result[None, SeatChangeDeniedForBundledTicketError]:
    """Return an error if this ticket belongs to a bundle.

    A ticket bundle is meant to occupy a matching seat group with the
    appropriate mechanism, not to separately occupy single seats.
    """
    if db_ticket.belongs_to_bundle:
        return Err(
            SeatChangeDeniedForBundledTicketError(
                f"Ticket '{db_ticket.code}' belongs to a bundle and, thus, "
                'must not be used to occupy or release a single seat.'
            )
        )

    return Ok(None)


def _deny_seat_management_if_seat_belongs_to_group(
    seat: Seat,
) -> Result[None, SeatChangeDeniedForGroupSeatError]:
    if seat_group_service.is_seat_part_of_a_group(seat.id):
        return Err(
            SeatChangeDeniedForGroupSeatError(
                f"Seat '{seat.label}' belongs to a group and, thus, "
                'cannot be occupied by a single ticket, or removed separately.'
            )
        )

    return Ok(None)

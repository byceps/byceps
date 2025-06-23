"""
byceps.services.seating.seat_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import select

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.dbmodels.ticket_bundle import DbTicketBundle
from byceps.services.ticketing.models.ticket import (
    TicketBundleID,
    TicketCategoryID,
)
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels.seat import DbSeat
from .dbmodels.seat_group import (
    DbSeatGroup,
    DbSeatGroupAssignment,
    DbSeatGroupOccupancy,
)
from .errors import SeatingError
from .models import Seat, SeatGroup, SeatGroupID, SeatID


def create_seat_group(
    party_id: PartyID,
    ticket_category_id: TicketCategoryID,
    title: str,
    seats: Sequence[Seat],
) -> Result[SeatGroup, SeatingError]:
    """Create a seat group and assign the given seats."""
    seat_quantity = len(seats)
    if seat_quantity == 0:
        return Err(SeatingError('No seats specified.'))

    ticket_category_ids = {seat.category_id for seat in seats}
    if len(ticket_category_ids) != 1 or (
        ticket_category_id not in ticket_category_ids
    ):
        return Err(
            SeatingError("Seats' ticket category IDs do not match the group's.")
        )

    group_id = SeatGroupID(generate_uuid7())

    group = SeatGroup(
        id=group_id,
        party_id=party_id,
        ticket_category_id=ticket_category_id,
        seat_quantity=seat_quantity,
        title=title,
        seats=list(seats),
    )

    db_group = DbSeatGroup(
        group.id,
        group.party_id,
        group.ticket_category_id,
        seat_quantity,
        group.title,
    )
    db.session.add(db_group)

    for seat in seats:
        assignment_id = generate_uuid7()
        db_assignment = DbSeatGroupAssignment(assignment_id, db_group, seat.id)
        db.session.add(db_assignment)

    db.session.commit()

    return Ok(group)


def occupy_seat_group(
    db_seat_group: DbSeatGroup, db_ticket_bundle: DbTicketBundle
) -> Result[DbSeatGroupOccupancy, SeatingError]:
    """Occupy the seat group with that ticket bundle."""
    db_seats = db_seat_group.seats
    db_tickets = db_ticket_bundle.tickets

    group_availability_result = _ensure_group_is_available(db_seat_group)
    if group_availability_result.is_err():
        return Err(group_availability_result.unwrap_err())

    categories_match_result = _ensure_categories_match(
        db_seat_group, db_ticket_bundle
    )
    if categories_match_result.is_err():
        return Err(categories_match_result.unwrap_err())

    quantities_match_result = _ensure_quantities_match(
        db_seat_group, db_ticket_bundle
    )
    if quantities_match_result.is_err():
        return Err(quantities_match_result.unwrap_err())

    actual_quantities_match_result = _ensure_actual_quantities_match(
        db_seats, db_tickets
    )
    if actual_quantities_match_result.is_err():
        return Err(actual_quantities_match_result.unwrap_err())

    occupancy_id = generate_uuid7()
    db_occupancy = DbSeatGroupOccupancy(
        occupancy_id, db_seat_group.id, db_ticket_bundle.id
    )
    db.session.add(db_occupancy)

    occupy_seats_result = _occupy_seats(db_seats, db_tickets)
    if occupy_seats_result.is_err():
        return Err(occupy_seats_result.unwrap_err())

    db.session.commit()

    return Ok(db_occupancy)


def switch_seat_group(
    db_occupancy: DbSeatGroupOccupancy, db_to_group: DbSeatGroup
) -> Result[None, SeatingError]:
    """Switch ticket bundle to another seat group."""
    db_ticket_bundle = db_occupancy.ticket_bundle
    db_tickets = db_ticket_bundle.tickets
    db_seats = db_to_group.seats

    group_availability_result = _ensure_group_is_available(db_to_group)
    if group_availability_result.is_err():
        return Err(group_availability_result.unwrap_err())

    categories_match_result = _ensure_categories_match(
        db_to_group, db_ticket_bundle
    )
    if categories_match_result.is_err():
        return Err(categories_match_result.unwrap_err())

    quantities_match_result = _ensure_quantities_match(
        db_to_group, db_ticket_bundle
    )
    if quantities_match_result.is_err():
        return Err(quantities_match_result.unwrap_err())

    actual_quantities_match_result = _ensure_actual_quantities_match(
        db_seats, db_tickets
    )
    if actual_quantities_match_result.is_err():
        return Err(actual_quantities_match_result.unwrap_err())

    db_occupancy.seat_group_id = db_to_group.id

    occupy_seats_result = _occupy_seats(db_seats, db_tickets)
    if occupy_seats_result.is_err():
        return Err(occupy_seats_result.unwrap_err())

    db.session.commit()

    return Ok(None)


def _ensure_group_is_available(
    db_seat_group: DbSeatGroup,
) -> Result[None, SeatingError]:
    """Return an error if the seat group is occupied."""
    occupancy = find_occupancy_for_seat_group(db_seat_group.id)
    if occupancy is not None:
        return Err(SeatingError('Seat group is already occupied.'))

    return Ok(None)


def _ensure_categories_match(
    db_seat_group: DbSeatGroup, db_ticket_bundle: DbTicketBundle
) -> Result[None, SeatingError]:
    """Return an error if the seat group's and the ticket bundle's
    categories don't match.
    """
    if db_seat_group.ticket_category_id != db_ticket_bundle.ticket_category_id:
        return Err(SeatingError('Seat and ticket categories do not match.'))

    return Ok(None)


def _ensure_quantities_match(
    db_seat_group: DbSeatGroup, db_ticket_bundle: DbTicketBundle
) -> Result[None, SeatingError]:
    """Return an error if the seat group's and the ticket bundle's
    quantities don't match.
    """
    if db_seat_group.seat_quantity != db_ticket_bundle.ticket_quantity:
        return Err(SeatingError('Seat and ticket quantities do not match.'))

    return Ok(None)


def _ensure_actual_quantities_match(
    db_seats: Sequence[DbSeat], db_tickets: Sequence[DbTicket]
) -> Result[None, SeatingError]:
    """Return an error if the totals of seats and tickets don't match."""
    if len(db_seats) != len(db_tickets):
        return Err(
            SeatingError(
                'The actual quantities of seats and tickets do not match.'
            )
        )

    return Ok(None)


def _occupy_seats(
    db_seats: Sequence[DbSeat], db_tickets: Sequence[DbTicket]
) -> Result[None, SeatingError]:
    """Occupy all seats in the group with all tickets from the bundle."""
    db_seats = _sort_seats(db_seats)
    for db_seat in db_seats:
        already_occupying_ticket = db_seat.occupied_by_ticket
        if already_occupying_ticket:
            return Err(
                SeatingError(
                    f'Seat {db_seat.id} is already occupied by ticket {already_occupying_ticket.id}; seat cannot be occupied.'
                )
            )

    db_tickets = _sort_tickets(db_tickets)
    for db_ticket in db_tickets:
        if db_ticket.revoked:
            return Err(
                SeatingError(
                    f'Ticket {db_ticket.id} is revoked; it cannot be used to occupy a seat.'
                )
            )

    for db_seat, db_ticket in zip(db_seats, db_tickets, strict=True):
        db_ticket.occupied_seat = db_seat

    return Ok(None)


def _sort_seats(db_seats: Sequence[DbSeat]) -> list[DbSeat]:
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(db_seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(db_tickets: Sequence[DbTicket]) -> list[DbTicket]:
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(db_tickets, key=lambda t: t.created_at))


def release_seat_group(
    seat_group_id: SeatGroupID,
) -> Result[None, SeatingError]:
    """Release a seat group so it becomes available again."""
    db_occupancy = find_occupancy_for_seat_group(seat_group_id)
    if db_occupancy is None:
        return Err(SeatingError('Seat group is not occupied.'))

    for db_ticket in db_occupancy.ticket_bundle.tickets:
        db_ticket.occupied_seat = None

    db.session.delete(db_occupancy)

    db.session.commit()

    return Ok(None)


def count_seat_groups_for_party(party_id: PartyID) -> int:
    """Return the number of seat groups for that party."""
    return (
        db.session.scalar(
            select(db.func.count(DbSeatGroup.id)).filter_by(party_id=party_id)
        )
        or 0
    )


def find_seat_group(seat_group_id: SeatGroupID) -> DbSeatGroup | None:
    """Return the seat group with that id, or `None` if not found."""
    return db.session.get(DbSeatGroup, seat_group_id)


def find_seat_group_occupied_by_ticket_bundle(
    ticket_bundle_id: TicketBundleID,
) -> SeatGroupID | None:
    """Return the ID of the seat group occupied by that ticket bundle,
    or `None` if not found.
    """
    return db.session.execute(
        select(DbSeatGroupOccupancy.seat_group_id).filter_by(
            ticket_bundle_id=ticket_bundle_id
        )
    ).scalar_one_or_none()


def find_occupancy_for_seat_group(
    seat_group_id: SeatGroupID,
) -> DbSeatGroupOccupancy | None:
    """Return the occupancy for that seat group, or `None` if not found."""
    return db.session.execute(
        select(DbSeatGroupOccupancy).filter_by(seat_group_id=seat_group_id)
    ).scalar_one_or_none()


def get_all_seat_groups_for_party(party_id: PartyID) -> Sequence[DbSeatGroup]:
    """Return all seat groups for that party."""
    return db.session.scalars(
        select(DbSeatGroup).filter_by(party_id=party_id)
    ).all()


def is_seat_part_of_a_group(seat_id: SeatID) -> bool:
    """Return whether or not the seat is part of a seat group."""
    return (
        db.session.scalar(
            select(
                select(DbSeatGroupAssignment)
                .filter_by(seat_id=seat_id)
                .exists()
            )
        )
        or False
    )

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
from byceps.services.ticketing import ticket_bundle_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.dbmodels.ticket_bundle import DbTicketBundle
from byceps.services.ticketing.models.ticket import (
    TicketBundle,
    TicketBundleID,
    TicketCategoryID,
)
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from . import seat_service
from .dbmodels.seat_group import (
    DbSeatGroup,
    DbSeatGroupAssignment,
    DbSeatGroupOccupancy,
)
from .errors import SeatingError
from .models import Seat, SeatGroup, SeatGroupID, SeatID


def create_group(
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


def occupy_group(
    group: SeatGroup, db_ticket_bundle: DbTicketBundle
) -> Result[DbSeatGroupOccupancy, SeatingError]:
    """Occupy the seat group with that ticket bundle."""
    ticket_bundle = ticket_bundle_service.db_entity_to_ticket_bundle(
        db_ticket_bundle
    )

    db_tickets = db_ticket_bundle.tickets

    group_availability_result = _ensure_group_is_available(group)
    if group_availability_result.is_err():
        return Err(group_availability_result.unwrap_err())

    categories_match_result = _ensure_categories_match(group, ticket_bundle)
    if categories_match_result.is_err():
        return Err(categories_match_result.unwrap_err())

    quantities_match_result = _ensure_quantities_match(group, ticket_bundle)
    if quantities_match_result.is_err():
        return Err(quantities_match_result.unwrap_err())

    occupancy_id = generate_uuid7()
    db_occupancy = DbSeatGroupOccupancy(
        occupancy_id, group.id, ticket_bundle.id
    )
    db.session.add(db_occupancy)

    occupy_seats_result = _occupy_seats(group.seats, db_tickets)
    if occupy_seats_result.is_err():
        return Err(occupy_seats_result.unwrap_err())

    db.session.commit()

    return Ok(db_occupancy)


def switch_group(
    db_occupancy: DbSeatGroupOccupancy, target_group: SeatGroup
) -> Result[None, SeatingError]:
    """Switch ticket bundle to another seat group."""
    db_ticket_bundle = db_occupancy.ticket_bundle
    ticket_bundle = ticket_bundle_service.db_entity_to_ticket_bundle(
        db_ticket_bundle
    )

    db_tickets = db_ticket_bundle.tickets

    group_availability_result = _ensure_group_is_available(target_group)
    if group_availability_result.is_err():
        return Err(group_availability_result.unwrap_err())

    categories_match_result = _ensure_categories_match(
        target_group, ticket_bundle
    )
    if categories_match_result.is_err():
        return Err(categories_match_result.unwrap_err())

    quantities_match_result = _ensure_quantities_match(
        target_group, ticket_bundle
    )
    if quantities_match_result.is_err():
        return Err(quantities_match_result.unwrap_err())

    db_occupancy.seat_group_id = target_group.id

    occupy_seats_result = _occupy_seats(target_group.seats, db_tickets)
    if occupy_seats_result.is_err():
        return Err(occupy_seats_result.unwrap_err())

    db.session.commit()

    return Ok(None)


def _ensure_group_is_available(
    group: SeatGroup,
) -> Result[None, SeatingError]:
    """Return an error if the seat group is occupied."""
    occupancy = find_occupancy_for_group(group.id)
    if occupancy is not None:
        return Err(SeatingError('Seat group is already occupied.'))

    return Ok(None)


def _ensure_categories_match(
    group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[None, SeatingError]:
    """Return an error if the seat group's and the ticket bundle's
    categories don't match.
    """
    if group.ticket_category_id != ticket_bundle.ticket_category.id:
        return Err(SeatingError('Seat and ticket categories do not match.'))

    return Ok(None)


def _ensure_quantities_match(
    group: SeatGroup, ticket_bundle: TicketBundle
) -> Result[None, SeatingError]:
    """Return an error if

    - the defined and actual seat quantity of the seat group or
    - the defined and actual ticket quantity of the ticket bundle or
    - the defined quantities of the seat group and the ticket bundle or
    - the actual quantities of seats and tickets

    don't match.
    """
    if group.seat_quantity != len(group.seats):
        return Err(
            SeatingError(
                'Defined and actual seat quantities in seat group do not match.'
            )
        )

    if ticket_bundle.ticket_quantity != len(ticket_bundle.ticket_ids):
        return Err(
            SeatingError(
                'Defined and actual ticket quantities in tucket bundle do not match.'
            )
        )

    if group.seat_quantity != ticket_bundle.ticket_quantity:
        return Err(SeatingError('Seat and ticket quantities do not match.'))

    if len(group.seats) != len(ticket_bundle.ticket_ids):
        return Err(
            SeatingError(
                'The actual quantities of seats and tickets do not match.'
            )
        )

    return Ok(None)


def _occupy_seats(
    seats: list[Seat], db_tickets: Sequence[DbTicket]
) -> Result[None, SeatingError]:
    """Occupy all seats in the group with all tickets from the bundle."""
    for seat in seats:
        already_occupying_ticket = seat.occupied_by_ticket_id is not None
        if already_occupying_ticket:
            return Err(
                SeatingError(
                    f'Seat {seat.id} is already occupied by ticket {already_occupying_ticket.id}; seat cannot be occupied.'
                )
            )

    for db_ticket in db_tickets:
        if db_ticket.revoked:
            return Err(
                SeatingError(
                    f'Ticket {db_ticket.id} is revoked; it cannot be used to occupy a seat.'
                )
            )

    seats = _sort_seats(seats)
    db_tickets = _sort_tickets(db_tickets)

    for seat, db_ticket in zip(seats, db_tickets, strict=True):
        db_ticket.occupied_seat_id = seat.id

    return Ok(None)


def _sort_seats(seats: list[Seat]) -> list[Seat]:
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(db_tickets: Sequence[DbTicket]) -> list[DbTicket]:
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(db_tickets, key=lambda t: t.created_at))


def release_group(
    group_id: SeatGroupID,
) -> Result[None, SeatingError]:
    """Release a seat group so it becomes available again."""
    db_occupancy = find_occupancy_for_group(group_id)
    if db_occupancy is None:
        return Err(SeatingError('Seat group is not occupied.'))

    for db_ticket in db_occupancy.ticket_bundle.tickets:
        db_ticket.occupied_seat = None

    db.session.delete(db_occupancy)

    db.session.commit()

    return Ok(None)


def count_groups_for_party(party_id: PartyID) -> int:
    """Return the number of seat groups for that party."""
    return (
        db.session.scalar(
            select(db.func.count(DbSeatGroup.id)).filter_by(party_id=party_id)
        )
        or 0
    )


def find_group(group_id: SeatGroupID) -> SeatGroup | None:
    """Return the seat group with that id, or `None` if not found."""
    db_group = db.session.get(DbSeatGroup, group_id)

    if db_group is None:
        return None

    seat_ids = {db_seat.id for db_seat in db_group.seats}
    seats = seat_service.get_seats(seat_ids)

    return _db_entity_to_group(db_group, seats)


def find_group_occupied_by_ticket_bundle(
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


def find_occupancy_for_group(
    group_id: SeatGroupID,
) -> DbSeatGroupOccupancy | None:
    """Return the occupancy for that seat group, or `None` if not found."""
    return db.session.execute(
        select(DbSeatGroupOccupancy).filter_by(seat_group_id=group_id)
    ).scalar_one_or_none()


def get_all_groups_for_party(party_id: PartyID) -> Sequence[DbSeatGroup]:
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


def _db_entity_to_group(db_group: DbSeatGroup, seats: list[Seat]) -> SeatGroup:
    return SeatGroup(
        id=db_group.id,
        party_id=db_group.party_id,
        ticket_category_id=db_group.ticket_category_id,
        seat_quantity=db_group.seat_quantity,
        title=db_group.title,
        seats=seats,
    )

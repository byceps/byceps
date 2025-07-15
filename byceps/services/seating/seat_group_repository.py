"""
byceps.services.seating.seat_group_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import select, delete

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketBundleID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels.seat_group import (
    DbSeatGroup,
    DbSeatGroupAssignment,
    DbSeatGroupOccupancy,
)
from .errors import SeatingError
from .models import Seat, SeatGroup, SeatGroupID, SeatGroupOccupancy, SeatID


def create_group(group: SeatGroup) -> None:
    """Create a seat group and assign the given seats."""
    db_group = DbSeatGroup(
        group.id,
        group.party_id,
        group.ticket_category_id,
        group.seat_quantity,
        group.title,
    )
    db.session.add(db_group)

    for seat in group.seats:
        assignment_id = generate_uuid7()
        db_assignment = DbSeatGroupAssignment(assignment_id, db_group, seat.id)
        db.session.add(db_assignment)

    db.session.commit()


def occupy_group(
    group: SeatGroup,
    occupancy: SeatGroupOccupancy,
    db_tickets: Sequence[DbTicket],
) -> Result[None, SeatingError]:
    """Occupy the seat group."""
    db_occupancy = DbSeatGroupOccupancy(
        occupancy.id, occupancy.group_id, occupancy.ticket_bundle_id
    )
    db.session.add(db_occupancy)

    occupy_seats_result = _occupy_seats(group.seats, db_tickets)
    if occupy_seats_result.is_err():
        return Err(occupy_seats_result.unwrap_err())

    db.session.commit()

    return Ok(None)


def switch_group(
    occupancy: SeatGroupOccupancy,
    target_group: SeatGroup,
    db_tickets: Sequence[DbTicket],
) -> Result[None, SeatingError]:
    """Switch ticket bundle to another seat group."""
    db_occupancy = db.session.execute(
        select(DbSeatGroupOccupancy).filter_by(seat_group_id=occupancy.group_id)
    ).scalar_one_or_none()
    if db_occupancy is None:
        return Err(SeatingError('Seat group occupancy not found in database.'))

    db_occupancy.seat_group_id = target_group.id

    occupy_seats_result = _occupy_seats(target_group.seats, db_tickets)
    if occupy_seats_result.is_err():
        return Err(occupy_seats_result.unwrap_err())

    db.session.commit()

    return Ok(None)


def _occupy_seats(
    seats: list[Seat], db_tickets: Sequence[DbTicket]
) -> Result[None, SeatingError]:
    """Occupy all seats in the group with all tickets from the bundle."""
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


def _sort_seats(seats: Sequence[Seat]) -> list[Seat]:
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(db_tickets: Sequence[DbTicket]) -> list[DbTicket]:
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(db_tickets, key=lambda t: t.created_at))


def release_group(group_id: SeatGroupID) -> Result[None, SeatingError]:
    """Release a seat group so it becomes available again."""
    db_occupancy = find_occupancy_for_group(group_id)
    if db_occupancy is None:
        return Err(SeatingError('Seat group is not occupied.'))

    for db_ticket in db_occupancy.ticket_bundle.tickets:
        db_ticket.occupied_seat = None

    db.session.execute(
        delete(DbSeatGroupOccupancy).filter_by(id=db_occupancy.id)
    )

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


def find_group(group_id: SeatGroupID) -> tuple[DbSeatGroup, set[SeatID]] | None:
    """Return the seat group with that id, or `None` if not found."""
    db_group = db.session.get(DbSeatGroup, group_id)

    if db_group is None:
        return None

    seat_ids = {db_seat.id for db_seat in db_group.seats}

    return db_group, seat_ids


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


def get_groups_for_party(party_id: PartyID) -> Sequence[DbSeatGroup]:
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

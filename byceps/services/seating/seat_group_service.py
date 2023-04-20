"""
byceps.services.seating.seat_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional, Sequence

from sqlalchemy import select

from ...database import db
from ...typing import PartyID

from ..ticketing.dbmodels.ticket import DbTicket
from ..ticketing.dbmodels.ticket_bundle import DbTicketBundle
from ..ticketing.models.ticket import TicketBundleID, TicketCategoryID

from .dbmodels.seat import DbSeat
from .dbmodels.seat_group import (
    DbSeatGroup,
    DbSeatGroupAssignment,
    DbSeatGroupOccupancy,
)
from .models import Seat, SeatGroupID, SeatID


def create_seat_group(
    party_id: PartyID,
    ticket_category_id: TicketCategoryID,
    title: str,
    seats: Sequence[Seat],
) -> DbSeatGroup:
    """Create a seat group and assign the given seats."""
    seat_quantity = len(seats)
    if seat_quantity == 0:
        raise ValueError("No seats specified.")

    ticket_category_ids = {seat.category_id for seat in seats}
    if len(ticket_category_ids) != 1 or (
        ticket_category_id not in ticket_category_ids
    ):
        raise ValueError("Seats' ticket category IDs do not match the group's.")

    db_group = DbSeatGroup(party_id, ticket_category_id, seat_quantity, title)
    db.session.add(db_group)

    for seat in seats:
        db_assignment = DbSeatGroupAssignment(db_group, seat.id)
        db.session.add(db_assignment)

    db.session.commit()

    return db_group


def occupy_seat_group(
    db_seat_group: DbSeatGroup, db_ticket_bundle: DbTicketBundle
) -> DbSeatGroupOccupancy:
    """Occupy the seat group with that ticket bundle."""
    db_seats = db_seat_group.seats
    db_tickets = db_ticket_bundle.tickets

    _ensure_group_is_available(db_seat_group)
    _ensure_categories_match(db_seat_group, db_ticket_bundle)
    _ensure_quantities_match(db_seat_group, db_ticket_bundle)
    _ensure_actual_quantities_match(db_seats, db_tickets)

    db_occupancy = DbSeatGroupOccupancy(db_seat_group.id, db_ticket_bundle.id)
    db.session.add(db_occupancy)

    _occupy_seats(db_seats, db_tickets)

    db.session.commit()

    return db_occupancy


def switch_seat_group(
    db_occupancy: DbSeatGroupOccupancy, db_to_group: DbSeatGroup
) -> None:
    """Switch ticket bundle to another seat group."""
    db_ticket_bundle = db_occupancy.ticket_bundle
    db_tickets = db_ticket_bundle.tickets
    db_seats = db_to_group.seats

    _ensure_group_is_available(db_to_group)
    _ensure_categories_match(db_to_group, db_ticket_bundle)
    _ensure_quantities_match(db_to_group, db_ticket_bundle)
    _ensure_actual_quantities_match(db_seats, db_tickets)

    db_occupancy.seat_group_id = db_to_group.id

    _occupy_seats(db_seats, db_tickets)

    db.session.commit()


def _ensure_group_is_available(db_seat_group: DbSeatGroup) -> None:
    """Raise an error if the seat group is occupied."""
    occupancy = find_occupancy_for_seat_group(db_seat_group.id)
    if occupancy is not None:
        raise ValueError('Seat group is already occupied.')


def _ensure_categories_match(
    db_seat_group: DbSeatGroup, db_ticket_bundle: DbTicketBundle
) -> None:
    """Raise an error if the seat group's and the ticket bundle's
    categories don't match.
    """
    if db_seat_group.ticket_category_id != db_ticket_bundle.ticket_category_id:
        raise ValueError('Seat and ticket categories do not match.')


def _ensure_quantities_match(
    db_seat_group: DbSeatGroup, db_ticket_bundle: DbTicketBundle
) -> None:
    """Raise an error if the seat group's and the ticket bundle's
    quantities don't match.
    """
    if db_seat_group.seat_quantity != db_ticket_bundle.ticket_quantity:
        raise ValueError('Seat and ticket quantities do not match.')


def _ensure_actual_quantities_match(
    db_seats: Sequence[DbSeat], db_tickets: Sequence[DbTicket]
) -> None:
    """Raise an error if the totals of seats and tickets don't match."""
    if len(db_seats) != len(db_tickets):
        raise ValueError(
            'The actual quantities of seats and tickets ' 'do not match.'
        )


def _occupy_seats(
    db_seats: Sequence[DbSeat], db_tickets: Sequence[DbTicket]
) -> None:
    """Occupy all seats in the group with all tickets from the bundle."""
    db_seats = _sort_seats(db_seats)
    db_tickets = _sort_tickets(db_tickets)

    for seat, ticket in zip(db_seats, db_tickets):
        ticket.occupied_seat = seat


def _sort_seats(db_seats: Sequence[DbSeat]) -> list[DbSeat]:
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(db_seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(db_tickets: Sequence[DbTicket]) -> list[DbTicket]:
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(db_tickets, key=lambda t: t.created_at))


def release_seat_group(seat_group_id: SeatGroupID) -> None:
    """Release a seat group so it becomes available again."""
    db_occupancy = find_occupancy_for_seat_group(seat_group_id)
    if db_occupancy is None:
        raise ValueError('Seat group is not occupied.')

    for db_ticket in db_occupancy.ticket_bundle.tickets:
        db_ticket.occupied_seat = None

    db.session.delete(db_occupancy)

    db.session.commit()


def count_seat_groups_for_party(party_id: PartyID) -> int:
    """Return the number of seat groups for that party."""
    return db.session.scalar(
        select(db.func.count(DbSeatGroup.id)).filter_by(party_id=party_id)
    )


def find_seat_group(seat_group_id: SeatGroupID) -> Optional[DbSeatGroup]:
    """Return the seat group with that id, or `None` if not found."""
    return db.session.get(DbSeatGroup, seat_group_id)


def find_seat_group_occupied_by_ticket_bundle(
    ticket_bundle_id: TicketBundleID,
) -> Optional[SeatGroupID]:
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
) -> Optional[DbSeatGroupOccupancy]:
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
    return db.session.scalar(
        select(
            select(DbSeatGroupAssignment).filter_by(seat_id=seat_id).exists()
        )
    )

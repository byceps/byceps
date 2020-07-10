"""
byceps.services.seating.seat_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import PartyID

from ..ticketing.models.ticket import Ticket as DbTicket
from ..ticketing.models.ticket_bundle import TicketBundle as DbTicketBundle
from ..ticketing.transfer.models import TicketCategoryID

from .models.seat import Seat as DbSeat
from .models.seat_group import (
    Occupancy as DbSeatGroupOccupancy,
    SeatGroup as DbSeatGroup,
    SeatGroupAssignment as DbSeatGroupAssignment,
)
from .transfer.models import SeatGroupID


def create_seat_group(
    party_id: PartyID,
    ticket_category_id: TicketCategoryID,
    title: str,
    seats: Sequence[DbSeat],
    *,
    commit: bool=True,
) -> DbSeatGroup:
    """Create a seat group and assign the given seats."""
    seat_quantity = len(seats)
    if seat_quantity == 0:
        raise ValueError("No seats specified.")

    ticket_category_ids = {seat.category_id for seat in seats}
    if len(ticket_category_ids) != 1 \
            or (ticket_category_id not in ticket_category_ids):
        raise ValueError("Seats' ticket category IDs do not match the group's.")

    group = DbSeatGroup(party_id, ticket_category_id, seat_quantity, title)
    db.session.add(group)

    for seat in seats:
        assignment = DbSeatGroupAssignment(group, seat)
        db.session.add(assignment)

    if commit:
        db.session.commit()

    return group


def occupy_seat_group(
    seat_group: DbSeatGroup, ticket_bundle: DbTicketBundle
) -> DbSeatGroupOccupancy:
    """Occupy the seat group with that ticket bundle."""
    seats = seat_group.seats
    tickets = ticket_bundle.tickets

    _ensure_group_is_available(seat_group)
    _ensure_categories_match(seat_group, ticket_bundle)
    _ensure_quantities_match(seat_group, ticket_bundle)
    _ensure_actual_quantities_match(seats, tickets)

    occupancy = DbSeatGroupOccupancy(seat_group.id, ticket_bundle.id)
    db.session.add(occupancy)

    _occupy_seats(seats, tickets)

    db.session.commit()

    return occupancy


def switch_seat_group(
    occupancy: DbSeatGroupOccupancy, to_group: DbSeatGroup
) -> None:
    """Switch ticket bundle to another seat group."""
    ticket_bundle = occupancy.ticket_bundle
    tickets = ticket_bundle.tickets
    seats = to_group.seats

    _ensure_group_is_available(to_group)
    _ensure_categories_match(to_group, ticket_bundle)
    _ensure_quantities_match(to_group, ticket_bundle)
    _ensure_actual_quantities_match(seats, tickets)

    occupancy.seat_group_id = to_group.id

    _occupy_seats(seats, tickets)

    db.session.commit()


def _ensure_group_is_available(seat_group: DbSeatGroup) -> None:
    """Raise an error if the seat group is occupied."""
    if seat_group.is_occupied():
        raise ValueError('Seat group is already occupied.')


def _ensure_categories_match(
    seat_group: DbSeatGroup, ticket_bundle: DbTicketBundle
) -> None:
    """Raise an error if the seat group's and the ticket bundle's
    categories don't match.
    """
    if seat_group.ticket_category_id != ticket_bundle.ticket_category_id:
        raise ValueError('Seat and ticket categories do not match.')


def _ensure_quantities_match(
    seat_group: DbSeatGroup, ticket_bundle: DbTicketBundle
) -> None:
    """Raise an error if the seat group's and the ticket bundle's
    quantities don't match.
    """
    if seat_group.seat_quantity != ticket_bundle.ticket_quantity:
        raise ValueError('Seat and ticket quantities do not match.')


def _ensure_actual_quantities_match(
    seats: Sequence[DbSeat], tickets: Sequence[DbTicket]
) -> None:
    """Raise an error if the totals of seats and tickets don't match."""
    if len(seats) != len(tickets):
        raise ValueError(
            'The actual quantities of seats and tickets ' 'do not match.'
        )


def _occupy_seats(seats: Sequence[DbSeat], tickets: Sequence[DbTicket]) -> None:
    """Occupy all seats in the group with all tickets from the bundle."""
    seats = _sort_seats(seats)
    tickets = _sort_tickets(tickets)

    for seat, ticket in zip(seats, tickets):
        ticket.occupied_seat = seat


def _sort_seats(seats: Sequence[DbSeat]) -> Sequence[DbSeat]:
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(tickets: Sequence[DbTicket]) -> Sequence[DbTicket]:
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(tickets, key=lambda t: t.created_at))


def release_seat_group(seat_group: DbSeatGroup) -> None:
    """Release a seat group so it becomes available again."""
    if not seat_group.is_occupied():
        raise ValueError('Seat group is not occupied.')

    for ticket in seat_group.occupancy.ticket_bundle.tickets:
        ticket.occupied_seat = None

    db.session.delete(seat_group.occupancy)

    db.session.commit()


def count_seat_groups_for_party(party_id: PartyID) -> int:
    """Return the number of seat groups for that party."""
    return DbSeatGroup.query \
        .filter_by(party_id=party_id) \
        .count()


def find_seat_group(seat_group_id: SeatGroupID) -> Optional[DbSeatGroup]:
    """Return the seat group with that id, or `None` if not found."""
    return DbSeatGroup.query.get(seat_group_id)


def get_all_seat_groups_for_party(party_id: PartyID) -> Sequence[DbSeatGroup]:
    """Return all seat groups for that party."""
    return DbSeatGroup.query \
        .filter_by(party_id=party_id) \
        .all()

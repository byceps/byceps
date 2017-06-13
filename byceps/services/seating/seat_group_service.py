"""
byceps.services.seating.seat_group_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Sequence

from ...database import db
from ...typing import PartyID

from ..ticketing.models.ticket import Ticket
from ..ticketing.models.ticket_bundle import TicketBundle

from .models.category import Category
from .models.seat import Seat
from .models.seat_group import Occupancy as SeatGroupOccupancy, SeatGroup, \
    SeatGroupAssignment


def create_seat_group(party_id: PartyID, seat_category: Category, title: str,
                      seats: Sequence[Seat]) -> SeatGroup:
    """Create a seat group and assign the given seats."""
    seat_quantity = len(seats)
    if seat_quantity == 0:
        raise ValueError("No seats specified.")

    seats_categories = {seat.category for seat in seats}
    if len(seats_categories) != 1 or (seat_category not in seats_categories):
        raise ValueError("Seats' category IDs do not match the group's.")

    group = SeatGroup(party_id, seat_category, seat_quantity, title)
    db.session.add(group)

    for seat in seats:
        assignment = SeatGroupAssignment(group, seat)
        db.session.add(assignment)

    db.session.commit()

    return group


def occupy_seat_group(seat_group: SeatGroup, ticket_bundle: TicketBundle
                     ) -> SeatGroupOccupancy:
    """Occupy the seat group with that ticket bundle."""
    seats = seat_group.seats
    tickets = ticket_bundle.tickets

    _ensure_group_is_available(seat_group)
    _ensure_categories_match(seat_group, ticket_bundle)
    _ensure_quantities_match(seat_group, ticket_bundle)
    _ensure_actual_quantities_match(seats, tickets)

    occupancy = SeatGroupOccupancy(seat_group.id, ticket_bundle.id)
    db.session.add(occupancy)

    _occupy_seats(seats, tickets)

    db.session.commit()

    return occupancy


def switch_seat_group(occupancy: SeatGroupOccupancy, to_group: SeatGroup
                     ) -> None:
    """Switch ticket bundle to another seat group."""
    ticket_bundle = occupancy.ticket_bundle
    tickets = ticket_bundle.tickets
    seats = to_group.seats

    _ensure_group_is_available(to_group)
    _ensure_categories_match(to_group, ticket_bundle)
    _ensure_quantities_match(to_group, ticket_bundle)
    _ensure_actual_quantities_match(seats, tickets)

    occupancy.seat_group.id = to_group.id

    _occupy_seats(seats, tickets)

    db.session.commit()


def _ensure_group_is_available(seat_group: SeatGroup) -> None:
    """Raise an error if the seat group is occupied."""
    if seat_group.is_occupied():
        raise ValueError('Seat group is already occupied.')


def _ensure_categories_match(seat_group: SeatGroup, ticket_bundle: TicketBundle
                            ) -> None:
    """Raise an error if the seat group's and the ticket bundle's
    categories don't match.
    """
    if seat_group.seat_category_id != ticket_bundle.ticket_category_id:
        raise ValueError('Seat and ticket categories do not match.')


def _ensure_quantities_match(seat_group: SeatGroup, ticket_bundle: TicketBundle
                            ) -> None:
    """Raise an error if the seat group's and the ticket bundle's
    quantities don't match.
    """
    if seat_group.seat_quantity != ticket_bundle.ticket_quantity:
        raise ValueError('Seat and ticket quantities do not match.')


def _ensure_actual_quantities_match(seats: Sequence[Seat],
                                    tickets: Sequence[Ticket]) -> None:
    """Raise an error if the totals of seats and tickets don't match."""
    if len(seats) != len(tickets):
        raise ValueError('The actual quantities of seats and tickets '
                         'do not match.')


def _occupy_seats(seats: Sequence[Seat], tickets: Sequence[Ticket]) -> None:
    """Occupy all seats in the group with all tickets from the bundle."""
    seats = _sort_seats(seats)
    tickets = _sort_tickets(tickets)

    for seat, ticket in zip(seats, tickets):
        ticket.occupied_seat = seat


def _sort_seats(seats: Sequence[Seat]) -> Sequence[Seat]:
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(tickets: Sequence[Ticket]) -> Sequence[Ticket]:
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(tickets, key=lambda t: t.created_at))


def release_seat_group(seat_group: SeatGroup) -> None:
    """Release a seat group so it becomes available again."""
    if not seat_group.is_occupied():
        raise ValueError('Seat group is not occupied.')

    for ticket in seat_group.occupancy.ticket_bundle.tickets:
        ticket.occupied_seat = None

    db.session.delete(seat_group.occupancy)

    db.session.commit()


def count_seat_groups_for_party(party_id: PartyID) -> int:
    """Return the number of seat groups for that party."""
    return SeatGroup.query \
        .filter_by(party_id=party_id) \
        .count()


def get_all_seat_groups_for_party(party_id: PartyID) -> Sequence[SeatGroup]:
    """Return all seat groups for that party."""
    return SeatGroup.query \
        .filter_by(party_id=party_id) \
        .all()

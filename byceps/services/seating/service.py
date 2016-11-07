# -*- coding: utf-8 -*-

"""
byceps.services.seating.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.area import Area
from .models.category import Category
from .models.seat import Seat
from .models.seat_group import Occupancy as SeatGroupOccupancy, SeatGroup, \
    SeatGroupAssignment


# -------------------------------------------------------------------- #
# areas


def create_area(party_id, slug, title):
    """Create an area."""
    area = Area(party_id, slug, title)

    db.session.add(area)
    db.session.commit()

    return area


def count_areas_for_party(party_id):
    """Return the number of seating areas for that party."""
    return Area.query \
        .for_party_id(party_id) \
        .count()


def find_area_for_party_by_slug(party_id, slug):
    """Return the area for that party with that slug, or `None` if not found."""
    return Area.query \
        .for_party_id(party_id) \
        .filter_by(slug=slug) \
        .options(db.joinedload('seats').joinedload('category')) \
        .first()


def get_areas_for_party(party_id):
    """Return all areas for that party."""
    return Area.query \
        .for_party_id(party_id) \
        .all()


def get_areas_for_party_paginated(party_id, page, per_page):
    """Return the areas for that party to show on the specified page."""
    return Area.query \
        .for_party_id(party_id) \
        .order_by(Area.title) \
        .paginate(page, per_page)


# -------------------------------------------------------------------- #
# categories


def create_category(party_id, title):
    """Create a category."""
    category = Category(party_id, title)

    db.session.add(category)
    db.session.commit()

    return category


def count_categories_for_party(party_id):
    """Return the number of categories for that party."""
    return Category.query \
        .for_party_id(party_id) \
        .count()


def get_categories_for_party(party_id):
    """Return all categories for that party."""
    return Category.query \
        .for_party_id(party_id) \
        .all()


# -------------------------------------------------------------------- #
# seats


def create_seat(area, coord_x, coord_y, category):
    """Create a seat."""
    seat = Seat(area, category, coord_x=coord_x, coord_y=coord_y)

    db.session.add(seat)
    db.session.commit()

    return seat


def count_seats_for_party(party_id):
    """Return the number of seats in seating areas for that party."""
    return Seat.query \
        .join(Area).filter(Area.party_id == party_id) \
        .count()


def get_seat_total_per_area(party_id):
    """Return the number of seats per area for that party."""
    return dict(db.session \
        .query(
            Area.id,
            db.func.count(Seat.id)
        ) \
        .filter_by(party_id=party_id) \
        .join(Seat) \
        .group_by(Area.id) \
        .all())


# -------------------------------------------------------------------- #
# seat groups


def create_seat_group(party_id, seat_category, seat_quantity, title, seats):
    """Create a seat group and assign the given seats."""
    if len(seats) != seat_quantity:
        raise ValueError("Number of seats to assign does not match "
                         "the group's seat quantity.")

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


def occupy_seat_group(seat_group, ticket_bundle):
    """Occupy the seat group with that ticket bundle."""
    if seat_group.is_occupied():
        raise ValueError('Seat group is already occupied.')

    if seat_group.seat_category_id != ticket_bundle.ticket_category_id:
        raise ValueError('Seat and ticket categories do not match.')

    if seat_group.seat_quantity != ticket_bundle.ticket_quantity:
        raise ValueError('Seat and ticket quantities do not match.')

    seats = seat_group.seats
    tickets = ticket_bundle.tickets

    if len(seats) != len(tickets):
        raise ValueError('The actual quantities of seats and tickets '
                         'do not match.')

    occupancy = SeatGroupOccupancy(seat_group.id, ticket_bundle.id)
    db.session.add(occupancy)

    _occupy_seats(seats, tickets)

    db.session.commit()

    return occupancy


def switch_seat_group(occupancy, to_group):
    """Switch ticket bundle to another seat group."""
    occupancy.seat_group.id = to_group.id

    _occupy_seats(to_group.seats, occupancy.ticket_bundle.tickets)

    db.session.commit()


def _occupy_seats(seats, tickets):
    """Occupy all seats in the group with all tickets from the bundle."""
    seats = _sort_seats(seats)
    tickets = _sort_tickets(tickets)

    for seat, ticket in zip(seats, tickets):
        ticket.occupied_seat = seat


def _sort_seats(seats):
    """Create a list of the seats sorted by their respective coordinates."""
    return list(sorted(seats, key=lambda s: (s.coord_x, s.coord_y)))


def _sort_tickets(tickets):
    """Create a list of the tickets sorted by creation time (ascending)."""
    return list(sorted(tickets, key=lambda t: t.created_at))


def release_seat_group(seat_group):
    """Release a seat group so it becomes available again."""
    if not seat_group.is_occupied():
        raise ValueError('Seat group is not occupied.')

    for ticket in seat_group.occupancy.ticket_bundle.tickets:
        ticket.occupied_seat = None

    db.session.delete(seat_group.occupancy)

    db.session.commit()


def count_seat_groups_for_party(party_id):
    """Return the number of seat groups for that party."""
    return SeatGroup.query \
        .filter_by(party_id=party_id) \
        .count()


def get_all_seat_groups_for_party(party_id):
    """Return all seat groups for that party."""
    return SeatGroup.query \
        .filter_by(party_id=party_id) \
        .all()

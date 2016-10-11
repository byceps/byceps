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
from .models.seat_group import SeatGroup, SeatGroupAssignment


# -------------------------------------------------------------------- #
# areas


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


def get_categories_for_party(party_id):
    """Return all categories for that party."""
    return Category.query \
        .for_party_id(party_id) \
        .all()


# -------------------------------------------------------------------- #
# seats


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


def create_seat_group(party_id, title, seat_ids):
    """Create a seat group and assign the given seats."""
    group = SeatGroup(party_id, title)
    db.session.add(group)
    db.session.commit()

    for seat_id in seat_ids:
        assignment = SeatGroupAssignment(group.id, seat_id)
        db.session.add(assignment)
    db.session.commit()

    return group


def get_all_seat_groups_for_party(party_id):
    """Return all seat groups for that party."""
    return SeatGroup.query \
        .filter_by(party_id=party_id) \
        .all()

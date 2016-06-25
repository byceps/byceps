# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..seating.models.area import Area
from ..seating.models.seat import Seat


def get_seat_total_per_area(party):
    """Return the number of seats per area for this party."""
    areas = Area.query.for_party(party).all()

    return dict(db.session \
        .query(
            Area.id,
            db.func.count(Seat.id)
        ) \
        .filter_by(party_id=party.id) \
        .join(Seat) \
        .group_by(Area.id) \
        .all())


def count_areas_for_party(party):
    """Return the number of seating areas for that party."""
    return Area.query.for_party(party).count()


def count_seats_for_party(party):
    """Return the number of seats in seating areas for that party."""
    return Seat.query \
        .join(Area).filter(Area.party_id == party.id) \
        .count()

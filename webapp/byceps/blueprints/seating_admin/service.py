# -*- coding: utf-8 -*-

"""
byceps.blueprints.seating_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..party.models import Party
from ..seating.models import Area, Seat


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

"""
byceps.services.seating.seat_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict

from ...database import db
from ...typing import PartyID

from .models.area import Area, AreaID
from .models.category import Category
from .models.seat import Seat


def create_seat(area: Area, coord_x: int, coord_y: int, category: Category
               ) -> Seat:
    """Create a seat."""
    seat = Seat(area, category, coord_x=coord_x, coord_y=coord_y)

    db.session.add(seat)
    db.session.commit()

    return seat


def count_seats_for_party(party_id: PartyID) -> int:
    """Return the number of seats in seating areas for that party."""
    return Seat.query \
        .join(Area).filter(Area.party_id == party_id) \
        .count()


def get_seat_total_per_area(party_id: PartyID) -> Dict[AreaID, int]:
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

"""
byceps.services.seating.area_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ...database import db, Pagination
from ...typing import PartyID

from ..ticketing.models.ticket import Ticket as DbTicket

from .models.area import Area as DbArea
from .models.seat import Seat as DbSeat


def create_area(party_id: PartyID, slug: str, title: str) -> DbArea:
    """Create an area."""
    area = DbArea(party_id, slug, title)

    db.session.add(area)
    db.session.commit()

    return area


def count_areas_for_party(party_id: PartyID) -> int:
    """Return the number of seating areas for that party."""
    return DbArea.query \
        .for_party(party_id) \
        .count()


def find_area_for_party_by_slug(
    party_id: PartyID, slug: str
) -> Optional[DbArea]:
    """Return the area for that party with that slug, or `None` if not found."""
    return DbArea.query \
        .for_party(party_id) \
        .filter_by(slug=slug) \
        .first()


def get_areas_for_party(party_id: PartyID) -> DbArea:
    """Return all areas for that party."""
    return DbArea.query \
        .for_party(party_id) \
        .all()


def get_areas_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the areas for that party."""
    area = db.aliased(DbArea)

    subquery = db.session \
        .query(
            db.func.count(DbTicket.id)
        ) \
        .filter(DbTicket.revoked == False) \
        .filter(DbTicket.occupied_seat_id != None) \
        .join(DbSeat) \
        .filter(DbSeat.area_id == area.id) \
        .subquery() \
        .as_scalar()

    return db.session \
        .query(
            area,
            subquery
        ) \
        .filter(area.party_id == party_id) \
        .group_by(area.id) \
        .paginate()

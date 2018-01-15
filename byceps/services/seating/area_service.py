"""
byceps.services.seating.area_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import PartyID

from .models.area import Area


def create_area(party_id: PartyID, slug: str, title: str) -> Area:
    """Create an area."""
    area = Area(party_id, slug, title)

    db.session.add(area)
    db.session.commit()

    return area


def count_areas_for_party(party_id: PartyID) -> int:
    """Return the number of seating areas for that party."""
    return Area.query \
        .for_party_id(party_id) \
        .count()


def find_area_for_party_by_slug(party_id: PartyID, slug: str) -> Optional[Area]:
    """Return the area for that party with that slug, or `None` if not found."""
    return Area.query \
        .for_party_id(party_id) \
        .filter_by(slug=slug) \
        .first()


def get_areas_for_party(party_id: PartyID) -> Area:
    """Return all areas for that party."""
    return Area.query \
        .for_party_id(party_id) \
        .all()


def get_areas_for_party_paginated(party_id: PartyID, page: int, per_page: int
                                 ) -> Pagination:
    """Return the areas for that party to show on the specified page."""
    return Area.query \
        .for_party_id(party_id) \
        .order_by(Area.title) \
        .paginate(page, per_page)

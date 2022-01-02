"""
byceps.services.seating.area_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from ...database import db, paginate, Pagination
from ...typing import PartyID

from ..ticketing.dbmodels.ticket import Ticket as DbTicket

from .dbmodels.area import Area as DbArea
from .dbmodels.seat import Seat as DbSeat
from .transfer.models import Area


def create_area(party_id: PartyID, slug: str, title: str) -> Area:
    """Create an area."""
    area = DbArea(party_id, slug, title)

    db.session.add(area)
    db.session.commit()

    return _db_entity_to_area(area)


def delete_area(area_id: str) -> None:
    """Delete an area."""
    db.session.query(DbArea) \
        .filter_by(id=area_id) \
        .delete()
    db.session.commit()


def count_areas_for_party(party_id: PartyID) -> int:
    """Return the number of seating areas for that party."""
    return db.session \
        .query(DbArea) \
        .filter_by(party_id=party_id) \
        .count()


def find_area_for_party_by_slug(party_id: PartyID, slug: str) -> Optional[Area]:
    """Return the area for that party with that slug, or `None` if not found."""
    area = db.session \
        .query(DbArea) \
        .filter_by(party_id=party_id) \
        .filter_by(slug=slug) \
        .first()

    if area is None:
        return None

    return _db_entity_to_area(area)


def get_areas_for_party(party_id: PartyID) -> list[Area]:
    """Return all areas for that party."""
    areas = db.session \
        .query(DbArea) \
        .filter_by(party_id=party_id) \
        .all()

    return [_db_entity_to_area(area) for area in areas]


def get_areas_for_party_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return the areas for that party."""
    area = db.aliased(DbArea)

    subquery = select(db.func.count(DbTicket.id)) \
        .filter(DbTicket.revoked == False) \
        .filter(DbTicket.occupied_seat_id != None) \
        .join(DbSeat) \
        .filter(DbSeat.area_id == area.id) \
        .scalar_subquery()

    items_query = select(area, subquery) \
        .filter(area.party_id == party_id) \
        .group_by(area.id)

    count_query = select(db.func.count(DbArea.id)) \
        .filter(area.party_id == party_id)

    def item_mapper(
        area_and_ticket_count: tuple[DbArea, int]
    ) -> tuple[Area, int]:
        area, ticket_count = area_and_ticket_count
        return _db_entity_to_area(area), ticket_count

    return paginate(
        items_query, count_query, page, per_page, item_mapper=item_mapper
    )


def _db_entity_to_area(area: DbArea) -> Area:
    return Area(
        id=area.id,
        party_id=area.party_id,
        slug=area.slug,
        title=area.title,
        image_filename=area.image_filename,
        image_width=area.image_width,
        image_height=area.image_height,
    )

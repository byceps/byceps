"""
byceps.services.seating.area_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from sqlalchemy import select
from sqlalchemy.sql import Select

from ...database import db, paginate, Pagination
from ...typing import PartyID

from ..ticketing.dbmodels.ticket import DbTicket

from .dbmodels.area import DbArea
from .dbmodels.seat import DbSeat
from .transfer.models import Area, SeatUtilization


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


def get_areas_with_seat_utilization(
    party_id: PartyID,
) -> list[Area, SeatUtilization]:
    """Return all areas and their seat utilization for that party."""
    query = _get_areas_with_seat_utilization_query(party_id)
    rows = db.session.execute(query).all()
    return [_map_areas_with_seat_utilization_row(row) for row in rows]


def get_areas_with_seat_utilization_paginated(
    party_id: PartyID, page: int, per_page: int
) -> Pagination:
    """Return areas and their seat utilization for that party, paginated."""
    items_query = _get_areas_with_seat_utilization_query(party_id)

    count_query = select(db.func.count(DbArea.id)) \
        .filter(DbArea.party_id == party_id)

    return paginate(
        items_query,
        count_query,
        page,
        per_page,
        item_mapper=_map_areas_with_seat_utilization_row,
    )


def _get_areas_with_seat_utilization_query(party_id: PartyID) -> Select:
    area = db.aliased(DbArea)

    subquery_occupied_seat_count = select(db.func.count(DbTicket.id)) \
        .filter(DbTicket.revoked == False) \
        .filter(DbTicket.occupied_seat_id.is_not(None)) \
        .join(DbSeat) \
        .filter(DbSeat.area_id == area.id) \
        .scalar_subquery()

    subquery_total_seat_count = select(db.func.count(DbSeat.id)) \
        .filter_by(area_id=area.id) \
        .scalar_subquery()

    return select(
            area,
            subquery_occupied_seat_count,
            subquery_total_seat_count,
        ) \
        .filter(area.party_id == party_id) \
        .group_by(area.id)


def _map_areas_with_seat_utilization_row(
    row: tuple[DbArea, int, int]
) -> tuple[Area, SeatUtilization]:
    area, occupied_seat_count, total_seat_count = row
    utilization = SeatUtilization(
        occupied=occupied_seat_count, total=total_seat_count
    )
    return _db_entity_to_area(area), utilization


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

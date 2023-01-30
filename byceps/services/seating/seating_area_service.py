"""
byceps.services.seating.seating_area_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from sqlalchemy import delete, select

from ...database import db
from ...typing import PartyID

from ..ticketing.dbmodels.ticket import DbTicket

from .dbmodels.area import DbSeatingArea
from .dbmodels.seat import DbSeat
from .models import SeatingArea, SeatingAreaID, SeatUtilization


def create_area(
    party_id: PartyID,
    slug: str,
    title: str,
    *,
    image_filename: Optional[str] = None,
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
) -> SeatingArea:
    """Create an area."""
    db_area = DbSeatingArea(
        party_id,
        slug,
        title,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
    )

    db.session.add(db_area)
    db.session.commit()

    return _db_entity_to_area(db_area)


def delete_area(area_id: SeatingAreaID) -> None:
    """Delete an area."""
    db.session.execute(delete(DbSeatingArea).filter_by(id=area_id))
    db.session.commit()


def count_areas_for_party(party_id: PartyID) -> int:
    """Return the number of seating areas for that party."""
    return db.session.scalar(
        select(db.func.count(DbSeatingArea.id)).filter_by(party_id=party_id)
    )


def find_area(area_id: SeatingAreaID) -> Optional[SeatingArea]:
    """Return the area, or `None` if not found."""
    db_area = db.session.get(DbSeatingArea, area_id)

    if db_area is None:
        return None

    return _db_entity_to_area(db_area)


def find_area_for_party_by_slug(
    party_id: PartyID, slug: str
) -> Optional[SeatingArea]:
    """Return the area for that party with that slug, or `None` if not found."""
    db_area = db.session.scalars(
        select(DbSeatingArea).filter_by(party_id=party_id).filter_by(slug=slug)
    ).first()

    if db_area is None:
        return None

    return _db_entity_to_area(db_area)


def get_areas_with_seat_utilization(
    party_id: PartyID,
) -> list[tuple[SeatingArea, SeatUtilization]]:
    """Return all areas and their seat utilization for that party."""
    area = db.aliased(DbSeatingArea)

    subquery_occupied_seat_count = (
        select(db.func.count(DbTicket.id))
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(DbTicket.occupied_seat_id.is_not(None))
        .join(DbSeat)
        .filter(DbSeat.area_id == area.id)
        .scalar_subquery()
    )

    subquery_total_seat_count = (
        select(db.func.count(DbSeat.id))
        .filter_by(area_id=area.id)
        .scalar_subquery()
    )

    rows = db.session.execute(
        select(
            area,
            subquery_occupied_seat_count,
            subquery_total_seat_count,
        )
        .filter(area.party_id == party_id)
        .group_by(area.id)
        .order_by(area.title)
    ).all()

    return [
        (
            _db_entity_to_area(db_area),
            SeatUtilization(
                occupied=occupied_seat_count, total=total_seat_count
            ),
        )
        for db_area, occupied_seat_count, total_seat_count in rows
    ]


def _db_entity_to_area(db_area: DbSeatingArea) -> SeatingArea:
    return SeatingArea(
        id=db_area.id,
        party_id=db_area.party_id,
        slug=db_area.slug,
        title=db_area.title,
        image_filename=db_area.image_filename,
        image_width=db_area.image_width,
        image_height=db_area.image_height,
    )

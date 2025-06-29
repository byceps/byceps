"""
byceps.services.seating.seating_area_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.ticket import DbTicket

from .dbmodels.area import DbSeatingArea
from .dbmodels.seat import DbSeat
from .models import SeatingArea, SeatingAreaID, SeatUtilization


def create_area(area: SeatingArea) -> None:
    """Create an area."""
    db_area = DbSeatingArea(
        area.id,
        area.party_id,
        area.slug,
        area.title,
        image_filename=area.image_filename,
        image_width=area.image_width,
        image_height=area.image_height,
    )

    db.session.add(db_area)
    db.session.commit()


def update_area(area: SeatingArea) -> None:
    """Update an area."""
    db_area = find_area(area.id)
    if db_area is None:
        raise ValueError(f'Unknown seating area ID "{area_id}"')

    db_area.slug = area.slug
    db_area.title = area.title
    db_area.image_filename = area.image_filename
    db_area.image_width = area.image_width
    db_area.image_height = area.image_height

    db.session.commit()


def delete_area(area_id: SeatingAreaID) -> None:
    """Delete an area."""
    db.session.execute(delete(DbSeatingArea).filter_by(id=area_id))
    db.session.commit()


def find_area(area_id: SeatingAreaID) -> DbSeatingArea | None:
    """Return the area, or `None` if not found."""
    return db.session.get(DbSeatingArea, area_id)


def find_area_for_party_by_slug(
    party_id: PartyID, slug: str
) -> DbSeatingArea | None:
    """Return the area for that party with that slug, or `None` if not found."""
    return db.session.scalars(
        select(DbSeatingArea).filter_by(party_id=party_id).filter_by(slug=slug)
    ).first()


def get_areas_for_party(party_id: PartyID) -> Sequence[DbSeatingArea]:
    """Return all areas for that party."""
    return db.session.scalars(
        select(DbSeatingArea).filter_by(party_id=party_id)
    ).all()


def get_areas_with_utilization(
    party_id: PartyID,
) -> list[tuple[DbSeatingArea, SeatUtilization]]:
    """Return all areas and their utilization for that party."""
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
            db_area,
            SeatUtilization(
                occupied=occupied_seat_count, total=total_seat_count
            ),
        )
        for db_area, occupied_seat_count, total_seat_count in rows
    ]


def count_areas_for_party(party_id: PartyID) -> int:
    """Return the number of seating areas for that party."""
    return (
        db.session.scalar(
            select(db.func.count(DbSeatingArea.id)).filter_by(party_id=party_id)
        )
        or 0
    )

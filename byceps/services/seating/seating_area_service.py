"""
byceps.services.seating.seating_area_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.party.models import PartyID

from . import seating_area_domain_service, seating_area_repository
from .dbmodels.area import DbSeatingArea
from .models import SeatingArea, SeatingAreaID, SeatUtilization


def create_area(
    party_id: PartyID,
    slug: str,
    title: str,
    *,
    image_filename: str | None = None,
    image_width: int | None = None,
    image_height: int | None = None,
) -> SeatingArea:
    """Create an area."""
    area = seating_area_domain_service.create_area(
        party_id,
        slug,
        title,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
    )

    seating_area_repository.create_area(area)

    return area


def update_area(
    area: SeatingArea,
    slug: str,
    title: str,
    image_filename: str | None,
    image_width: int | None,
    image_height: int | None,
) -> SeatingArea:
    """Update an area."""
    updated_area = seating_area_domain_service.update_area(
        area, slug, title, image_filename, image_width, image_height
    )

    seating_area_repository.update_area(updated_area)

    return updated_area


def delete_area(area_id: SeatingAreaID) -> None:
    """Delete an area."""
    seating_area_repository.delete_area(area_id)


def find_area(area_id: SeatingAreaID) -> SeatingArea | None:
    """Return the area, or `None` if not found."""
    db_area = seating_area_repository.find_area(area_id)

    if db_area is None:
        return None

    return _db_entity_to_area(db_area)


def find_area_for_party_by_slug(
    party_id: PartyID, slug: str
) -> SeatingArea | None:
    """Return the area for that party with that slug, or `None` if not found."""
    db_area = seating_area_repository.find_area_for_party_by_slug(
        party_id, slug
    )

    if db_area is None:
        return None

    return _db_entity_to_area(db_area)


def get_areas_for_party(party_id: PartyID) -> list[SeatingArea]:
    """Return all areas for that party."""
    db_areas = seating_area_repository.get_areas_for_party(party_id)

    return [_db_entity_to_area(db_area) for db_area in db_areas]


def get_areas_with_seat_utilization(
    party_id: PartyID,
) -> list[tuple[SeatingArea, SeatUtilization]]:
    """Return all areas and their seat utilization for that party."""
    db_areas_with_seat_utilization = (
        seating_area_repository.get_areas_with_seat_utilization(party_id)
    )

    return [
        (_db_entity_to_area(db_area), seat_utilization)
        for db_area, seat_utilization in db_areas_with_seat_utilization
    ]


def count_areas_for_party(party_id: PartyID) -> int:
    """Return the number of seating areas for that party."""
    return seating_area_repository.count_areas_for_party(party_id)


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

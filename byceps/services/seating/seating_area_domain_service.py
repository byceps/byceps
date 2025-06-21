"""
byceps.services.seating.seating_area_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from byceps.services.party.models import PartyID
from byceps.util.uuid import generate_uuid4

from .models import SeatingArea, SeatingAreaID


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
    area_id = SeatingAreaID(generate_uuid4())

    return SeatingArea(
        id=area_id,
        party_id=party_id,
        slug=slug,
        title=title,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
    )


def update_area(
    area: SeatingArea,
    slug: str,
    title: str,
    image_filename: str | None,
    image_width: int | None,
    image_height: int | None,
) -> SeatingArea:
    """Update an area."""
    return dataclasses.replace(
        area,
        slug=slug,
        title=title,
        image_filename=image_filename,
        image_width=image_width,
        image_height=image_height,
    )

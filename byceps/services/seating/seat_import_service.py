"""
byceps.services.seating.seat_import_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import json
from io import TextIOBase
from typing import Iterator, Optional

from pydantic import BaseModel, ValidationError

from ...util.result import Err, Ok, Result

from ..ticketing.models.ticket import TicketCategoryID

from .models import Seat, SeatingAreaID
from . import seat_service


class SeatToImport(BaseModel):
    area_title: str
    coord_x: int
    coord_y: int
    rotation: Optional[int] = None
    category_title: str
    label: Optional[str] = None
    type_: Optional[str] = None


def parse_lines(lines: TextIOBase) -> Iterator[str]:
    """Read text line by line, removing trailing whitespace."""
    for line in lines:
        yield line.rstrip()


def parse_seat_json(json_data: str) -> Result[SeatToImport, str]:
    """Parse a JSON object into a seat import object."""
    try:
        data_dict = json.loads(json_data)
    except json.decoder.JSONDecodeError as e:
        return Err(str(e))

    try:
        seat_to_import = SeatToImport.parse_obj(data_dict)
        return Ok(seat_to_import)
    except ValidationError as e:
        return Err(str(e))


def import_seat(
    seat_to_import: SeatToImport,
    area_ids_by_title: dict[str, SeatingAreaID],
    category_ids_by_title: dict[str, TicketCategoryID],
) -> Result[Seat, str]:
    """Import a seat."""
    area_title = seat_to_import.area_title
    area_id = area_ids_by_title.get(area_title)
    if area_id is None:
        return Err(f'Unknown area title "{area_title}"')

    category_title = seat_to_import.category_title
    category_id = category_ids_by_title.get(category_title)
    if category_id is None:
        return Err(f'Unknown category title "{category_title}"')

    seat = seat_service.create_seat(
        area_id,
        seat_to_import.coord_x,
        seat_to_import.coord_y,
        category_id,
        rotation=seat_to_import.rotation,
        label=seat_to_import.label,
        type_=seat_to_import.type_,
    )
    return Ok(seat)

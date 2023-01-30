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
    for line in lines:
        yield line.strip()


def parse_seat_json(json_data: str) -> SeatToImport:
    data_dict = json.loads(json_data)

    try:
        return SeatToImport.parse_obj(data_dict)
    except ValidationError as e:
        raise Exception(str(e))


def import_seat(
    seat_to_import: SeatToImport,
    area_ids_by_title: dict[str, SeatingAreaID],
    category_ids_by_title: dict[str, TicketCategoryID],
) -> Seat:
    area_id = area_ids_by_title[seat_to_import.area_title]
    category_id = category_ids_by_title[seat_to_import.category_title]

    return seat_service.create_seat(
        area_id,
        seat_to_import.coord_x,
        seat_to_import.coord_y,
        category_id,
        rotation=seat_to_import.rotation,
        label=seat_to_import.label,
        type_=seat_to_import.type_,
    )

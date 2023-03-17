"""
byceps.services.seating.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType, Optional
from uuid import UUID

from pydantic import BaseModel

from ...typing import PartyID

from ..ticketing.models.ticket import TicketCategoryID


SeatingAreaID = NewType('SeatingAreaID', UUID)


@dataclass(frozen=True)
class SeatingArea:
    id: SeatingAreaID
    party_id: PartyID
    slug: str
    title: str
    image_filename: Optional[str]
    image_width: Optional[int]
    image_height: Optional[int]


SeatID = NewType('SeatID', UUID)


@dataclass(frozen=True)
class Seat:
    id: SeatID
    area_id: SeatingAreaID
    coord_x: int
    coord_y: int
    rotation: Optional[int]
    category_id: TicketCategoryID
    label: Optional[str]
    type_: Optional[str]


SeatGroupID = NewType('SeatGroupID', UUID)


@dataclass(frozen=True)
class SeatUtilization:
    occupied: int
    total: int


class SerializableSeatToImport(BaseModel):
    area_title: str
    coord_x: int
    coord_y: int
    category_title: str
    rotation: Optional[int] = None
    label: Optional[str] = None
    type_: Optional[str] = None
    group_title: Optional[str] = None


@dataclass(frozen=True)
class SeatToImport:
    area_id: SeatingAreaID
    coord_x: int
    coord_y: int
    category_id: TicketCategoryID
    rotation: Optional[int] = None
    label: Optional[str] = None
    type_: Optional[str] = None
    group_title: Optional[str] = None

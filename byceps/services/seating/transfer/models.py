"""
byceps.services.seating.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType, Optional
from uuid import UUID

from ....typing import PartyID

from ...ticketing.transfer.models import TicketCategoryID


AreaID = NewType('AreaID', UUID)


@dataclass(frozen=True)
class Area:
    id: AreaID
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
    coord_x: int
    coord_y: int
    category_id: TicketCategoryID
    label: Optional[str]
    type_: Optional[str]


SeatGroupID = NewType('SeatGroupID', UUID)


@dataclass(frozen=True)
class SeatUtilization:
    occupied: int
    total: int

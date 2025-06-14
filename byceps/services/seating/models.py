"""
byceps.services.seating.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from pydantic import BaseModel

from byceps.services.party.models import PartyID
from byceps.services.ticketing.models.ticket import TicketCategoryID


SeatingAreaID = NewType('SeatingAreaID', UUID)


@dataclass(frozen=True)
class SeatingArea:
    id: SeatingAreaID
    party_id: PartyID
    slug: str
    title: str
    image_filename: str | None
    image_width: int | None
    image_height: int | None


SeatID = NewType('SeatID', UUID)


@dataclass(frozen=True)
class Seat:
    id: SeatID
    area_id: SeatingAreaID
    coord_x: int
    coord_y: int
    rotation: int | None
    category_id: TicketCategoryID
    label: str | None
    type_: str | None


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
    rotation: int | None = None
    label: str | None = None
    type_: str | None = None
    group_title: str | None = None


@dataclass(frozen=True)
class SeatToImport:
    area_id: SeatingAreaID
    coord_x: int
    coord_y: int
    category_id: TicketCategoryID
    rotation: int | None = None
    label: str | None = None
    type_: str | None = None
    group_title: str | None = None


@dataclass(frozen=True)
class SeatReservationPrecondition:
    id: UUID
    party_id: PartyID
    minimum_ticket_quantity: int
    at_earliest: datetime

    def is_met(self, ticket_quantity: int, now: datetime) -> bool:
        return (
            ticket_quantity >= self.minimum_ticket_quantity
            and now >= self.at_earliest
        )

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
from byceps.services.ticketing.models.ticket import TicketCategoryID, TicketID


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
    occupied_by_ticket_id: TicketID | None


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
    at_earliest: datetime
    minimum_ticket_quantity: int

    def is_met(self, now: datetime, ticket_quantity: int) -> bool:
        return (
            now >= self.at_earliest
            and ticket_quantity >= self.minimum_ticket_quantity
        )

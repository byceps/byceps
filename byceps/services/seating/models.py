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
from byceps.services.ticketing.models.ticket import (
    TicketCategoryID,
    TicketCode,
    TicketID,
)
from byceps.services.user.models.user import User


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


# For assembling a visual seat plan without unused fields.
@dataclass(frozen=True, slots=True)
class AreaSeat:
    id: SeatID
    coord_x: int
    coord_y: int
    rotation: int | None
    label: str | None
    type_: str | None
    occupied_by_ticket_id: TicketID | None
    occupied_by_user: User | None

    @property
    def occupied(self) -> bool:
        return self.occupied_by_ticket_id is not None


SeatGroupID = NewType('SeatGroupID', UUID)


@dataclass(frozen=True)
class SeatGroup:
    id: SeatGroupID
    party_id: PartyID
    ticket_category_id: TicketCategoryID
    seat_quantity: int
    title: str
    seats: list[Seat]


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


@dataclass(frozen=True)
class ManagedTicket:
    id: TicketID
    code: TicketCode
    category_label: str
    occupies_seat: bool
    seat_label: str | None
    user: User | None

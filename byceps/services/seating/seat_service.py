"""
byceps.services.seating.seat_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.category import DbTicketCategory
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import (
    TicketCategory,
    TicketCategoryID,
)
from byceps.util.uuid import generate_uuid7

from . import seat_domain_service, seat_repository
from .dbmodels.area import DbSeatingArea
from .dbmodels.seat import DbSeat
from .models import Seat, SeatID, SeatingAreaID, SeatUtilization


def create_seat(
    area_id: SeatingAreaID,
    coord_x: int,
    coord_y: int,
    category_id: TicketCategoryID,
    *,
    rotation: int | None = None,
    label: str | None = None,
    type_: str | None = None,
) -> Seat:
    """Create a seat."""
    seat = seat_domain_service.create_seat(
        area_id,
        coord_x,
        coord_y,
        category_id,
        rotation=rotation,
        label=label,
        type_=type_,
    )

    seat_repository.create_seat(seat)

    return seat


def delete_seat(seat_id: SeatID) -> None:
    """Delete a seat."""
    seat_repository.delete_seat(seat_id)


def count_occupied_seats_by_category(
    party_id: PartyID,
) -> list[tuple[TicketCategory, int]]:
    """Count occupied seats for the party, grouped by ticket category."""
    return seat_repository.count_occupied_seats_by_category(party_id)


def count_occupied_seats_for_party(party_id: PartyID) -> int:
    """Count occupied seats for the party."""
    return seat_repository.count_occupied_seats_for_party(party_id)


def count_seats_for_party(party_id: PartyID) -> int:
    """Return the number of seats in seating areas for that party."""
    return seat_repository.count_seats_for_party(party_id)


def get_seat_utilization(party_id: PartyID) -> SeatUtilization:
    """Return how many seats of how many in total are occupied."""
    occupied_seat_count = count_occupied_seats_for_party(party_id)
    total_seat_count = count_seats_for_party(party_id)

    return SeatUtilization(occupied_seat_count, total_seat_count)


def aggregate_seat_utilizations(
    seat_utilizations: Iterable[SeatUtilization],
) -> SeatUtilization:
    """Aggregate multiple seat utilizations into one."""
    return seat_domain_service.aggregate_seat_utilizations(seat_utilizations)


def find_seat(seat_id: SeatID) -> Seat | None:
    """Return the seat with that id, or `None` if not found."""
    db_seat = seat_repository.find_seat(seat_id)

    if db_seat is None:
        return None

    return _db_entity_to_seat(db_seat)


def get_seat(seat_id: SeatID) -> Seat:
    """Return the seat with that id, or raise an exception."""
    db_seat = seat_repository.get_seat(seat_id)

    return _db_entity_to_seat(db_seat)


def get_seats(seat_ids: set[SeatID]) -> set[Seat]:
    """Return the seats with those IDs."""
    if not seat_ids:
        return set()

    db_seats = seat_repository.get_seats(seat_ids)

    return {_db_entity_to_seat(db_seat) for db_seat in db_seats}


def get_seats_with_tickets_for_area(
    area_id: SeatingAreaID,
) -> list[tuple[Seat, DbTicket | None]]:
    """Return the seats and their associated tickets (if available) for
    that area.
    """
    db_seats = seat_repository.get_seats_with_tickets_for_area(area_id)

    return [
        (_db_entity_to_seat(db_seat), db_seat.occupied_by_ticket)
        for db_seat in db_seats
    ]


def _db_entity_to_seat(db_seat: DbSeat) -> Seat:
    return Seat(
        id=db_seat.id,
        area_id=db_seat.area_id,
        coord_x=db_seat.coord_x,
        coord_y=db_seat.coord_y,
        rotation=db_seat.rotation,
        category_id=db_seat.category_id,
        label=db_seat.label,
        type_=db_seat.type_,
    )

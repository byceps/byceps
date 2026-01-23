"""
byceps.services.seating.seat_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable


from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import (
    TicketCategory,
    TicketCategoryID,
    TicketID,
)
from byceps.services.user import user_service
from byceps.services.user.models import User, UserID

from . import seat_domain_service, seat_repository
from .dbmodels.seat import DbSeat
from .models import AreaSeat, Seat, SeatID, SeatingAreaID, SeatUtilization


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
    occupied = count_occupied_seats_for_party(party_id)
    total = count_seats_for_party(party_id)

    return SeatUtilization(occupied=occupied, total=total)


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


def get_seats(seat_ids: set[SeatID]) -> list[Seat]:
    """Return the seats with those IDs."""
    if not seat_ids:
        return []

    db_seats = seat_repository.get_seats(seat_ids)

    return [_db_entity_to_seat(db_seat) for db_seat in db_seats]


def get_area_seats(area_id: SeatingAreaID) -> list[AreaSeat]:
    """Return the area's seats and their associated tickets (if
    available) to create a visual representation from.
    """
    db_seats = seat_repository.get_seats_with_tickets_for_area(area_id)

    seats_with_db_tickets = [
        (_db_entity_to_seat(db_seat), db_seat.occupied_by_ticket)
        for db_seat in db_seats
    ]

    db_tickets = [
        db_ticket
        for _, db_ticket in seats_with_db_tickets
        if db_ticket is not None
    ]
    user_ids = {
        db_ticket.used_by_id for db_ticket in db_tickets if db_ticket.used_by_id
    }
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return [
        _build_area_seat(seat, db_ticket, users_by_id)
        for seat, db_ticket in seats_with_db_tickets
    ]


def _build_area_seat(
    seat: Seat, db_ticket: DbTicket | None, users_by_id: dict[UserID, User]
) -> AreaSeat:
    ticket_id: TicketID | None = None
    user: User | None = None
    if db_ticket:
        ticket_id = db_ticket.id
        user_id = db_ticket.used_by_id
        if user_id:
            user = users_by_id[user_id]

    return AreaSeat(
        id=seat.id,
        coord_x=seat.coord_x,
        coord_y=seat.coord_y,
        rotation=seat.rotation,
        label=seat.label,
        type_=seat.type_,
        occupied_by_ticket_id=ticket_id,
        occupied_by_user=user,
    )


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
        occupied_by_ticket_id=db_seat.occupied_by_ticket.id
        if db_seat.occupied_by_ticket
        else None,
    )

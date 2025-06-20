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

from . import seat_domain_service
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

    db_seat = DbSeat(
        seat.id,
        seat.area_id,
        seat.category_id,
        coord_x=seat.coord_x,
        coord_y=seat.coord_y,
        rotation=seat.rotation,
        label=seat.label,
        type_=seat.type_,
    )

    db.session.add(db_seat)
    db.session.commit()

    return seat


def delete_seat(seat_id: SeatID) -> None:
    """Delete a seat."""
    db.session.execute(delete(DbSeat).filter_by(id=seat_id))
    db.session.commit()


def count_occupied_seats_by_category(
    party_id: PartyID,
) -> list[tuple[TicketCategory, int]]:
    """Count occupied seats for the party, grouped by ticket category."""
    subquery = (
        select(DbSeat.id, DbSeat.category_id)
        .join(DbTicket)
        .filter_by(revoked=False)
        .subquery()
    )

    rows = db.session.execute(
        select(
            DbTicketCategory.id,
            DbTicketCategory.party_id,
            DbTicketCategory.title,
            db.func.count(subquery.c.id),
        )
        .outerjoin(subquery, DbTicketCategory.id == subquery.c.category_id)
        .filter(DbTicketCategory.party_id == party_id)
        .group_by(DbTicketCategory.id)
        .order_by(DbTicketCategory.id)
    ).all()

    return [
        (
            TicketCategory(id=category_id, party_id=party_id, title=title),
            occupied_seat_count,
        )
        for category_id, party_id, title, occupied_seat_count in rows
    ]


def count_occupied_seats_for_party(party_id: PartyID) -> int:
    """Count occupied seats for the party."""
    return (
        db.session.scalar(
            select(db.func.count(DbSeat.id))
            .join(DbTicket)
            .join(DbTicketCategory)
            .filter(DbTicket.revoked == False)  # noqa: E712
            .filter(DbTicketCategory.party_id == party_id)
        )
        or 0
    )


def count_seats_for_party(party_id: PartyID) -> int:
    """Return the number of seats in seating areas for that party."""
    return (
        db.session.scalar(
            select(db.func.count(DbSeat.id))
            .join(DbSeatingArea)
            .filter(DbSeatingArea.party_id == party_id)
        )
        or 0
    )


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
    db_seat = db.session.get(DbSeat, seat_id)

    if db_seat is None:
        return None

    return _db_entity_to_seat(db_seat)


def get_seat(seat_id: SeatID) -> Seat:
    """Return the seat with that id, or raise an exception."""
    seat = find_seat(seat_id)

    if seat is None:
        raise ValueError(f'Unknown seat ID "{seat_id}"')

    return seat


def find_seats(seat_ids: set[SeatID]) -> set[Seat]:
    """Return the seats with those IDs."""
    if not seat_ids:
        return set()

    db_seats = db.session.scalars(
        select(DbSeat).filter(DbSeat.id.in_(frozenset(seat_ids)))
    ).all()

    return {_db_entity_to_seat(db_seat) for db_seat in db_seats}


def get_seats_with_tickets_for_area(
    area_id: SeatingAreaID,
) -> list[tuple[Seat, DbTicket | None]]:
    """Return the seats and their associated tickets (if available) for
    that area.
    """
    db_seats = (
        db.session.scalars(
            select(DbSeat)
            .filter_by(area_id=area_id)
            .options(
                db.joinedload(DbSeat.occupied_by_ticket),
            )
        )
        .unique()
        .all()
    )

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

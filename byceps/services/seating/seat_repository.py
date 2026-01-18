"""
byceps.services.seating.seat_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.ticketing.dbmodels.category import DbTicketCategory
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketCategory

from .dbmodels.area import DbSeatingArea
from .dbmodels.seat import DbSeat
from .models import Seat, SeatID, SeatingAreaID


def create_seat(seat: Seat) -> None:
    """Create a seat."""
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


def find_seat(seat_id: SeatID) -> DbSeat | None:
    """Return the seat with that id, or `None` if not found."""
    return db.session.get(DbSeat, seat_id)


def get_seat(seat_id: SeatID) -> DbSeat:
    """Return the seat with that id, or raise an exception."""
    db_seat = find_seat(seat_id)

    if db_seat is None:
        raise ValueError(f'Unknown seat ID "{seat_id}"')

    return db_seat


def get_seats(seat_ids: set[SeatID]) -> Sequence[DbSeat]:
    """Return the seats with those IDs."""
    if not seat_ids:
        return []

    return db.session.scalars(
        select(DbSeat).filter(DbSeat.id.in_(frozenset(seat_ids)))
    ).all()


def get_seats_with_tickets_for_area(area_id: SeatingAreaID) -> Sequence[DbSeat]:
    """Return the seats and their associated tickets (if available) for
    that area.
    """
    return (
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

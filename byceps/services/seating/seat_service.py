"""
byceps.services.seating.seat_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Dict, List, Optional, Sequence, Set, Tuple

from ...database import db
from ...typing import PartyID

from ..ticketing.models.category import Category as DbTicketCategory
from ..ticketing.models.ticket import Ticket as DbTicket
from ..ticketing.transfer.models import TicketCategory, TicketCategoryID

from .models.area import Area as DbArea
from .models.seat import Seat as DbSeat
from .transfer.models import AreaID, SeatID


def create_seat(
    area: DbArea, coord_x: int, coord_y: int, category_id: TicketCategoryID
) -> DbSeat:
    """Create a seat."""
    seat = DbSeat(area, category_id, coord_x=coord_x, coord_y=coord_y)

    db.session.add(seat)
    db.session.commit()

    return seat


def delete_seat(seat_id: SeatID) -> None:
    """Delete a seat."""
    db.session.query(DbSeat) \
        .filter_by(id=seat_id) \
        .delete()
    db.session.commit()


def count_occupied_seats_by_category(
    party_id: PartyID,
) -> List[Tuple[TicketCategory, int]]:
    """Count occupied seats for the party, grouped by ticket category."""
    subquery = db.session \
        .query(
            DbSeat.id,
            DbSeat.category_id
        ) \
        .join(DbTicket) \
        .filter_by(revoked=False) \
        .subquery()

    rows = db.session \
        .query(
            DbTicketCategory.id,
            DbTicketCategory.party_id,
            DbTicketCategory.title,
            db.func.count(subquery.c.id)
        ) \
        .outerjoin(subquery, db.and_(DbTicketCategory.id == subquery.c.category_id)) \
        .filter(DbTicketCategory.party_id == party_id) \
        .group_by(DbTicketCategory.id) \
        .order_by(DbTicketCategory.id) \
        .all()

    return [(TicketCategory(row[0], row[1], row[2]), row[3]) for row in rows]


def count_seats_for_party(party_id: PartyID) -> int:
    """Return the number of seats in seating areas for that party."""
    return DbSeat.query \
        .join(DbArea) \
        .filter(DbArea.party_id == party_id) \
        .count()


def get_seat_total_per_area(party_id: PartyID) -> Dict[AreaID, int]:
    """Return the number of seats per area for that party."""
    area_ids_and_seat_counts = db.session \
        .query(
            DbArea.id,
            db.func.count(DbSeat.id)
        ) \
        .filter_by(party_id=party_id) \
        .outerjoin(DbSeat) \
        .group_by(DbArea.id) \
        .all()

    return dict(area_ids_and_seat_counts)


def find_seat(seat_id: SeatID) -> Optional[DbSeat]:
    """Return the seat with that id, or `None` if not found."""
    return DbSeat.query.get(seat_id)


def find_seats(seat_ids: Set[SeatID]) -> Set[DbSeat]:
    """Return the seats with those IDs."""
    if not seat_ids:
        return set()

    seats = DbSeat.query \
        .filter(DbSeat.id.in_(frozenset(seat_ids))) \
        .all()

    return set(seats)


def get_seats_with_tickets_for_area(area_id: AreaID) -> Sequence[DbSeat]:
    """Return the seats and their associated tickets (if available) for
    that area.
    """
    return DbSeat.query \
        .filter_by(area_id=area_id) \
        .options(
            db.joinedload('occupied_by_ticket'),
        ) \
        .all()

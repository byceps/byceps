"""
byceps.services.ticketing.ticket_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Dict, Optional, Sequence, Set

from ...database import db, Pagination
from ...typing import PartyID, UserID

from ..party.models.party import Party as DbParty
from ..party import service as party_service
from ..seating.models.seat import Seat as DbSeat
from ..shop.order.transfer.models import OrderNumber
from ..user.models.user import User as DbUser

from .models.category import Category as DbCategory
from .models.ticket import Ticket as DbTicket
from .models.ticket_event import TicketEvent as DbTicketEvent
from .transfer.models import TicketCode, TicketID, TicketSaleStats


def delete_ticket(ticket_id: TicketID) -> None:
    """Delete a ticket and its events."""
    db.session.query(DbTicketEvent) \
        .filter_by(ticket_id=ticket_id) \
        .delete()

    db.session.query(DbTicket) \
        .filter_by(id=ticket_id) \
        .delete()

    db.session.commit()


def find_ticket(ticket_id: TicketID) -> Optional[DbTicket]:
    """Return the ticket with that id, or `None` if not found."""
    return DbTicket.query.get(ticket_id)


def find_ticket_by_code(code: TicketCode) -> Optional[DbTicket]:
    """Return the ticket with that code, or `None` if not found."""
    return DbTicket.query \
        .filter_by(code=code) \
        .one_or_none()


def find_tickets(ticket_ids: Set[TicketID]) -> Sequence[DbTicket]:
    """Return the tickets with those ids."""
    if not ticket_ids:
        return []

    return DbTicket.query \
        .filter(DbTicket.id.in_(ticket_ids)) \
        .all()


def find_tickets_created_by_order(
    order_number: OrderNumber,
) -> Sequence[DbTicket]:
    """Return the tickets created by this order (as it was marked as paid)."""
    return DbTicket.query \
        .filter_by(order_number=order_number) \
        .order_by(DbTicket.created_at) \
        .all()


def find_tickets_for_seat_manager(
    user_id: UserID, party_id: PartyID
) -> Sequence[DbTicket]:
    """Return the tickets for that party whose respective seats the user
    is entitled to manage.
    """
    return DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.revoked == False) \
        .filter(
            (
                (DbTicket.seat_managed_by_id == None) &
                (DbTicket.owned_by_id == user_id)
            ) |
            (DbTicket.seat_managed_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat'),
        ) \
        .all()


def find_tickets_related_to_user(user_id: UserID) -> Sequence[DbTicket]:
    """Return tickets related to the user."""
    return DbTicket.query \
        .filter(
            (DbTicket.owned_by_id == user_id) |
            (DbTicket.seat_managed_by_id == user_id) |
            (DbTicket.user_managed_by_id == user_id) |
            (DbTicket.used_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('occupied_seat').joinedload('category'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
            db.joinedload('used_by'),
        ) \
        .order_by(DbTicket.created_at) \
        .all()


def find_tickets_related_to_user_for_party(
    user_id: UserID, party_id: PartyID
) -> Sequence[DbTicket]:
    """Return tickets related to the user for the party."""
    return DbTicket.query \
        .for_party(party_id) \
        .filter(
            (DbTicket.owned_by_id == user_id) |
            (DbTicket.seat_managed_by_id == user_id) |
            (DbTicket.user_managed_by_id == user_id) |
            (DbTicket.used_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('occupied_seat').joinedload('category'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
            db.joinedload('used_by'),
        ) \
        .order_by(DbTicket.created_at) \
        .all()


def find_tickets_used_by_user(
    user_id: UserID, party_id: PartyID
) -> Sequence[DbTicket]:
    """Return the tickets (if any) used by the user for that party."""
    return DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.used_by_id == user_id) \
        .filter(DbTicket.revoked == False) \
        .outerjoin(DbSeat) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(DbSeat.coord_x, DbSeat.coord_y) \
        .all()


def uses_any_ticket_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user uses any ticket for that party."""
    q = DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.used_by_id == user_id) \
        .filter(DbTicket.revoked == False)

    return db.session.query(q.exists()).scalar()


def select_ticket_users_for_party(
    user_ids: Set[UserID], party_id: PartyID
) -> Set[UserID]:
    """Return the IDs of those users that use a ticket for that party."""
    if not user_ids:
        return set()

    q = DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.used_by_id == DbUser.id) \
        .filter(DbTicket.revoked == False)

    rows = db.session.query(DbUser.id) \
        .filter(q.exists()) \
        .filter(DbUser.id.in_(user_ids)) \
        .all()

    return {row[0] for row in rows}


def get_ticket_with_details(ticket_id: TicketID) -> Optional[DbTicket]:
    """Return the ticket with that id, or `None` if not found."""
    return DbTicket.query \
        .options(
            db.joinedload('category'),
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('owned_by'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
        ) \
        .get(ticket_id)


def get_tickets_with_details_for_party_paginated(
    party_id: PartyID, page: int, per_page: int, *, search_term=None
) -> Pagination:
    """Return the party's tickets to show on the specified page."""
    query = DbTicket.query \
        .for_party(party_id) \
        .options(
            db.joinedload('category'),
            db.joinedload('owned_by'),
            db.joinedload('occupied_seat').joinedload('area'),
        )

    if search_term:
        ilike_pattern = f'%{search_term}%'
        query = query \
            .filter(DbTicket.code.ilike(ilike_pattern))

    return query \
        .order_by(DbTicket.created_at) \
        .paginate(page, per_page)


def get_ticket_count_by_party_id() -> Dict[PartyID, int]:
    """Return ticket count (including 0) per party, indexed by party ID."""
    party = db.aliased(DbParty)

    subquery = db.session \
        .query(
            db.func.count(DbTicket.id)
        ) \
        .join(DbCategory) \
        .filter(DbCategory.party_id == party.id) \
        .filter(DbTicket.revoked == False) \
        .subquery() \
        .as_scalar()

    party_ids_and_ticket_counts = db.session \
        .query(
            party.id,
            subquery
        ) \
        .all()

    return dict(party_ids_and_ticket_counts)


def count_revoked_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of revoked tickets for that party."""
    return DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.revoked == True) \
        .count()


def count_sold_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of "sold" (i.e. generated and not revoked)
    tickets for that party.
    """
    return DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.revoked == False) \
        .count()


def count_tickets_checked_in_for_party(party_id: PartyID) -> int:
    """Return the number tickets for that party that were used to check
    in their respective user.
    """
    return DbTicket.query \
        .for_party(party_id) \
        .filter(DbTicket.user_checked_in == True) \
        .count()


def get_ticket_sale_stats(party_id: PartyID) -> TicketSaleStats:
    """Return the number of maximum and sold tickets, respectively."""
    party = party_service.get_party(party_id)

    sold = count_sold_tickets_for_party(party.id)

    return TicketSaleStats(
        tickets_max=party.max_ticket_quantity,
        tickets_sold=sold,
    )

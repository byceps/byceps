"""
byceps.services.ticketing.ticket_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from enum import Enum
from typing import Optional

from sqlalchemy import select

from ...database import db, paginate, Pagination
from ...typing import PartyID, UserID

from ..party import party_service
from ..seating.dbmodels.seat import DbSeat
from ..seating.transfer.models import SeatID
from ..shop.order.transfer.number import OrderNumber
from ..user.dbmodels.user import DbUser

from .dbmodels.category import DbTicketCategory
from .dbmodels.ticket import DbTicket
from .dbmodels.log import DbTicketLogEntry
from . import ticket_code_service, ticket_log_service
from .transfer.models import (
    TicketCategoryID,
    TicketCode,
    TicketID,
    TicketSaleStats,
)


def update_ticket_code(
    ticket_id: TicketID, code: str, initiator_id: UserID
) -> None:
    """Set a custom code for the ticket."""
    db_ticket = get_ticket(ticket_id)

    if not ticket_code_service.is_ticket_code_wellformed(code):
        raise ValueError(f'Ticket code "{code}" is not well-formed')

    old_code = db_ticket.code

    db_ticket.code = code

    db_log_entry = ticket_log_service.build_entry(
        'ticket-code-changed',
        db_ticket.id,
        {
            'old_code': old_code,
            'new_code': code,
            'initiator_id': str(initiator_id),
        },
    )
    db.session.add(db_log_entry)

    db.session.commit()


def delete_ticket(ticket_id: TicketID) -> None:
    """Delete a ticket and its log entries."""
    db.session.query(DbTicketLogEntry).filter_by(ticket_id=ticket_id).delete()

    db.session.query(DbTicket).filter_by(id=ticket_id).delete()

    db.session.commit()


def find_ticket(ticket_id: TicketID) -> Optional[DbTicket]:
    """Return the ticket with that id, or `None` if not found."""
    return db.session.get(DbTicket, ticket_id)


def get_ticket(ticket_id: TicketID) -> DbTicket:
    """Return the ticket with that id, or raise an exception."""
    db_ticket = find_ticket(ticket_id)

    if db_ticket is None:
        raise ValueError(f'Unknown ticket ID "{ticket_id}"')

    return db_ticket


def find_ticket_by_code(
    party_id: PartyID, code: TicketCode
) -> Optional[DbTicket]:
    """Return the ticket with that code for that party, or `None` if not
    found.
    """
    return (
        db.session.query(DbTicket)
        .filter_by(party_id=party_id)
        .filter_by(code=code)
        .one_or_none()
    )


def find_tickets(ticket_ids: set[TicketID]) -> list[DbTicket]:
    """Return the tickets with those ids."""
    if not ticket_ids:
        return []

    return db.session.query(DbTicket).filter(DbTicket.id.in_(ticket_ids)).all()


def find_tickets_created_by_order(
    order_number: OrderNumber,
) -> list[DbTicket]:
    """Return the tickets created by this order (as it was marked as paid)."""
    return (
        db.session.query(DbTicket)
        .filter_by(order_number=order_number)
        .order_by(DbTicket.created_at)
        .all()
    )


def find_tickets_for_seat_manager(
    user_id: UserID, party_id: PartyID
) -> list[DbTicket]:
    """Return the tickets for that party whose respective seats the user
    is entitled to manage.
    """
    return (
        db.session.query(DbTicket)
        .filter(DbTicket.party_id == party_id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(
            (
                (DbTicket.seat_managed_by_id.is_(None))
                & (DbTicket.owned_by_id == user_id)
            )
            | (DbTicket.seat_managed_by_id == user_id)
        )
        .options(
            db.joinedload(DbTicket.occupied_seat),
        )
        .all()
    )


def find_tickets_related_to_user(user_id: UserID) -> list[DbTicket]:
    """Return tickets related to the user."""
    return (
        db.session.query(DbTicket)
        .filter(
            (DbTicket.owned_by_id == user_id)
            | (DbTicket.seat_managed_by_id == user_id)
            | (DbTicket.user_managed_by_id == user_id)
            | (DbTicket.used_by_id == user_id)
        )
        .options(
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.category),
            db.joinedload(DbTicket.seat_managed_by),
            db.joinedload(DbTicket.user_managed_by),
            db.joinedload(DbTicket.used_by),
        )
        .order_by(DbTicket.created_at)
        .all()
    )


def find_tickets_related_to_user_for_party(
    user_id: UserID, party_id: PartyID
) -> list[DbTicket]:
    """Return tickets related to the user for the party."""
    return (
        db.session.query(DbTicket)
        .filter(DbTicket.party_id == party_id)
        .filter(
            (DbTicket.owned_by_id == user_id)
            | (DbTicket.seat_managed_by_id == user_id)
            | (DbTicket.user_managed_by_id == user_id)
            | (DbTicket.used_by_id == user_id)
        )
        .options(
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.category),
            db.joinedload(DbTicket.seat_managed_by),
            db.joinedload(DbTicket.user_managed_by),
            db.joinedload(DbTicket.used_by),
        )
        .order_by(DbTicket.created_at)
        .all()
    )


def find_tickets_used_by_user(
    user_id: UserID, party_id: PartyID
) -> list[DbTicket]:
    """Return the tickets (if any) used by the user for that party."""
    return (
        db.session.query(DbTicket)
        .filter(DbTicket.party_id == party_id)
        .filter(DbTicket.used_by_id == user_id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .outerjoin(DbSeat)
        .options(
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
        )
        .order_by(DbSeat.coord_x, DbSeat.coord_y)
        .all()
    )


def uses_any_ticket_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user uses any ticket for that party."""
    q = (
        db.session.query(DbTicket)
        .filter_by(party_id=party_id)
        .filter_by(used_by_id=user_id)
        .filter_by(revoked=False)
    )

    return db.session.query(q.exists()).scalar()


def get_ticket_users_for_party(party_id: PartyID) -> set[UserID]:
    """Return the IDs of the users of tickets for that party."""
    rows = (
        db.session.query(DbTicket.used_by_id)
        .filter(DbTicket.party_id == party_id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(DbTicket.used_by_id.is_not(None))
        .all()
    )

    return {row[0] for row in rows}


def select_ticket_users_for_party(
    user_ids: set[UserID], party_id: PartyID
) -> set[UserID]:
    """Return the IDs of those users that use a ticket for that party."""
    if not user_ids:
        return set()

    q = (
        db.session.query(DbTicket)
        .filter(DbTicket.party_id == party_id)
        .filter(DbTicket.used_by_id == DbUser.id)
        .filter(DbTicket.revoked == False)  # noqa: E712
    )

    rows = (
        db.session.query(DbUser.id)
        .filter(q.exists())
        .filter(DbUser.id.in_(user_ids))
        .all()
    )

    return {row[0] for row in rows}


def get_ticket_with_details(ticket_id: TicketID) -> Optional[DbTicket]:
    """Return the ticket with that id, or `None` if not found."""
    return (
        db.session.query(DbTicket)
        .options(
            db.joinedload(DbTicket.category),
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
            db.joinedload(DbTicket.owned_by),
            db.joinedload(DbTicket.seat_managed_by),
            db.joinedload(DbTicket.user_managed_by),
        )
        .get(ticket_id)
    )


FilterMode = Enum('FilterMode', ['select', 'reject'])


def get_tickets_with_details_for_party_paginated(
    party_id: PartyID,
    page: int,
    per_page: int,
    *,
    search_term: Optional[str] = None,
    filter_category_id: Optional[TicketCategoryID] = None,
    filter_revoked: Optional[FilterMode] = None,
    filter_checked_in: Optional[FilterMode] = None,
) -> Pagination:
    """Return the party's tickets to show on the specified page."""
    items_query = (
        select(DbTicket)
        .filter(DbTicket.party_id == party_id)
        .join(DbTicketCategory)
        .options(
            db.joinedload(DbTicket.category),
            db.joinedload(DbTicket.owned_by),
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
        )
        .order_by(DbTicket.created_at)
    )

    count_query = (
        select(db.func.count(DbTicket.id))
        .filter(DbTicket.party_id == party_id)
        .join(DbTicketCategory)
    )

    if search_term:
        ilike_pattern = f'%{search_term}%'
        items_query = items_query.filter(DbTicket.code.ilike(ilike_pattern))
        count_query = count_query.filter(DbTicket.code.ilike(ilike_pattern))

    if filter_category_id:
        items_query = items_query.filter(
            DbTicketCategory.id == str(filter_category_id)
        )
        count_query = count_query.filter(
            DbTicketCategory.id == str(filter_category_id)
        )

    if filter_revoked is not None:
        items_query = items_query.filter(
            DbTicket.revoked == (filter_revoked is FilterMode.select)
        )
        count_query = count_query.filter(
            DbTicket.revoked == (filter_revoked is FilterMode.select)
        )

    if filter_checked_in is not None:
        items_query = items_query.filter(
            DbTicket.user_checked_in == (filter_checked_in is FilterMode.select)
        )
        count_query = count_query.filter(
            DbTicket.user_checked_in == (filter_checked_in is FilterMode.select)
        )

    return paginate(
        items_query, count_query, page, per_page, scalar_result=True
    )


def count_revoked_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of revoked tickets for that party."""
    return (
        db.session.query(DbTicket)
        .filter_by(party_id=party_id)
        .filter_by(revoked=True)
        .count()
    )


def count_sold_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of "sold" (i.e. generated and not revoked)
    tickets for that party.
    """
    return (
        db.session.query(DbTicket)
        .filter_by(party_id=party_id)
        .filter_by(revoked=False)
        .count()
    )


def count_tickets_checked_in_for_party(party_id: PartyID) -> int:
    """Return the number tickets for that party that were used to check
    in their respective user.
    """
    return (
        db.session.query(DbTicket)
        .filter_by(party_id=party_id)
        .filter_by(user_checked_in=True)
        .count()
    )


def get_ticket_sale_stats(party_id: PartyID) -> TicketSaleStats:
    """Return the number of maximum and sold tickets, respectively."""
    party = party_service.get_party(party_id)

    sold = count_sold_tickets_for_party(party.id)

    return TicketSaleStats(
        tickets_max=party.max_ticket_quantity,
        tickets_sold=sold,
    )


def find_ticket_occupying_seat(seat_id: SeatID) -> Optional[DbTicket]:
    """Return the ticket that occupies that seat, or `None` if not found."""
    return db.session.execute(
        select(DbTicket).filter_by(occupied_seat_id=seat_id)
    ).one_or_none()

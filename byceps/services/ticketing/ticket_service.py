"""
byceps.services.ticketing.ticket_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum

from sqlalchemy import delete, select

from byceps.database import db, paginate, Pagination
from byceps.services.party import party_service
from byceps.services.seating.dbmodels.seat import DbSeat
from byceps.services.seating.models import SeatID
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import PartyID, UserID

from . import ticket_code_service, ticket_log_service
from .dbmodels.category import DbTicketCategory
from .dbmodels.log import DbTicketLogEntry
from .dbmodels.ticket import DbTicket
from .models.ticket import (
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
    db.session.execute(delete(DbTicketLogEntry).filter_by(ticket_id=ticket_id))
    db.session.execute(delete(DbTicket).filter_by(id=ticket_id))
    db.session.commit()


def find_ticket(ticket_id: TicketID) -> DbTicket | None:
    """Return the ticket with that id, or `None` if not found."""
    return db.session.get(DbTicket, ticket_id)


def get_ticket(ticket_id: TicketID) -> DbTicket:
    """Return the ticket with that id, or raise an exception."""
    db_ticket = find_ticket(ticket_id)

    if db_ticket is None:
        raise ValueError(f'Unknown ticket ID "{ticket_id}"')

    return db_ticket


def find_ticket_by_code(party_id: PartyID, code: TicketCode) -> DbTicket | None:
    """Return the ticket with that code for that party, or `None` if not
    found.
    """
    return db.session.execute(
        select(DbTicket).filter_by(party_id=party_id).filter_by(code=code)
    ).scalar_one_or_none()


def get_tickets(ticket_ids: set[TicketID]) -> Sequence[DbTicket]:
    """Return the tickets with those ids."""
    if not ticket_ids:
        return []

    return db.session.scalars(
        select(DbTicket).filter(DbTicket.id.in_(ticket_ids))
    ).all()


def get_tickets_created_by_order(
    order_number: OrderNumber,
) -> Sequence[DbTicket]:
    """Return the tickets created by this order (as it was marked as paid)."""
    return db.session.scalars(
        select(DbTicket)
        .filter_by(order_number=order_number)
        .order_by(DbTicket.created_at)
    ).all()


def get_tickets_for_seat_manager(
    user_id: UserID, party_id: PartyID
) -> Sequence[DbTicket]:
    """Return the tickets for that party whose respective seats the user
    is entitled to manage.
    """
    return (
        db.session.scalars(
            select(DbTicket)
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
        )
        .unique()
        .all()
    )


def get_tickets_related_to_user(user_id: UserID) -> Sequence[DbTicket]:
    """Return tickets related to the user."""
    return (
        db.session.scalars(
            select(DbTicket)
            .filter(
                (DbTicket.owned_by_id == user_id)
                | (DbTicket.seat_managed_by_id == user_id)
                | (DbTicket.user_managed_by_id == user_id)
                | (DbTicket.used_by_id == user_id)
            )
            .options(
                db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
                db.joinedload(DbTicket.occupied_seat).joinedload(
                    DbSeat.category
                ),
                db.joinedload(DbTicket.seat_managed_by),
                db.joinedload(DbTicket.user_managed_by),
                db.joinedload(DbTicket.used_by),
            )
            .order_by(DbTicket.created_at)
        )
        .unique()
        .all()
    )


def get_tickets_related_to_user_for_party(
    user_id: UserID, party_id: PartyID
) -> Sequence[DbTicket]:
    """Return tickets related to the user for the party."""
    return (
        db.session.scalars(
            select(DbTicket)
            .filter(DbTicket.party_id == party_id)
            .filter(
                (DbTicket.owned_by_id == user_id)
                | (DbTicket.seat_managed_by_id == user_id)
                | (DbTicket.user_managed_by_id == user_id)
                | (DbTicket.used_by_id == user_id)
            )
            .options(
                db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
                db.joinedload(DbTicket.occupied_seat).joinedload(
                    DbSeat.category
                ),
                db.joinedload(DbTicket.seat_managed_by),
                db.joinedload(DbTicket.user_managed_by),
                db.joinedload(DbTicket.used_by),
            )
            .order_by(DbTicket.created_at)
        )
        .unique()
        .all()
    )


def get_tickets_used_by_user(
    user_id: UserID, party_id: PartyID
) -> Sequence[DbTicket]:
    """Return the tickets (if any) used by the user for that party."""
    return (
        db.session.scalars(
            select(DbTicket)
            .filter(DbTicket.party_id == party_id)
            .filter(DbTicket.used_by_id == user_id)
            .filter(DbTicket.revoked == False)  # noqa: E712
            .outerjoin(DbSeat)
            .options(
                db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
            )
            .order_by(DbSeat.coord_x, DbSeat.coord_y)
        )
        .unique()
        .all()
    )


def uses_any_ticket_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user uses any ticket for that party."""
    return db.session.scalar(
        select(
            select(DbTicket)
            .filter_by(party_id=party_id)
            .filter_by(used_by_id=user_id)
            .filter_by(revoked=False)
            .exists()
        )
    )


def get_ticket_users_for_party(party_id: PartyID) -> set[UserID]:
    """Return the IDs of the users of tickets for that party."""
    user_ids = db.session.scalars(
        select(DbTicket.used_by_id)
        .filter(DbTicket.party_id == party_id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .filter(DbTicket.used_by_id.is_not(None))
    ).all()

    return set(user_ids)


def select_ticket_users_for_party(
    user_ids: set[UserID], party_id: PartyID
) -> set[UserID]:
    """Return the IDs of those users that use a ticket for that party."""
    if not user_ids:
        return set()

    stmt = (
        select(DbTicket)
        .filter(DbTicket.party_id == party_id)
        .filter(DbTicket.used_by_id == DbUser.id)
        .filter(DbTicket.revoked == False)  # noqa: E712
    )

    user_ids = db.session.scalars(
        select(DbUser.id).filter(stmt.exists()).filter(DbUser.id.in_(user_ids))
    ).all()

    return set(user_ids)


def get_ticket_with_details(ticket_id: TicketID) -> DbTicket | None:
    """Return the ticket with that id, or `None` if not found."""
    return db.session.scalar(
        select(DbTicket)
        .options(
            db.joinedload(DbTicket.category),
            db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
            db.joinedload(DbTicket.owned_by),
            db.joinedload(DbTicket.seat_managed_by),
            db.joinedload(DbTicket.user_managed_by),
        )
        .filter_by(id=ticket_id)
    )


FilterMode = Enum('FilterMode', ['select', 'reject'])


def get_tickets_with_details_for_party_paginated(
    party_id: PartyID,
    page: int,
    per_page: int,
    *,
    search_term: str | None = None,
    filter_category_id: TicketCategoryID | None = None,
    filter_revoked: FilterMode | None = None,
    filter_checked_in: FilterMode | None = None,
) -> Pagination:
    """Return the party's tickets to show on the specified page."""
    stmt = (
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

    if search_term:
        ilike_pattern = f'%{search_term}%'
        stmt = stmt.filter(DbTicket.code.ilike(ilike_pattern))

    if filter_category_id:
        stmt = stmt.filter(DbTicketCategory.id == str(filter_category_id))

    if filter_revoked is not None:
        stmt = stmt.filter(
            DbTicket.revoked == (filter_revoked is FilterMode.select)
        )

    if filter_checked_in is not None:
        stmt = stmt.filter(
            DbTicket.user_checked_in == (filter_checked_in is FilterMode.select)
        )

    return paginate(stmt, page, per_page)


def count_revoked_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of revoked tickets for that party."""
    return db.session.scalar(
        select(db.func.count(DbTicket.id))
        .filter_by(party_id=party_id)
        .filter_by(revoked=True)
    )


def count_sold_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of "sold" (i.e. generated and not revoked)
    tickets for that party.
    """
    return db.session.scalar(
        select(db.func.count(DbTicket.id))
        .filter_by(party_id=party_id)
        .filter_by(revoked=False)
    )


def count_tickets_checked_in_for_party(party_id: PartyID) -> int:
    """Return the number tickets for that party that were used to check
    in their respective user.
    """
    return db.session.scalar(
        select(db.func.count(DbTicket.id))
        .filter_by(party_id=party_id)
        .filter_by(user_checked_in=True)
    )


def get_ticket_sale_stats(party_id: PartyID) -> TicketSaleStats:
    """Return the number of maximum and sold tickets, respectively."""
    party = party_service.get_party(party_id)

    sold = count_sold_tickets_for_party(party.id)

    return TicketSaleStats(
        tickets_max=party.max_ticket_quantity,
        tickets_sold=sold,
    )


def find_ticket_occupying_seat(seat_id: SeatID) -> DbTicket | None:
    """Return the ticket that occupies that seat, or `None` if not found."""
    return db.session.execute(
        select(DbTicket).filter_by(occupied_seat_id=seat_id)
    ).one_or_none()

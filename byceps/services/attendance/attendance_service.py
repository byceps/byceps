"""
byceps.services.attendance.attendance_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from typing import Iterable, Optional

from sqlalchemy import select

from ...database import db, paginate, Pagination
from ...typing import PartyID, UserID

from ..seating.dbmodels.seat import DbSeat
from ..ticketing.dbmodels.category import DbTicketCategory
from ..ticketing.dbmodels.ticket import DbTicket
from ..user.dbmodels.user import DbUser

from .models import Attendee, AttendeeTicket


def get_attendees_paginated(
    party_id: PartyID,
    page: int,
    per_page: int,
    *,
    search_term: Optional[str] = None,
) -> Pagination:
    """Return the party's ticket users with tickets and seats."""
    users_paginated = _get_users_paginated(
        party_id, page, per_page, search_term=search_term
    )
    users = users_paginated.items
    user_ids = {u.id for u in users}

    tickets = _get_tickets_for_users(party_id, user_ids)
    tickets_by_user_id = _index_tickets_by_user_id(tickets)

    attendees = list(_generate_attendees(users, tickets_by_user_id))

    users_paginated.items = attendees
    return users_paginated


def _get_users_paginated(
    party_id: PartyID,
    page: int,
    per_page: int,
    *,
    search_term: Optional[str] = None,
) -> Pagination:
    # Drop revoked tickets here already to avoid users without tickets
    # being included in the list.

    items_stmt = (
        select(
            DbUser, db.func.lower(DbUser.screen_name).label('screen_name_lower')
        )
        .distinct()
        .options(
            db.load_only(DbUser.id, DbUser.screen_name, DbUser.deleted),
            db.joinedload(DbUser.avatar),
        )
        .join(DbTicket, DbTicket.used_by_id == DbUser.id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
        .order_by('screen_name_lower')
    )

    count_stmt = (
        select(db.func.count(db.distinct(DbUser.id)))
        .join(DbTicket, DbTicket.used_by_id == DbUser.id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
    )

    if search_term:
        items_stmt = items_stmt.filter(
            DbUser.screen_name.ilike(f'%{search_term}%')
        )
        count_stmt = count_stmt.filter(
            DbUser.screen_name.ilike(f'%{search_term}%')
        )

    return paginate(items_stmt, count_stmt, page, per_page)


def _get_tickets_for_users(
    party_id: PartyID, user_ids: set[UserID]
) -> list[DbTicket]:
    return (
        db.session.scalars(
            select(DbTicket)
            .options(
                db.joinedload(DbTicket.category),
                db.joinedload(DbTicket.occupied_seat).joinedload(DbSeat.area),
            )
            .filter(DbTicket.party_id == party_id)
            .filter(DbTicket.used_by_id.in_(user_ids))
            .filter(DbTicket.revoked == False)  # noqa: E712
        )
        .unique()
        .all()
    )


def _index_tickets_by_user_id(
    tickets: Iterable[DbTicket],
) -> dict[UserID, set[DbTicket]]:
    tickets_by_user_id = defaultdict(set)
    for ticket in tickets:
        tickets_by_user_id[ticket.used_by_id].add(ticket)
    return tickets_by_user_id


def _generate_attendees(
    users: Iterable[DbUser], tickets_by_user_id: dict[UserID, set[DbTicket]]
) -> Iterable[Attendee]:
    for user in users:
        tickets = tickets_by_user_id[user.id]
        attendee_tickets = _to_attendee_tickets(tickets)
        yield Attendee(user, attendee_tickets)


def _to_attendee_tickets(tickets: Iterable[DbTicket]) -> list[AttendeeTicket]:
    attendee_tickets = [
        AttendeeTicket(t.occupied_seat, t.user_checked_in) for t in tickets
    ]
    attendee_tickets.sort(key=_get_attendee_ticket_sort_key)
    return attendee_tickets


def _get_attendee_ticket_sort_key(
    attendee_ticket: AttendeeTicket,
) -> tuple[bool, str, bool]:
    return (
        # List tickets with occupied seat first.
        attendee_ticket.seat is None,

        # Sort by seat label.
        attendee_ticket.seat.label if attendee_ticket.seat else None,

        # List checked in tickets first.
        not attendee_ticket.checked_in,
    )

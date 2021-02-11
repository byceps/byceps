"""
byceps.services.attendance.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

from ...database import db, paginate, Pagination
from ...typing import PartyID, UserID

from ..ticketing.dbmodels.ticket import Category as DbCategory, Ticket as DbTicket
from ..user.dbmodels.user import User as DbUser

from .transfer.models import Attendee, AttendeeTicket


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
    query = DbUser.query \
        .distinct() \
        .options(
            db.load_only('id', 'screen_name', 'deleted'),
            db.joinedload('avatar_selection').joinedload('avatar'),
        ) \
        .join(DbTicket, DbTicket.used_by_id == DbUser.id) \
        .filter(DbTicket.revoked == False) \
        .join(DbCategory).filter(DbCategory.party_id == party_id)

    if search_term:
        query = query \
            .filter(DbUser.screen_name.ilike(f'%{search_term}%'))

    query = query \
        .order_by(db.func.lower(DbUser.screen_name))

    return paginate(query, page, per_page)


def _get_tickets_for_users(
    party_id: PartyID, user_ids: Set[UserID]
) -> List[DbTicket]:
    return DbTicket.query \
        .options(
            db.joinedload('category'),
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .for_party(party_id) \
        .filter(DbTicket.used_by_id.in_(user_ids)) \
        .filter(DbTicket.revoked == False) \
        .all()


def _index_tickets_by_user_id(
    tickets: Iterable[DbTicket],
) -> Dict[UserID, Set[DbTicket]]:
    tickets_by_user_id = defaultdict(set)
    for ticket in tickets:
        tickets_by_user_id[ticket.used_by_id].add(ticket)
    return tickets_by_user_id


def _generate_attendees(
    users: Iterable[DbUser], tickets_by_user_id: Dict[UserID, Set[DbTicket]]
) -> Iterable[Attendee]:
    for user in users:
        tickets = tickets_by_user_id[user.id]
        attendee_tickets = _to_attendee_tickets(tickets)
        yield Attendee(user, attendee_tickets)


def _to_attendee_tickets(tickets: Iterable[DbTicket]) -> List[AttendeeTicket]:
    attendee_tickets = [
        AttendeeTicket(t.occupied_seat, t.user_checked_in) for t in tickets
    ]
    attendee_tickets.sort(key=_get_attendee_ticket_sort_key)
    return attendee_tickets


def _get_attendee_ticket_sort_key(
    attendee_ticket: AttendeeTicket,
) -> Tuple[bool, str, bool]:
    return (
        # List tickets with occupied seat first.
        attendee_ticket.seat is None,

        # Sort by seat label.
        attendee_ticket.seat.label if attendee_ticket.seat else None,

        # List checked in tickets first.
        not attendee_ticket.checked_in,
    )

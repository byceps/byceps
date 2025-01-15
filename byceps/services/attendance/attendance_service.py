"""
byceps.services.attendance.attendance_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterable, Sequence

from sqlalchemy import select

from byceps.database import db, paginate, Pagination
from byceps.services.orga_team import orga_team_service
from byceps.services.party.models import PartyID
from byceps.services.seating import seating_area_service
from byceps.services.seating.dbmodels.seat import DbSeat
from byceps.services.ticketing.dbmodels.category import DbTicketCategory
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketID
from byceps.services.user import user_service
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID

from .models import Attendee, AttendeeSeat, AttendeeTicket


def get_attendees_paginated(
    party_id: PartyID,
    page: int,
    per_page: int,
    *,
    search_term: str | None = None,
) -> Pagination:
    """Return the party's ticket users with tickets and seats."""
    pagination = _get_user_ids_paginated(
        party_id, page, per_page, search_term=search_term
    )
    user_ids = set(pagination.items)

    db_tickets = _get_tickets_for_users(party_id, user_ids)
    tickets_by_user_id = _index_tickets_by_user_id(db_tickets)

    attendees = list(
        _generate_attendees(party_id, user_ids, tickets_by_user_id)
    )

    pagination.items = attendees

    return pagination


def _get_user_ids_paginated(
    party_id: PartyID,
    page: int,
    per_page: int,
    *,
    search_term: str | None = None,
) -> Pagination:
    # Drop revoked tickets here already to avoid users without tickets
    # being included in the list.

    stmt = (
        select(
            DbUser.id,
            db.func.lower(DbUser.screen_name).label('screen_name_lower'),
        )
        .distinct()
        .join(DbTicket, DbTicket.used_by_id == DbUser.id)
        .filter(DbTicket.revoked == False)  # noqa: E712
        .join(DbTicketCategory)
        .filter(DbTicketCategory.party_id == party_id)
        .order_by('screen_name_lower')
    )

    if search_term:
        stmt = stmt.filter(DbUser.screen_name.ilike(f'%{search_term}%'))

    return paginate(stmt, page, per_page)


def _get_tickets_for_users(
    party_id: PartyID, user_ids: set[UserID]
) -> Sequence[DbTicket]:
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
    db_tickets: Iterable[DbTicket],
) -> dict[UserID, set[DbTicket]]:
    tickets_by_user_id = defaultdict(set)
    for db_ticket in db_tickets:
        tickets_by_user_id[db_ticket.used_by_id].add(db_ticket)
    return tickets_by_user_id


def _generate_attendees(
    party_id: PartyID,
    user_ids: set[UserID],
    tickets_by_user_id: dict[UserID, set[DbTicket]],
) -> Iterable[Attendee]:
    users = user_service.get_users(user_ids, include_avatars=True)

    # Sort *again* case-insensitively by screen name.
    # Sorting in the database was relevant to correctly select
    # the entries for the page.
    # Sorting here is necessary to restore that order for a set
    # of users.
    users_sorted = list(
        sorted(users, key=lambda u: (u.screen_name or '').lower())
    )

    orga_ids = orga_team_service.select_orgas_for_party(user_ids, party_id)

    for user in users_sorted:
        is_orga = user.id in orga_ids

        db_tickets = tickets_by_user_id[user.id]
        attendee_tickets = _to_attendee_tickets(db_tickets)

        yield Attendee(
            user=user,
            is_orga=is_orga,
            tickets=attendee_tickets,
        )


def _to_attendee_tickets(
    db_tickets: Iterable[DbTicket],
) -> list[AttendeeTicket]:
    attendee_tickets = [
        _to_attendee_ticket(db_ticket) for db_ticket in db_tickets
    ]
    attendee_tickets.sort(key=_get_attendee_ticket_sort_key)
    return attendee_tickets


def _to_attendee_ticket(db_ticket: DbTicket) -> AttendeeTicket:
    return AttendeeTicket(
        id=db_ticket.id,
        category_title=db_ticket.category.title,
        seat=_to_attendee_seat(db_ticket),
        checked_in=db_ticket.user_checked_in,
    )


def _to_attendee_seat(db_ticket: DbTicket) -> AttendeeSeat | None:
    db_seat = db_ticket.occupied_seat
    if not db_seat:
        return None

    seating_area = seating_area_service._db_entity_to_area(db_seat.area)

    return AttendeeSeat(
        id=db_seat.id,
        area=seating_area,
        label=db_seat.label,
    )


def _get_attendee_ticket_sort_key(
    attendee_ticket: AttendeeTicket,
) -> tuple[bool, str | None, bool, TicketID]:
    return (
        # List tickets with occupied seat first.
        attendee_ticket.seat is None,
        # Sort by seat label.
        (attendee_ticket.seat.label if attendee_ticket.seat else '') or '',
        # List checked in tickets first.
        not attendee_ticket.checked_in,
        # Sort by ticket ID to stabilize sort.
        attendee_ticket.id,
    )

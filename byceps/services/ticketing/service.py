"""
byceps.services.ticketing.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict
from datetime import datetime
from itertools import chain
from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, Set

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import PartyID, UserID

from ..party.models import Party, PartyTuple
from ..party import service as party_service
from ..seating.models.category import Category
from ..seating.models.seat import Seat
from ..user.models.user import UserTuple
from ..user import service as user_service

from .models.archived_attendance import ArchivedAttendance
from .models.ticket import Ticket, TicketID
from .models.ticket_bundle import TicketBundle


# -------------------------------------------------------------------- #
# tickets


def create_ticket(category: Category, owned_by_id: UserID) -> Sequence[Ticket]:
    """Create a single ticket."""
    return create_tickets(category, owned_by_id, 1)


def create_tickets(category: Category, owned_by_id: UserID, quantity: int
                  ) -> Sequence[Ticket]:
    """Create a number of tickets of the same category for a single owner."""
    tickets = list(_build_tickets(category, owned_by_id, quantity))

    db.session.add_all(tickets)
    db.session.commit()

    return tickets


def _build_tickets(category: Category, owned_by_id: UserID, quantity: int, *,
                   bundle: Optional[TicketBundle]=None) -> Iterator[Ticket]:
    if quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    for _ in range(quantity):
        yield Ticket(category, owned_by_id, bundle=bundle)


def find_ticket(ticket_id: TicketID) -> Optional[Ticket]:
    """Return the ticket with that id, or `None` if not found."""
    return Ticket.query.get(ticket_id)


def find_tickets_related_to_user(user_id: UserID) -> Sequence[Ticket]:
    """Return tickets related to the user."""
    return Ticket.query \
        .filter(
            (Ticket.owned_by_id == user_id) |
            (Ticket.seat_managed_by_id == user_id) |
            (Ticket.user_managed_by_id == user_id) |
            (Ticket.used_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('occupied_seat').joinedload('category'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
            db.joinedload('used_by'),
        ) \
        .order_by(Ticket.created_at) \
        .all()


def find_tickets_related_to_user_for_party(user_id: UserID, party_id: PartyID
                                          ) -> Sequence[Ticket]:
    """Return tickets related to the user for the party."""
    return Ticket.query \
        .for_party_id(party_id) \
        .filter(
            (Ticket.owned_by_id == user_id) |
            (Ticket.seat_managed_by_id == user_id) |
            (Ticket.user_managed_by_id == user_id) |
            (Ticket.used_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('occupied_seat').joinedload('category'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
            db.joinedload('used_by'),
        ) \
        .order_by(Ticket.created_at) \
        .all()


def find_tickets_used_by_user(user_id: UserID, party_id: PartyID
                             ) -> Sequence[Ticket]:
    """Return the tickets (if any) used by the user for that party."""
    return Ticket.query \
        .for_party_id(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .join(Seat) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(Seat.coord_x, Seat.coord_y) \
        .all()


def uses_any_ticket_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user uses any ticket for that party."""
    count = Ticket.query \
        .for_party_id(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .count()

    return count > 0


def get_attended_parties(user_id: UserID) -> Sequence[PartyTuple]:
    """Return the parties the user has attended in the past."""
    ticket_attendance_party_ids = _get_attended_party_ids(user_id)
    archived_attendance_party_ids = _get_archived_attendance_party_ids(user_id)

    party_ids = set(chain(ticket_attendance_party_ids,
                          archived_attendance_party_ids))

    return party_service.get_parties(party_ids)


def _get_attended_party_ids(user_id: UserID) -> Set[PartyID]:
    """Return the IDs of the non-legacy parties the user has attended."""
    # Note: Party dates aren't UTC, yet.
    party_id_rows = db.session \
        .query(Party.id) \
        .filter(Party.ends_at < datetime.now()) \
        .join(Category).join(Ticket).filter(Ticket.used_by_id == user_id) \
        .all()

    return _get_first_column_values_as_set(party_id_rows)


def get_ticket_with_details(ticket_id: TicketID) -> Optional[Ticket]:
    """Return the ticket with that id, or `None` if not found."""
    return Ticket.query \
        .options(
            db.joinedload('category'),
            db.joinedload('occupied_seat').joinedload('area'),
            db.joinedload('owned_by'),
            db.joinedload('seat_managed_by'),
            db.joinedload('user_managed_by'),
        ) \
        .get(ticket_id)


def get_tickets_with_details_for_party_paginated(party_id: PartyID, page: int,
                                                 per_page: int) -> Pagination:
    """Return the party's tickets to show on the specified page."""
    return Ticket.query \
        .for_party_id(party_id) \
        .options(
            db.joinedload('category'),
            db.joinedload('owned_by'),
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(Ticket.created_at) \
        .paginate(page, per_page)


def get_ticket_count_by_party_id() -> Dict[PartyID, int]:
    """Return ticket count (including 0) per party, indexed by party ID."""
    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Ticket.id)
        ) \
        .outerjoin(Category) \
        .outerjoin(Ticket) \
        .group_by(Party.id) \
        .all())


def count_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of "sold" (i.e. generated) tickets for that party."""
    return Ticket.query \
        .for_party_id(party_id) \
        .count()


def get_attendees_by_party(party_ids: Set[PartyID]
                          ) -> Dict[PartyID, Set[UserTuple]]:
    """Return the parties' attendees, indexed by party."""
    if not party_ids:
        return {}

    attendee_ids_by_party_id = get_attendee_ids_for_parties(party_ids)

    all_attendee_ids = set(
        chain.from_iterable(attendee_ids_by_party_id.values()))
    all_attendees = user_service.find_users(all_attendee_ids)
    all_attendees_by_id = user_service.index_users_by_id(all_attendees)

    attendees_by_party_id = {}
    for party_id in party_ids:
        attendee_ids = attendee_ids_by_party_id.get(party_id, set())

        attendees = {all_attendees_by_id[attendee_id]
                     for attendee_id in attendee_ids}

        attendees_by_party_id[party_id] = attendees

    return attendees_by_party_id


def get_attendee_ids_for_parties(party_ids: Set[PartyID]
                                ) -> Dict[PartyID, Set[UserID]]:
    """Return the partys' attendee IDs, indexed by party ID."""
    if not party_ids:
        return {}

    ticket_rows = db.session \
        .query(Category.party_id, Ticket.used_by_id) \
        .filter(Category.party_id.in_(party_ids)) \
        .join(Ticket) \
        .filter(Ticket.used_by_id != None) \
        .all()

    archived_attendance_rows = db.session \
        .query(ArchivedAttendance.party_id, ArchivedAttendance.user_id) \
        .filter(ArchivedAttendance.party_id.in_(party_ids)) \
        .all()

    rows = ticket_rows + archived_attendance_rows

    attendee_ids_by_party_id = defaultdict(set)  # type: Dict[PartyID, Set[UserID]]
    for party_id, attendee_id in rows:
        attendee_ids_by_party_id[party_id].add(attendee_id)

    return dict(attendee_ids_by_party_id)


# -------------------------------------------------------------------- #
# ticket bundles


def create_ticket_bundle(category: Category, ticket_quantity: int,
                         owned_by_id: UserID) -> TicketBundle:
    """Create a ticket bundle and the given quantity of tickets."""
    if ticket_quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    bundle = TicketBundle(category.id, ticket_quantity, owned_by_id)
    db.session.add(bundle)

    tickets = list(_build_tickets(category, owned_by_id, ticket_quantity,
                                  bundle=bundle))
    db.session.add_all(tickets)

    db.session.commit()

    return bundle


def delete_ticket_bundle(bundle: TicketBundle) -> None:
    """Delete the ticket bundle and the tickets associated with it."""
    for ticket in bundle.tickets:
        db.session.delete(ticket)

    db.session.delete(bundle)

    db.session.commit()


# -------------------------------------------------------------------- #
# archived attendances


def create_archived_attendance(user_id: UserID, party_id: PartyID
                              ) -> ArchivedAttendance:
    """Create an archived attendance of the user at the party."""
    attendance = ArchivedAttendance(user_id, party_id)

    db.session.add(attendance)
    db.session.commit()

    return attendance


def _get_archived_attendance_party_ids(user_id: UserID) -> Set[PartyID]:
    """Return the IDs of the legacy parties the user has attended."""
    party_id_rows = db.session \
        .query(ArchivedAttendance.party_id) \
        .filter(ArchivedAttendance.user_id == user_id) \
        .all()

    return _get_first_column_values_as_set(party_id_rows)


# -------------------------------------------------------------------- #
# helpers


def _get_first_column_values_as_set(rows: Iterable[Sequence[Any]]) -> Set[Any]:
    """Return the first element of each row as a set."""
    return {row[0] for row in rows}

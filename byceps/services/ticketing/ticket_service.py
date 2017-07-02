"""
byceps.services.ticketing.ticket_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Iterator, Optional, Sequence

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import PartyID, UserID

from ..party.models import Party
from ..seating.models.category import Category, CategoryID
from ..seating.models.seat import Seat, SeatID

from .models.ticket import Ticket, TicketID
from .models.ticket_bundle import TicketBundle


# -------------------------------------------------------------------- #
# creation


def create_ticket(category_id: CategoryID, owned_by_id: UserID
                 ) -> Sequence[Ticket]:
    """Create a single ticket."""
    tickets = create_tickets(category_id, owned_by_id, 1)
    return tickets[0]


def create_tickets(category_id: CategoryID, owned_by_id: UserID, quantity: int
                  ) -> Sequence[Ticket]:
    """Create a number of tickets of the same category for a single owner."""
    tickets = list(build_tickets(category_id, owned_by_id, quantity))

    db.session.add_all(tickets)
    db.session.commit()

    return tickets


def build_tickets(category_id: CategoryID, owned_by_id: UserID, quantity: int,
                  *, bundle: Optional[TicketBundle]=None) -> Iterator[Ticket]:
    if quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    for _ in range(quantity):
        yield Ticket(category_id, owned_by_id, bundle=bundle)


# -------------------------------------------------------------------- #
# lookup


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
        .outerjoin(Seat) \
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


# -------------------------------------------------------------------- #
# user


def appoint_user_manager(ticket_id: TicketID, user_id: UserID):
    """Appoint the user as the ticket's user manager."""
    ticket = find_ticket(ticket_id)

    ticket.user_managed_by_id = user_id

    db.session.commit()


def withdraw_user_manager(ticket_id: TicketID):
    """Withdraw the ticket's custom user manager."""
    ticket = find_ticket(ticket_id)

    ticket.user_managed_by_id = None

    db.session.commit()


def appoint_user(ticket_id: TicketID, user_id: UserID):
    """Appoint the user as the ticket's user."""
    ticket = find_ticket(ticket_id)

    ticket.used_by_id = user_id

    db.session.commit()


def withdraw_user(ticket_id: TicketID):
    """Withdraw the ticket's user."""
    ticket = find_ticket(ticket_id)

    ticket.used_by_id = None

    db.session.commit()


# -------------------------------------------------------------------- #
# seat


def appoint_seat_manager(ticket_id: TicketID, user_id: UserID):
    """Appoint the user as the ticket's seat manager."""
    ticket = find_ticket(ticket_id)

    ticket.seat_managed_by_id = user_id

    db.session.commit()


def withdraw_seat_manager(ticket_id: TicketID):
    """Withdraw the ticket's custom seat manager."""
    ticket = find_ticket(ticket_id)

    ticket.seat_managed_by_id = None

    db.session.commit()


def occupy_seat(ticket_id: TicketID, seat_id: SeatID):
    """Occupy the seat with this ticket."""
    ticket = find_ticket(ticket_id)

    ticket.occupied_seat_id = seat_id

    db.session.commit()


def release_seat(ticket_id: TicketID):
    """Release the seat occupied by this ticket."""
    ticket = find_ticket(ticket_id)

    ticket.occupied_seat_id = None

    db.session.commit()

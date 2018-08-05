"""
byceps.services.ticketing.ticket_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Optional, Sequence, Set

from flask_sqlalchemy import Pagination

from ...database import db
from ...typing import PartyID, UserID

from ..party.models.party import Party
from ..seating.models.seat import Seat
from ..seating import seat_service
from ..seating.transfer.models import SeatID
from ..shop.order.transfer.models import OrderNumber
from ..user.models.user import User

from . import event_service
from .exceptions import SeatChangeDeniedForBundledTicket, \
    SeatChangeDeniedForGroupSeat, TicketCategoryMismatch, TicketIsRevoked
from .models.category import Category
from .models.ticket import Ticket
from .transfer.models import TicketCode, TicketID


# -------------------------------------------------------------------- #
# lookup


def find_ticket(ticket_id: TicketID) -> Optional[Ticket]:
    """Return the ticket with that id, or `None` if not found."""
    return Ticket.query.get(ticket_id)


def find_ticket_by_code(code: TicketCode) -> Optional[Ticket]:
    """Return the ticket with that code, or `None` if not found."""
    return Ticket.query \
        .filter_by(code=code) \
        .one_or_none()


def find_tickets(ticket_ids: Set[TicketID]) -> Sequence[Ticket]:
    """Return the tickets with those ids."""
    return Ticket.query \
        .filter(Ticket.id.in_(ticket_ids)) \
        .all()


def find_tickets_created_by_order(order_number: OrderNumber
                                 ) -> Sequence[Ticket]:
    """Return the tickets created by this order (as it was marked as paid)."""
    return Ticket.query \
        .filter_by(order_number=order_number) \
        .order_by(Ticket.created_at) \
        .all()


def find_tickets_for_seat_manager(user_id: UserID, party_id: PartyID
                                 ) -> Sequence[Ticket]:
    """Return the tickets for that party whose respective seats the user
    is entitled to manage.
    """
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == False) \
        .filter(
            (
                (Ticket.seat_managed_by_id == None) &
                (Ticket.owned_by_id == user_id)
            ) |
            (Ticket.seat_managed_by_id == user_id)
        ) \
        .options(
            db.joinedload('occupied_seat'),
        ) \
        .all()


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
        .for_party(party_id) \
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
        .for_party(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .outerjoin(Seat) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .order_by(Seat.coord_x, Seat.coord_y) \
        .all()


def find_tickets_used_by_user_simplified(user_id: UserID, party_id: PartyID
                                        ) -> Sequence[Ticket]:
    """Return the tickets (if any) used by the user for that party."""
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.used_by_id == user_id) \
        .options(
            db.joinedload('occupied_seat').joinedload('area'),
        ) \
        .all()


def uses_any_ticket_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user uses any ticket for that party."""
    count = Ticket.query \
        .for_party(party_id) \
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
                                                 per_page: int,
                                                 *, search_term=None
                                                ) -> Pagination:
    """Return the party's tickets to show on the specified page."""
    query = Ticket.query \
        .for_party(party_id) \
        .options(
            db.joinedload('category'),
            db.joinedload('owned_by'),
            db.joinedload('occupied_seat').joinedload('area'),
        )

    if search_term:
        ilike_pattern = '%{}%'.format(search_term)
        query = query \
            .filter(Ticket.code.ilike(ilike_pattern))

    return query \
        .order_by(Ticket.created_at) \
        .paginate(page, per_page)


def get_tickets_in_use_for_party_paginated(party_id: PartyID, page: int,
                                           per_page: int,
                                           *, search_term: Optional[str]=None
                                          ) -> Pagination:
    """Return the party's tickets which have a user assigned."""
    ticket_user = db.aliased(User)

    query = Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == False) \
        .filter(Ticket.used_by_id.isnot(None))

    if search_term:
        query = query \
            .filter(ticket_user.screen_name.ilike('%{}%'.format(search_term)))

    return query \
        .join(ticket_user, Ticket.used_by_id == ticket_user.id) \
        .order_by(db.func.lower(ticket_user.screen_name), Ticket.created_at) \
        .paginate(page, per_page)


def get_ticket_count_by_party_id() -> Dict[PartyID, int]:
    """Return ticket count (including 0) per party, indexed by party ID."""
    party = db.aliased(Party)

    subquery = db.session \
        .query(
            db.func.count(Ticket.id)
        ) \
        .join(Category) \
        .join(Party) \
        .filter(Party.id == party.id) \
        .filter(Ticket.revoked == False) \
        .subquery() \
        .as_scalar()

    party_ids_and_ticket_counts = db.session \
        .query(
            party.id,
            subquery
        ) \
        .all()

    return dict(party_ids_and_ticket_counts)


def count_tickets_for_party(party_id: PartyID) -> int:
    """Return the number of "sold" (i.e. generated and not revoked)
    tickets for that party.
    """
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.revoked == False) \
        .count()


def count_tickets_checked_in_for_party(party_id: PartyID) -> int:
    """Return the number tickets for that party that were used to check
    in their respective user.
    """
    return Ticket.query \
        .for_party(party_id) \
        .filter(Ticket.user_checked_in == True) \
        .count()


# -------------------------------------------------------------------- #
# seat


def appoint_seat_manager(ticket_id: TicketID, manager_id: UserID,
                         initiator_id: UserID) -> None:
    """Appoint the user as the ticket's seat manager."""
    ticket = find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    ticket.seat_managed_by_id = manager_id

    event = event_service._build_event('seat-manager-appointed', ticket.id, {
        'appointed_seat_manager_id': str(manager_id),
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def withdraw_seat_manager(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Withdraw the ticket's custom seat manager."""
    ticket = find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    ticket.seat_managed_by_id = None

    event = event_service._build_event('seat-manager-withdrawn', ticket.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def occupy_seat(ticket_id: TicketID, seat_id: SeatID, initiator_id: UserID
               ) -> None:
    """Occupy the seat with this ticket."""
    ticket = find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    _deny_seat_management_if_ticket_belongs_to_bundle(ticket)

    seat = seat_service.find_seat(seat_id)
    if seat is None:
        raise ValueError('Invalid seat ID')

    if seat.category_id != ticket.category_id:
        raise TicketCategoryMismatch(
            'Ticket and seat belong to different categories.')

    _deny_seat_management_if_seat_belongs_to_group(seat)

    previous_seat_id = ticket.occupied_seat_id

    ticket.occupied_seat_id = seat.id

    event_data = {
        'seat_id': str(seat.id),
        'initiator_id': str(initiator_id),
    }
    if previous_seat_id is not None:
        event_data['previous_seat_id'] = str(previous_seat_id)

    event = event_service._build_event('seat-occupied', ticket.id, event_data)
    db.session.add(event)

    db.session.commit()


def release_seat(ticket_id: TicketID, initiator_id: UserID) -> None:
    """Release the seat occupied by this ticket."""
    ticket = find_ticket(ticket_id)

    if ticket.revoked:
        raise TicketIsRevoked('Ticket {} has been revoked.'.format(ticket_id))

    _deny_seat_management_if_ticket_belongs_to_bundle(ticket)

    seat = seat_service.find_seat(ticket.occupied_seat_id)
    if seat is None:
        raise ValueError('Ticket does not occupy a seat.')

    _deny_seat_management_if_seat_belongs_to_group(seat)

    ticket.occupied_seat_id = None

    event = event_service._build_event('seat-released', ticket.id, {
        'initiator_id': str(initiator_id),
    })
    db.session.add(event)

    db.session.commit()


def _deny_seat_management_if_ticket_belongs_to_bundle(ticket: Ticket) -> None:
    """Raise an exception if this ticket belongs to a bundle.

    A ticket bundle is meant to occupy a matching seat group with the
    appropriate mechanism, not to separately occupy single seats.
    """
    if ticket.belongs_to_bundle:
        raise SeatChangeDeniedForBundledTicket(
            "Ticket '{}' belongs to a bundle and, thus, "
            'must not be used to occupy or release a single seat.'
            .format(ticket.code))


def _deny_seat_management_if_seat_belongs_to_group(seat: Seat) -> None:
    if seat.assignment is not None:
        raise SeatChangeDeniedForGroupSeat(
            "Seat '{}' belongs to a group and, thus, "
            'cannot be occupied by a single ticket, or removed separately.'
            .format(seat.label))

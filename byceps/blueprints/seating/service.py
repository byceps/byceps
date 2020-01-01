"""
byceps.blueprints.seating.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, Iterator, Sequence

from ...services.seating.models.seat import Seat
from ...services.ticketing.models.ticket import Ticket as DbTicket
from ...services.user import service as user_service
from ...services.user.transfer.models import User
from ...typing import UserID


def get_users(
    seats: Sequence[Seat], managed_tickets: Sequence[DbTicket]
) -> Dict[UserID, User]:
    user_ids = set()
    user_ids.extend(_get_seat_occupier_ids(seats))
    user_ids.extend(_get_ticket_user_ids(managed_tickets))

    users = user_service.find_users(user_ids, include_avatars=True)
    return user_service.index_users_by_id(users)


def _get_seat_occupier_ids(seats: Sequence[Seat]) -> Iterator[UserID]:
    tickets = _get_seat_tickets(seats)
    yield from _get_ticket_user_ids(tickets)


def _get_seat_tickets(seats: Sequence[Seat]) -> Iterator[DbTicket]:
    for seat in seats:
        if seat.has_user:
            yield seat.occupied_by_ticket


def _get_ticket_user_ids(tickets: Sequence[DbTicket]) -> Iterator[UserID]:
    for ticket in tickets:
        user_id = ticket.used_by_id
        if user_id is not None:
            yield user_id

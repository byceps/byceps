"""
byceps.blueprints.attendance.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
"""

from collections import namedtuple
from typing import Dict, Iterator, Sequence

from ...services.seating.models.seat import Seat, SeatID
from ...services.seating import seat_service
from ...services.ticketing.models.ticket import Ticket
from ...services.user.models.user import User
from ...services.user import service as user_service
from ...typing import UserID


Attendee = namedtuple('Attendee', ['user', 'seat'])


def get_attendees(tickets: Sequence[Ticket]) -> Iterator[Attendee]:
    users_by_id = _get_users_by_id(tickets)
    seats_by_id = _get_seats_by_id(tickets)

    for t in tickets:
        yield Attendee(
            users_by_id[t.used_by_id],
            seats_by_id.get(t.occupied_seat_id),
        )


def _get_users_by_id(tickets) -> Dict[UserID, User]:
    user_ids = {t.used_by_id for t in tickets}
    users = user_service.find_users(user_ids)
    return {user.id: user for user in users}


def _get_seats_by_id(tickets) -> Dict[SeatID, Seat]:
    seat_ids = {t.occupied_seat_id for t in tickets}
    seats = seat_service.find_seats(seat_ids)
    return {seat.id: seat for seat in seats}

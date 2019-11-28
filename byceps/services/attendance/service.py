"""
byceps.services.attendance.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
"""

from typing import Dict, List, Sequence

from ...services.seating.models.seat import Seat
from ...services.seating import seat_service
from ...services.seating.transfer.models import SeatID
from ...services.ticketing.models.ticket import Ticket
from ...services.user.models.user import User
from ...services.user import service as user_service
from ...typing import UserID

from .transfer.models import Attendee


def get_attendees(tickets: Sequence[Ticket]) -> List[Attendee]:
    users_by_id = _get_users_by_id(tickets)
    seats_by_id = _get_seats_by_id(tickets)

    def to_attendee(ticket: Ticket):
        user = users_by_id[ticket.used_by_id]
        seat = seats_by_id.get(ticket.occupied_seat_id)
        checked_in = ticket.user_checked_in

        return Attendee(user, seat, checked_in)

    return [to_attendee(t) for t in tickets]


def _get_users_by_id(tickets: Sequence[Ticket]) -> Dict[UserID, User]:
    user_ids = {t.used_by_id for t in tickets}
    users = user_service.find_users(user_ids, include_avatars=True)
    return {user.id: user for user in users}


def _get_seats_by_id(tickets: Sequence[Ticket]) -> Dict[SeatID, Seat]:
    seat_ids = {t.occupied_seat_id for t in tickets}
    seats = seat_service.find_seats(seat_ids)
    return {seat.id: seat for seat in seats}

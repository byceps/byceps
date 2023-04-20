"""
byceps.services.seating.seating_area_tickets_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Iterator, Optional

from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketCode, TicketID
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID

from .models import Seat


@dataclass(frozen=True)
class SeatTicket:
    id: TicketID
    code: TicketCode
    category_label: str
    user: Optional[User]


def get_users(
    seats_with_tickets: Iterable[tuple[Seat, DbTicket]],
    managed_tickets: Iterable[DbTicket],
) -> dict[UserID, User]:
    seat_tickets = _get_seat_tickets(seats_with_tickets)
    tickets = chain(seat_tickets, managed_tickets)

    return _get_ticket_users_by_id(tickets)


def _get_seat_tickets(
    seats_with_tickets: Iterable[tuple[Seat, DbTicket]]
) -> Iterator[DbTicket]:
    for seat, ticket in seats_with_tickets:
        if (ticket is not None) and (ticket.used_by_id is not None):
            yield ticket


def _get_ticket_users_by_id(tickets: Iterable[DbTicket]) -> dict[UserID, User]:
    user_ids = set(_get_ticket_user_ids(tickets))
    users = user_service.get_users(user_ids, include_avatars=True)
    return user_service.index_users_by_id(users)


def _get_ticket_user_ids(tickets: Iterable[DbTicket]) -> Iterator[UserID]:
    for ticket in tickets:
        user_id = ticket.used_by_id
        if user_id is not None:
            yield user_id


def get_seats_and_tickets(
    seats_with_tickets: Iterable[tuple[Seat, DbTicket]],
    users_by_id: dict[UserID, User],
) -> Iterator[tuple[Seat, Optional[SeatTicket]]]:
    for seat, ticket in seats_with_tickets:
        if ticket is not None:
            seat_ticket = _build_seat_ticket(ticket, users_by_id)
        else:
            seat_ticket = None

        yield seat, seat_ticket


def get_managed_tickets(
    tickets: Iterable[DbTicket], users_by_id: dict[UserID, User]
) -> Iterator[tuple[SeatTicket, bool, Optional[str]]]:
    for ticket in tickets:
        managed_ticket = _build_seat_ticket(ticket, users_by_id)
        occupies_seat = ticket.occupied_seat_id is not None
        seat_label = ticket.occupied_seat.label if occupies_seat else None

        yield managed_ticket, occupies_seat, seat_label


def _build_seat_ticket(
    ticket: DbTicket, users_by_id: dict[UserID, User]
) -> SeatTicket:
    user: Optional[User]
    if ticket.used_by_id is not None:
        user = users_by_id[ticket.used_by_id]
    else:
        user = None

    return SeatTicket(
        id=ticket.id,
        code=ticket.code,
        category_label=ticket.category.title,
        user=user,
    )

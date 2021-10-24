"""
byceps.blueprints.site.seating.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Iterator, Optional

from ....services.seating.dbmodels.seat import Seat as DbSeat
from ....services.seating.transfer.models import Seat
from ....services.ticketing.dbmodels.ticket import Ticket as DbTicket
from ....services.ticketing.transfer.models import TicketCode, TicketID
from ....services.user import service as user_service
from ....services.user.transfer.models import User
from ....typing import UserID


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
        seat_ticket = _get_seat_ticket(ticket, users_by_id)
        yield seat, seat_ticket


def _get_seat_ticket(
    ticket: Optional[DbTicket], users_by_id: dict[UserID, User]
) -> Optional[SeatTicket]:
    if ticket is None:
        return None

    user = _find_ticket_user(ticket, users_by_id)

    return SeatTicket(
        id=ticket.id,
        code=ticket.code,
        category_label=ticket.category.title,
        user=user,
    )


def get_managed_tickets(
    tickets: Iterable[DbTicket], users_by_id: dict[UserID, User]
) -> Iterator[tuple[SeatTicket, bool, Optional[str]]]:
    for ticket in tickets:
        user = _find_ticket_user(ticket, users_by_id)

        managed_ticket = SeatTicket(
            id=ticket.id,
            code=ticket.code,
            category_label=ticket.category.title,
            user=user,
        )

        occupies_seat = ticket.occupied_seat_id is not None

        seat_label = ticket.occupied_seat.label if occupies_seat else None

        yield managed_ticket, occupies_seat, seat_label


def _find_ticket_user(
    ticket: DbTicket, users_by_id: dict[UserID, User]
) -> Optional[User]:
    if ticket.used_by_id is None:
        return None

    return users_by_id[ticket.used_by_id]

"""
byceps.services.seating.seating_area_tickets_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import chain

from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketCode, TicketID
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from .models import Seat


@dataclass(frozen=True)
class SeatTicket:
    id: TicketID
    user: User | None


@dataclass(frozen=True)
class ManagedTicket:
    id: TicketID
    code: TicketCode
    category_label: str
    user: User | None


def get_users(
    seats_with_tickets: Iterable[tuple[Seat, DbTicket]],
    managed_tickets: Iterable[DbTicket],
) -> dict[UserID, User]:
    seat_tickets = _get_seat_tickets(seats_with_tickets)
    tickets = chain(seat_tickets, managed_tickets)
    user_ids = set(_get_ticket_user_ids(tickets))
    return user_service.get_users_indexed_by_id(user_ids, include_avatars=True)


def _get_seat_tickets(
    seats_with_tickets: Iterable[tuple[Seat, DbTicket]],
) -> Iterator[DbTicket]:
    for _, ticket in seats_with_tickets:
        if (ticket is not None) and (ticket.used_by_id is not None):
            yield ticket


def _get_ticket_user_ids(tickets: Iterable[DbTicket]) -> Iterator[UserID]:
    for ticket in tickets:
        user_id = ticket.used_by_id
        if user_id is not None:
            yield user_id


def get_seats_and_tickets(
    seats_with_tickets: Iterable[tuple[Seat, DbTicket]],
    users_by_id: dict[UserID, User],
) -> Iterator[tuple[Seat, SeatTicket | None]]:
    for seat, ticket in seats_with_tickets:
        if ticket is not None:
            seat_ticket = _build_seat_ticket(ticket, users_by_id)
        else:
            seat_ticket = None

        yield seat, seat_ticket


def _build_seat_ticket(
    ticket: DbTicket, users_by_id: dict[UserID, User]
) -> SeatTicket:
    user: User | None
    if ticket.used_by_id is not None:
        user = users_by_id[ticket.used_by_id]
    else:
        user = None

    return SeatTicket(
        id=ticket.id,
        user=user,
    )


def get_managed_tickets(
    tickets: Iterable[DbTicket], users_by_id: dict[UserID, User]
) -> Iterator[tuple[ManagedTicket, bool, str | None]]:
    for ticket in tickets:
        managed_ticket = _build_managed_ticket(ticket, users_by_id)
        occupies_seat = ticket.occupied_seat is not None
        seat_label = (
            ticket.occupied_seat.label
            if (ticket.occupied_seat is not None)
            else None
        )

        yield managed_ticket, occupies_seat, seat_label


def _build_managed_ticket(
    ticket: DbTicket, users_by_id: dict[UserID, User]
) -> ManagedTicket:
    user: User | None
    if ticket.used_by_id is not None:
        user = users_by_id[ticket.used_by_id]
    else:
        user = None

    return ManagedTicket(
        id=ticket.id,
        code=TicketCode(ticket.code),
        category_label=ticket.category.title,
        user=user,
    )

"""
byceps.services.seating.seating_area_tickets_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

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
    occupies_seat: bool
    seat_label: str | None
    user: User | None


def get_users(
    seats_with_db_tickets: Iterable[tuple[Seat, DbTicket]],
) -> dict[UserID, User]:
    db_tickets = _get_seat_tickets(seats_with_db_tickets)
    user_ids = set(_get_ticket_user_ids(db_tickets))
    return user_service.get_users_indexed_by_id(user_ids, include_avatars=True)


def _get_seat_tickets(
    seats_with_db_tickets: Iterable[tuple[Seat, DbTicket]],
) -> Iterator[DbTicket]:
    for _, db_ticket in seats_with_db_tickets:
        if (db_ticket is not None) and (db_ticket.used_by_id is not None):
            yield db_ticket


def _get_ticket_user_ids(db_tickets: Iterable[DbTicket]) -> Iterator[UserID]:
    for db_ticket in db_tickets:
        user_id = db_ticket.used_by_id
        if user_id is not None:
            yield user_id


def get_seats_and_tickets(
    seats_with_db_tickets: Iterable[tuple[Seat, DbTicket]],
    users_by_id: dict[UserID, User],
) -> Iterator[tuple[Seat, SeatTicket | None]]:
    for seat, db_ticket in seats_with_db_tickets:
        if db_ticket is not None:
            seat_ticket = _build_seat_ticket(db_ticket, users_by_id)
        else:
            seat_ticket = None

        yield seat, seat_ticket


def _build_seat_ticket(
    db_ticket: DbTicket, users_by_id: dict[UserID, User]
) -> SeatTicket:
    user: User | None
    if db_ticket.used_by_id is not None:
        user = users_by_id[db_ticket.used_by_id]
    else:
        user = None

    return SeatTicket(
        id=db_ticket.id,
        user=user,
    )


def get_managed_tickets(
    db_tickets: Iterable[DbTicket],
) -> Iterator[ManagedTicket]:
    user_ids = {
        db_ticket.used_by_id for db_ticket in db_tickets if db_ticket.used_by_id
    }

    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=False
    )

    for db_ticket in db_tickets:
        yield _build_managed_ticket(db_ticket, users_by_id)


def _build_managed_ticket(
    db_ticket: DbTicket, users_by_id: dict[UserID, User]
) -> ManagedTicket:
    occupies_seat = db_ticket.occupied_seat is not None

    seat_label = (
        db_ticket.occupied_seat.label
        if (db_ticket.occupied_seat is not None)
        else None
    )

    user: User | None
    if db_ticket.used_by_id is not None:
        user = users_by_id[db_ticket.used_by_id]
    else:
        user = None

    return ManagedTicket(
        id=db_ticket.id,
        code=TicketCode(db_ticket.code),
        category_label=db_ticket.category.title,
        occupies_seat=occupies_seat,
        seat_label=seat_label,
        user=user,
    )

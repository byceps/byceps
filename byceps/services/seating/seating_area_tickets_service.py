"""
byceps.services.seating.seating_area_tickets_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable

from byceps.services.party.models import PartyID
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import TicketCode
from byceps.services.user import user_service
from byceps.services.user.models.user import User, UserID

from .models import ManagedTicket


def get_managed_tickets(
    seat_manager_id: UserID, party_id: PartyID
) -> list[ManagedTicket]:
    db_tickets = ticket_service.get_tickets_for_seat_manager(
        seat_manager_id, party_id
    )

    users_by_id = _get_ticket_users_by_id(db_tickets, include_avatars=False)

    return [
        _build_managed_ticket(db_ticket, users_by_id)
        for db_ticket in db_tickets
    ]


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


def _get_ticket_users_by_id(
    db_tickets: Iterable[DbTicket], *, include_avatars: bool
) -> dict[UserID, User]:
    user_ids = {
        db_ticket.used_by_id for db_ticket in db_tickets if db_ticket.used_by_id
    }

    return user_service.get_users_indexed_by_id(
        user_ids, include_avatars=include_avatars
    )

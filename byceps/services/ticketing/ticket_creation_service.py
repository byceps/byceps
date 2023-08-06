"""
byceps.services.ticketing.ticket_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.exc import IntegrityError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from byceps.database import db
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.user.models.user import User
from byceps.typing import PartyID

from . import ticket_code_service
from .dbmodels.ticket import DbTicket
from .dbmodels.ticket_bundle import DbTicketBundle
from .models.ticket import TicketCategoryID


class TicketCreationFailedError(Exception):
    """Ticket creation failed for some reason."""


class TicketCreationFailedWithConflictError(TicketCreationFailedError):
    """Ticket creation failed because of a conflict with an existing,
    persisted ticket.
    """


def create_ticket(
    party_id: PartyID,
    category_id: TicketCategoryID,
    owner: User,
    *,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> DbTicket:
    """Create a single ticket."""
    quantity = 1

    db_tickets = create_tickets(
        party_id,
        category_id,
        owner,
        quantity,
        order_number=order_number,
        user=user,
    )

    return db_tickets[0]


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailedError),
    stop=stop_after_attempt(5),
)
def create_tickets(
    party_id: PartyID,
    category_id: TicketCategoryID,
    owner: User,
    quantity: int,
    *,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> list[DbTicket]:
    """Create a number of tickets of the same category for a single owner."""
    db_tickets = list(
        build_tickets(
            party_id,
            category_id,
            owner,
            quantity,
            order_number=order_number,
            user=user,
        )
    )

    db.session.add_all(db_tickets)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise TicketCreationFailedWithConflictError(exc) from exc

    return db_tickets


def build_tickets(
    party_id: PartyID,
    category_id: TicketCategoryID,
    owner: User,
    quantity: int,
    *,
    bundle: DbTicketBundle | None = None,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> Iterator[DbTicket]:
    if quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    try:
        codes = ticket_code_service.generate_ticket_codes(quantity)
    except ticket_code_service.TicketCodeGenerationFailedError as exc:
        raise TicketCreationFailedError(exc) from exc

    for code in codes:
        yield DbTicket(
            party_id,
            code,
            category_id,
            owner.id,
            bundle=bundle,
            order_number=order_number,
            used_by_id=user.id if user else None,
        )

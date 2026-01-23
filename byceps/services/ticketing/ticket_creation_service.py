"""
byceps.services.ticketing.ticket_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from byceps.database import db
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.ticketing.models.ticket import TicketID
from byceps.services.user.models import User
from byceps.util.result import Err, Ok
from byceps.util.uuid import generate_uuid7

from . import ticket_code_service
from .dbmodels.ticket import DbTicket
from .models.ticket import TicketBundleID, TicketCategory


class TicketCreationFailedError(Exception):
    """Ticket creation failed for some reason."""


class TicketCreationFailedWithConflictError(TicketCreationFailedError):
    """Ticket creation failed because of a conflict with an existing,
    persisted ticket.
    """


def create_ticket(
    category: TicketCategory,
    owner: User,
    *,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> DbTicket:
    """Create a single ticket."""
    quantity = 1

    db_tickets = create_tickets(
        category, owner, quantity, order_number=order_number, user=user
    )

    return db_tickets[0]


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailedError),
    stop=stop_after_attempt(5),
)
def create_tickets(
    category: TicketCategory,
    owner: User,
    quantity: int,
    *,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> list[DbTicket]:
    """Create a number of tickets of the same category for a single owner."""
    db_tickets = list(
        build_tickets(
            category, owner, quantity, order_number=order_number, user=user
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
    category: TicketCategory,
    owner: User,
    quantity: int,
    *,
    bundle_id: TicketBundleID | None = None,
    order_number: OrderNumber | None = None,
    user: User | None = None,
) -> Iterator[DbTicket]:
    if quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    created_at = datetime.utcnow()

    match ticket_code_service.generate_ticket_codes(quantity):
        case Ok(codes):
            for code in codes:
                ticket_id = TicketID(generate_uuid7())

                yield DbTicket(
                    ticket_id,
                    created_at,
                    category,
                    code,
                    owner.id,
                    bundle_id=bundle_id,
                    order_number=order_number,
                    used_by_id=user.id if user else None,
                )
        case Err(e):
            raise TicketCreationFailedError(e)

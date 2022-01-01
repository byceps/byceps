"""
byceps.services.ticketing.ticket_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator, Optional, Sequence

from sqlalchemy.exc import IntegrityError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from ...database import db
from ...typing import PartyID, UserID

from ..shop.order.transfer.number import OrderNumber

from .dbmodels.ticket import Ticket as DbTicket
from .dbmodels.ticket_bundle import TicketBundle as DbTicketBundle
from . import ticket_code_service
from .transfer.models import TicketCategoryID


class TicketCreationFailed(Exception):
    """Ticket creation failed for some reason."""


class TicketCreationFailedWithConflict(TicketCreationFailed):
    """Ticket creation failed because of a conflict with an existing,
    persisted ticket.
    """


def create_ticket(
    party_id: PartyID,
    category_id: TicketCategoryID,
    owned_by_id: UserID,
    *,
    order_number: Optional[OrderNumber] = None,
    used_by_id: Optional[UserID] = None,
) -> DbTicket:
    """Create a single ticket."""
    quantity = 1
    tickets = create_tickets(
        party_id,
        category_id,
        owned_by_id,
        quantity,
        order_number=order_number,
        used_by_id=used_by_id,
    )
    return tickets[0]


@retry(
    reraise=True,
    retry=retry_if_exception_type(TicketCreationFailed),
    stop=stop_after_attempt(5),
)
def create_tickets(
    party_id: PartyID,
    category_id: TicketCategoryID,
    owned_by_id: UserID,
    quantity: int,
    *,
    order_number: Optional[OrderNumber] = None,
    used_by_id: Optional[UserID] = None,
) -> Sequence[DbTicket]:
    """Create a number of tickets of the same category for a single owner."""
    tickets = list(
        build_tickets(
            party_id,
            category_id,
            owned_by_id,
            quantity,
            order_number=order_number,
            used_by_id=used_by_id,
        )
    )

    db.session.add_all(tickets)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise TicketCreationFailedWithConflict(e)

    return tickets


def build_tickets(
    party_id: PartyID,
    category_id: TicketCategoryID,
    owned_by_id: UserID,
    quantity: int,
    *,
    bundle: Optional[DbTicketBundle] = None,
    order_number: Optional[OrderNumber] = None,
    used_by_id: Optional[UserID] = None,
) -> Iterator[DbTicket]:
    if quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    try:
        codes = ticket_code_service.generate_ticket_codes(quantity)
    except ticket_code_service.TicketCodeGenerationFailed as e:
        raise TicketCreationFailed(e)

    for code in codes:
        yield DbTicket(
            party_id,
            code,
            category_id,
            owned_by_id,
            bundle=bundle,
            order_number=order_number,
            used_by_id=used_by_id,
        )

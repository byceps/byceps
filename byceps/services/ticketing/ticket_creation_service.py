"""
byceps.services.ticketing.ticket_creation_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from random import sample
from typing import Iterator, Optional, Sequence, Set

from ...database import db
from ...typing import UserID

from ..shop.order.transfer.models import OrderNumber

from .models.ticket import Ticket as DbTicket
from .models.ticket_bundle import TicketBundle as DbTicketBundle
from .transfer.models import TicketCategoryID, TicketCode


def create_ticket(
    category_id: TicketCategoryID,
    owned_by_id: UserID,
    *,
    order_number: Optional[OrderNumber] = None,
) -> DbTicket:
    """Create a single ticket."""
    tickets = create_tickets(
        category_id, owned_by_id, 1, order_number=order_number
    )
    return tickets[0]


def create_tickets(
    category_id: TicketCategoryID,
    owned_by_id: UserID,
    quantity: int,
    *,
    order_number: Optional[OrderNumber] = None,
) -> Sequence[DbTicket]:
    """Create a number of tickets of the same category for a single owner."""
    tickets = list(
        build_tickets(
            category_id, owned_by_id, quantity, order_number=order_number
        )
    )

    db.session.add_all(tickets)
    db.session.commit()

    return tickets


def build_tickets(
    category_id: TicketCategoryID,
    owned_by_id: UserID,
    quantity: int,
    *,
    bundle: Optional[DbTicketBundle] = None,
    order_number: Optional[OrderNumber] = None,
) -> Iterator[DbTicket]:
    if quantity < 1:
        raise ValueError('Ticket quantity must be positive.')

    codes: Set[TicketCode] = set()

    for _ in range(quantity):
        code = _generate_ticket_code_not_in(codes)
        codes.add(code)

        yield DbTicket(
            code,
            category_id,
            owned_by_id,
            bundle=bundle,
            order_number=order_number,
        )


_CODE_ALPHABET = 'BCDFGHJKLMNPQRSTVWXYZ'
_CODE_LENGTH = 5


def _generate_ticket_code() -> TicketCode:
    """Generate a ticket code.

    Generated codes are not necessarily unique!
    """
    return TicketCode(''.join(sample(_CODE_ALPHABET, _CODE_LENGTH)))


def _generate_ticket_code_not_in(codes: Set[TicketCode]) -> TicketCode:
    """Generate ticket codes and return the first one not in the set."""
    while True:
        code = _generate_ticket_code()
        if code not in codes:
            return code

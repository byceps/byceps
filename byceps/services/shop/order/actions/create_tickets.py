"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..transfer.action import ActionParameters
from ..transfer.order import Order

from . import ticket


def create_tickets(
    order: Order,
    ticket_quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Create tickets."""
    ticket_category_id = parameters['category_id']

    ticket.create_tickets(
        order, ticket_category_id, ticket_quantity, initiator_id
    )

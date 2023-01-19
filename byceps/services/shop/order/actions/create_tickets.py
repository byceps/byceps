"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..models.action import ActionParameters
from ..models.order import LineItem, Order

from . import ticket


def create_tickets(
    order: Order,
    line_item: LineItem,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Create tickets."""
    ticket_category_id = parameters['category_id']

    ticket.create_tickets(order, line_item, ticket_category_id, initiator_id)

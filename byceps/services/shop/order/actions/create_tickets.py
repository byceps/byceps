"""
byceps.services.shop.order.actions.create_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import LineItem, Order
from byceps.services.user.models.user import User

from . import ticket


def create_tickets(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> None:
    """Create tickets."""
    ticket_category_id = parameters['category_id']

    ticket.create_tickets(order, line_item, ticket_category_id, initiator)

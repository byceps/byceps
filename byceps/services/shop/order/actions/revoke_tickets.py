"""
byceps.services.shop.order.actions.revoke_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import LineItem, Order
from byceps.services.user.models.user import User
from byceps.util.result import Ok, Result

from . import ticket


def on_cancellation_after_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Revoke all tickets in the order."""
    ticket.revoke_tickets(order, line_item, initiator)

    return Ok(None)

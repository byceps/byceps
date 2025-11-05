"""
byceps.services.shop.order.actions.revoke_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import LineItem, Order
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import ticket_bundle


def on_cancellation_after_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Revoke all ticket bundles in this order."""
    match ticket_bundle.revoke_ticket_bundles(order, line_item, initiator):
        case Ok(_):
            return Ok(None)
        case Err(e):
            return Err(OrderActionFailedError(e))

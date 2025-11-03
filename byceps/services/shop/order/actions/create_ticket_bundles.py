"""
byceps.services.shop.order.actions.create_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import LineItem, Order
from byceps.services.user.models.user import User
from byceps.util.result import Ok, Result

from . import ticket_bundle


def on_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Create ticket bundles."""
    ticket_category_id = parameters['category_id']
    ticket_quantity_per_bundle = parameters['ticket_quantity']

    ticket_bundle.create_ticket_bundles(
        order,
        line_item,
        ticket_category_id,
        ticket_quantity_per_bundle,
        initiator,
    )

    return Ok(None)

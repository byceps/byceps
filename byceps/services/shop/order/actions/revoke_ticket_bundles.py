"""
byceps.services.shop.order.actions.revoke_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import LineItem, Order
from byceps.services.user.models.user import User

from . import ticket_bundle


def revoke_ticket_bundles(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> None:
    """Revoke all ticket bundles in this order."""
    ticket_bundle.revoke_ticket_bundles(order, line_item, initiator)

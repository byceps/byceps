"""
byceps.services.shop.order.actions.revoke_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..transfer.action import ActionParameters
from ..transfer.order import LineItemID, Order

from . import ticket_bundle


def revoke_ticket_bundles(
    order: Order,
    line_item_id: LineItemID,
    bundle_quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Revoke all ticket bundles in this order."""
    ticket_bundle.revoke_ticket_bundles(order, line_item_id, initiator_id)

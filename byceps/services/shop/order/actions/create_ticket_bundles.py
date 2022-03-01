"""
byceps.services.shop.order.actions.create_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..transfer.action import ActionParameters
from ..transfer.order import LineItemID, Order

from . import ticket_bundle


def create_ticket_bundles(
    order: Order,
    line_item_id: LineItemID,
    bundle_quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Create ticket bundles."""
    ticket_category_id = parameters['category_id']
    ticket_quantity_per_bundle = parameters['ticket_quantity']

    ticket_bundle.create_ticket_bundles(
        order,
        line_item_id,
        ticket_category_id,
        ticket_quantity_per_bundle,
        bundle_quantity,
        initiator_id,
    )

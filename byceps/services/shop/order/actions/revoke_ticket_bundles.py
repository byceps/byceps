"""
byceps.services.shop.order.actions.revoke_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..transfer.action import ActionParameters
from ..transfer.order import Order

from . import ticket


def revoke_ticket_bundles(
    order: Order,
    bundle_quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Revoke all ticket bundles in this order."""
    ticket.revoke_ticket_bundles(order, initiator_id)

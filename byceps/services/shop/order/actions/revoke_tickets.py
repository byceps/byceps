"""
byceps.services.shop.order.actions.revoke_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..models.action import ActionParameters
from ..models.order import LineItem, Order

from . import ticket


def revoke_tickets(
    order: Order,
    line_item: LineItem,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Revoke all tickets in the order."""
    ticket.revoke_tickets(order, line_item, initiator_id)

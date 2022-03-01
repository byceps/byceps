"""
byceps.services.shop.order.actions.revoke_tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ..transfer.action import ActionParameters
from ..transfer.order import Order

from . import ticket


def revoke_tickets(
    order: Order,
    quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Revoke all tickets in the order."""
    ticket.revoke_tickets(order, initiator_id)

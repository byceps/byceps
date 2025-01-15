"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from byceps.events.shop import ShopOrderPaidEvent
from byceps.services.shop.order import order_command_service
from byceps.services.shop.order.models.order import Order, OrderID
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.user.models.user import User


def get_tickets_for_order(order: Order) -> Sequence[DbTicket]:
    return ticket_service.get_tickets_created_by_order(order.order_number)


def mark_order_as_paid(order_id: OrderID, admin: User) -> ShopOrderPaidEvent:
    _, event = order_command_service.mark_order_as_paid(
        order_id, 'bank_transfer', admin
    ).unwrap()

    return event

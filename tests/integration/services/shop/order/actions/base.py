"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.transfer.models import PaymentMethod
from byceps.services.shop.order import service as order_service
from byceps.services.ticketing import ticket_service


def get_tickets_for_order(order):
    return ticket_service.find_tickets_created_by_order(order.order_number)


def place_order(storefront_id, orderer, articles_with_quantity):
    cart = Cart()
    for article, quantity in articles_with_quantity:
        cart.add_item(article, quantity)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order


def mark_order_as_paid(order_id, admin_id):
    order_service.mark_order_as_paid(
        order_id, PaymentMethod.bank_transfer, admin_id
    )

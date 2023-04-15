"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.events.shop import ShopOrderPaid
from byceps.services.shop.article.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Order, Orderer, OrderID
from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing import ticket_service
from byceps.typing import UserID


def get_tickets_for_order(order: Order) -> list[DbTicket]:
    return ticket_service.get_tickets_created_by_order(order.order_number)


def place_order(
    storefront_id: StorefrontID,
    orderer: Orderer,
    articles_with_quantity: list[tuple[Article, int]],
) -> Order:
    cart = Cart(EUR)
    for article, quantity in articles_with_quantity:
        cart.add_item(article, quantity)

    order, _ = order_checkout_service.place_order(storefront_id, orderer, cart)

    return order


def mark_order_as_paid(order_id: OrderID, admin_id: UserID) -> ShopOrderPaid:
    return order_service.mark_order_as_paid(order_id, 'bank_transfer', admin_id)

"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.events.shop import ShopOrderPaidEvent
from byceps.services.shop.article.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.order.models.order import Order, Orderer, OrderID
from byceps.services.shop.storefront.models import Storefront
from byceps.services.ticketing import ticket_service
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.user.models.user import User


def get_tickets_for_order(order: Order) -> list[DbTicket]:
    return ticket_service.get_tickets_created_by_order(order.order_number)


def place_order(
    storefront: Storefront,
    orderer: Orderer,
    articles_with_quantity: list[tuple[Article, int]],
) -> Order:
    cart = Cart(EUR)
    for article, quantity in articles_with_quantity:
        cart.add_item(article, quantity)

    order, _ = order_checkout_service.place_order(
        storefront, orderer, cart
    ).unwrap()

    return order


def mark_order_as_paid(order_id: OrderID, admin: User) -> ShopOrderPaidEvent:
    _, event = order_service.mark_order_as_paid(
        order_id, 'bank_transfer', admin
    ).unwrap()

    return event

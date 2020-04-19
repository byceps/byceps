"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service

from testfixtures.shop_order import create_orderer


def place_order_with_items(
    shop_id, user, created_at=None, items_with_quantity=None
):
    orderer = create_orderer(user)

    cart = Cart()

    if items_with_quantity is not None:
        for article, quantity in items_with_quantity:
            cart.add_item(article, quantity)

    order, _ = order_service.place_order(
        shop_id, orderer, cart, created_at=created_at
    )

    return order

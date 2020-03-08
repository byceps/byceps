"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service

from testfixtures.shop_order import create_orderer

from tests.base import AbstractAppTestCase
from tests.helpers import create_user


class OrderEmailTestBase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.admin = create_user('Admin')


def place_order_with_items(shop_id, orderer, created_at, items_with_quantity):
    orderer = create_orderer(orderer)
    cart = Cart()

    if items_with_quantity is not None:
        for article, quantity in items_with_quantity:
            cart.add_item(article, quantity)

    order, _ = order_service.place_order(
        shop_id, orderer, cart, created_at=created_at
    )

    return order.id

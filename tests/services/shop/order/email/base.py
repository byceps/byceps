"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order import service as order_service

from testfixtures.shop_order import create_orderer

from tests.helpers import create_user
from tests.services.shop.base import ShopTestBase
from tests.services.shop.helpers import create_article


class OrderEmailTestBase(ShopTestBase):

    def setUp(self):
        super().setUp()

        self.admin = create_user('Admin')

    # helpers

    def create_article(
        self, shop_id, item_number, description, price, quantity
    ):
        return create_article(
            shop_id,
            item_number=item_number,
            description=description,
            price=price,
            quantity=quantity,
        )

    def place_order_with_items(
        self, shop_id, orderer, created_at, items_with_quantity
    ):
        orderer = create_orderer(orderer)
        cart = Cart()

        if items_with_quantity is not None:
            for article, quantity in items_with_quantity:
                cart.add_item(article, quantity)

        order, _ = order_service.place_order(self.shop.id, orderer, cart)

        if created_at is not None:
            db_order = Order.query.get(order.id)
            db_order.created_at = created_at
            self.db.session.commit()

        return order.id

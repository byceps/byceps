"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from testfixtures.shop_order import create_order, create_order_item

from tests.services.shop.base import ShopTestBase


class OrderEmailTestBase(ShopTestBase):

    def setUp(self):
        super().setUp()

        self.admin = self.create_user('Admin')

    # helpers

    def create_article(self, shop_id, item_number, description, price,
                       quantity):
        return super().create_article(shop_id, item_number=item_number,
                                      description=description, price=price,
                                      quantity=quantity)

    def place_order_with_items(self, shop_id, orderer, order_number,
                               created_at, items_with_quantity):
        order = create_order(shop_id, orderer, order_number=order_number)

        if created_at is not None:
            order.created_at = created_at

        if items_with_quantity is not None:
            for article, quantity in items_with_quantity:
                create_order_item(order, article, quantity)

        self.db.session.add(order)
        self.db.session.commit()

        return order

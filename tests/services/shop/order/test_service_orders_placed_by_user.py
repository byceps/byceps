"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service

from testfixtures.shop_order import create_orderer

from tests.base import AbstractAppTestCase
from tests.helpers import create_email_config, create_user_with_detail
from tests.services.shop.helpers import create_shop


class ShopOrdersServiceTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()

        self.shop1_id = create_shop('shop-1').id
        self.shop2_id = create_shop('shop-2').id

        sequence_service.create_order_number_sequence(self.shop1_id, 'LF-02-B')
        sequence_service.create_order_number_sequence(self.shop2_id, 'LF-03-B')

        self.user1 = create_user_with_detail('User1')
        self.user2 = create_user_with_detail('User2')

    def test_get_orders_placed_by_user(self):
        orderer1 = create_orderer(self.user1)
        orderer2 = create_orderer(self.user2)

        order1 = self.place_order(self.shop1_id, orderer1)
        order2 = self.place_order(self.shop1_id, orderer2)  # different user
        order3 = self.place_order(self.shop1_id, orderer1)
        order4 = self.place_order(self.shop1_id, orderer1)
        order5 = self.place_order(self.shop2_id, orderer1)  # different shop

        orders_orderer1_shop1 = self.get_orders_by_user(orderer1, self.shop1_id)
        assert orders_orderer1_shop1 == [order4, order3, order1]

        orders_orderer2_shop1 = self.get_orders_by_user(orderer2, self.shop1_id)
        assert orders_orderer2_shop1 == [order2]

        orders_orderer1_shop2 = self.get_orders_by_user(orderer1, self.shop2_id)
        assert orders_orderer1_shop2 == [order5]

    # helpers

    def place_order(self, shop_id, orderer):
        cart = Cart()

        order, _ = order_service.place_order(shop_id, orderer, cart)

        return order

    def get_orders_by_user(self, orderer, shop_id):
        return order_service.get_orders_placed_by_user_for_shop(
            orderer.user_id, shop_id
        )

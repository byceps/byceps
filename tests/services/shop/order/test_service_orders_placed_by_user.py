"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod

from testfixtures.shop_order import create_orderer

from tests.helpers import create_brand, create_email_config, create_party, \
    create_user_with_detail
from tests.services.shop.base import ShopTestBase


class ShopOrdersServiceTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        create_email_config()

        brand = create_brand()

        party1 = create_party(brand.id, 'lafiesta-2012', 'La Fiesta 2012')
        party2 = create_party(brand.id, 'lafiesta-2013', 'La Fiesta 2013')

        self.shop1_id = self.create_shop(party1.id).id
        self.shop2_id = self.create_shop(party2.id).id

        self.create_order_number_sequence(self.shop1_id, 'LF-02-B')
        self.create_order_number_sequence(self.shop2_id, 'LF-03-B')

        self.user1 = create_user_with_detail('User1')
        self.user2 = create_user_with_detail('User2')

    def test_get_orders_placed_by_user_for_party(self):
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
        payment_method = PaymentMethod.bank_transfer

        cart = Cart()

        return order_service.place_order(shop_id, orderer, payment_method, cart)

    def get_orders_by_user(self, orderer, shop_id):
        return order_service \
            .get_orders_placed_by_user_for_shop(orderer.user_id, shop_id)

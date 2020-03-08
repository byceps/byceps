"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.transfer.models import PaymentMethod
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as shop_sequence_service

from testfixtures.shop_order import create_orderer

from tests.helpers import (
    create_brand,
    create_email_config,
    create_party,
    create_user_with_detail,
)
from tests.services.shop.base import ShopTestBase


class OrderActionTestBase(ShopTestBase):

    def setUp(self):
        super().setUp()

        self.admin = create_user_with_detail('Admin')
        self.buyer = create_user_with_detail('Buyer')

        create_email_config()

        self.shop = self.create_shop()

        shop_sequence_service.create_order_number_sequence(
            self.shop.id, prefix='order-'
        )

        brand = create_brand()
        self.party = create_party(brand_id=brand.id)

    # -------------------------------------------------------------------- #
    # helpers

    def place_order(self, articles_with_quantity):
        orderer = create_orderer(self.buyer)

        cart = Cart()
        for article, quantity in articles_with_quantity:
            cart.add_item(article, quantity)

        order, _ = order_service.place_order(self.shop.id, orderer, cart)

        return order

    def mark_order_as_paid(self):
        order_service.mark_order_as_paid(
            self.order.id, PaymentMethod.bank_transfer, self.admin.id
        )

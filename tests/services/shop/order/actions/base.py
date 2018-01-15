"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.payment import PaymentMethod
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence.models import Purpose
from byceps.services.shop.sequence import service as shop_sequence_service

from testfixtures.shop_order import create_orderer

from tests.base import AbstractAppTestCase


ANY_PAYMENT_METHOD = PaymentMethod.bank_transfer


class OrderActionTestBase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.admin = self.create_user_with_detail('Admin')
        self.buyer = self.create_user_with_detail('Buyer')

        shop_sequence_service.create_party_sequence(self.party.id,
            Purpose.order, prefix='article-')

    # -------------------------------------------------------------------- #
    # helpers

    def create_order(self, articles_with_quantity):
        orderer = create_orderer(self.buyer)

        cart = Cart()
        for article, quantity in articles_with_quantity:
            cart.add_item(article, quantity)

        return order_service.create_order(self.party.id, orderer,
            ANY_PAYMENT_METHOD, cart)

    def mark_order_as_paid(self):
        order_service.mark_order_as_paid(self.order.id, ANY_PAYMENT_METHOD,
            self.admin.id)

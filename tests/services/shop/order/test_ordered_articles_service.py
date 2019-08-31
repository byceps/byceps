"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.email import service as email_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import ordered_articles_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod, \
    PaymentState

from testfixtures.shop_order import create_orderer

from tests.helpers import create_brand, create_party, create_user_with_detail
from tests.services.shop.base import ShopTestBase


class OrderedArticlesServiceTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        user = create_user_with_detail()
        self.orderer = create_orderer(user)

        brand = create_brand()
        party = create_party(brand_id=brand.id)

        email_config_id = brand.id
        email_service.set_sender(email_config_id, 'shop@example.com')

        self.shop = self.create_shop(party.id, email_config_id)
        self.create_order_number_sequence(self.shop.id, 'ABC-01-B')
        self.article = self.create_article(self.shop.id, quantity=100)

    def test_count_ordered_articles(self):
        expected = {
            PaymentState.open: 12,
            PaymentState.canceled_before_paid: 7,
            PaymentState.paid: 3,
            PaymentState.canceled_after_paid: 6,
        }

        for article_quantity, payment_state in [
            (4, PaymentState.open),
            (6, PaymentState.canceled_after_paid),
            (1, PaymentState.open),
            (5, PaymentState.canceled_before_paid),
            (3, PaymentState.paid),
            (2, PaymentState.canceled_before_paid),
            (7, PaymentState.open),
        ]:
            order = self.place_order(article_quantity)
            self.set_payment_state(order.order_number, payment_state)

        totals = ordered_articles_service \
            .count_ordered_articles(self.article.item_number)

        assert totals == expected

    # -------------------------------------------------------------------- #
    # helpers

    def place_order(self, article_quantity):
        payment_method = PaymentMethod.bank_transfer

        cart = Cart()
        cart.add_item(self.article, article_quantity)

        return order_service.place_order(self.shop.id, self.orderer,
                                         payment_method, cart)

    def set_payment_state(self, order_number, payment_state):
        order = order_service.find_order_by_order_number(order_number)
        order.payment_state = payment_state
        self.db.session.commit()

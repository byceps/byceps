"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import count

from byceps.services.shop.order import ordered_articles_service
from byceps.services.shop.order.models.payment import PaymentState

from testfixtures.shop_article import create_article
from testfixtures.shop_order import create_order, create_order_item

from tests.base import AbstractAppTestCase


class OrderedArticlesServiceTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = self.create_user_with_detail()

        self.create_brand_and_party()

        self.article = self.create_article()

    def test_count_ordered_articles(self):
        expected = {
            PaymentState.open: 12,
            PaymentState.canceled_before_paid: 7,
            PaymentState.paid: 3,
            PaymentState.canceled_after_paid: 6,
        }

        order_number_sequence = count(1)
        for article_quantity, payment_state in [
            (4, PaymentState.open),
            (6, PaymentState.canceled_after_paid),
            (1, PaymentState.open),
            (5, PaymentState.canceled_before_paid),
            (3, PaymentState.paid),
            (2, PaymentState.canceled_before_paid),
            (7, PaymentState.open),
        ]:
            order_number = 'XY-01-B{:05d}'.format(next(order_number_sequence))
            self.create_order(order_number, article_quantity, payment_state)

        totals = ordered_articles_service.count_ordered_articles(self.article)

        assert totals == expected

    # -------------------------------------------------------------------- #
    # helpers

    def create_article(self):
        article = create_article(party_id=self.party.id)

        self.db.session.add(article)
        self.db.session.commit()

        return article

    def create_order(self, order_number, article_quantity, payment_state):
        order = create_order(self.party.id, self.user,
                             order_number=order_number)
        order.payment_state = payment_state
        self.db.session.add(order)

        order_item = create_order_item(order, self.article, article_quantity)
        self.db.session.add(order_item)

        self.db.session.commit()

        return order.to_tuple()

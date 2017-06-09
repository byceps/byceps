"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from byceps.services.shop.article.models import Article
from byceps.services.shop.order.models.order import Order, PaymentState
from byceps.services.shop.sequence.models import Purpose
from byceps.services.snippet.models.snippet import Snippet

from testfixtures.authentication import create_session_token
from testfixtures.shop_article import create_article
from testfixtures.shop_sequence import create_party_sequence
from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class ShopTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.app.add_url_rule('/shop/order_placed', 'snippet.order_placed',
                              lambda: None)

        self.setup_order_number_prefix_and_sequence()
        self.setup_orderer()
        self.setup_article()

    def setup_order_number_prefix_and_sequence(self):
        purpose = Purpose.order
        prefix = 'AEC-01-B'

        sequence = create_party_sequence(self.party, purpose, prefix, value=4)

        self.db.session.add(sequence)
        self.db.session.commit()

    def setup_orderer(self):
        self.orderer = create_user(1)

        self.db.session.add(self.orderer)
        self.db.session.commit()

        session_token = create_session_token(self.orderer.id)

        self.db.session.add(session_token)
        self.db.session.commit()

    def setup_article(self):
        article = create_article(party=self.party, quantity=5)
        self.db.session.add(article)
        self.db.session.commit()

        self.article_id = article.id

    def test_order_article(self):
        article_before = self.get_article()
        self.assertEqual(article_before.quantity, 5)

        url = '/shop/order_single/{}'.format(str(self.article_id))
        form_data = {
            'first_names': 'Hiro',
            'last_name': 'Protagonist',
            'country': 'State of Mind',
            'zip_code': '31337',
            'city': 'Atrocity',
            'street': 'L33t Street 101',
            'quantity': 1,  # TODO: Test with `3` if limitation is removed.
        }
        with self.client(user=self.orderer) as client:
            response = client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'), 'http://example.com/shop/order_placed')

        article_afterwards = self.get_article()
        self.assertEqual(article_afterwards.quantity, 4)

        order = Order.query.filter_by(placed_by=self.orderer).one()
        self.assertEqual(order.order_number, 'AEC-01-B00005')
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].article.id, self.article_id)
        self.assertEqual(order.items[0].price, article_before.price)
        self.assertEqual(order.items[0].tax_rate, article_before.tax_rate)
        self.assertEqual(order.items[0].quantity, 1)

    # helpers

    def get_article(self):
        return Article.query.get(self.article_id)

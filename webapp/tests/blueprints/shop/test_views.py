# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from byceps.blueprints.shop.models import Article, Order, \
    PartySequencePurpose, PaymentState
from byceps.blueprints.snippet.models import Snippet
from byceps.blueprints.user.models import User

from testfixtures.shop import create_article, create_party_sequence
from testfixtures.user import create_user

from tests import AbstractAppTestCase


class ShopTestCase(AbstractAppTestCase):

    def setUp(self):
        super(ShopTestCase, self).setUp()

        self.app.add_url_rule('/shop/order_placed', 'snippet.order_placed',
                              lambda: None)

        self.setup_order_number_sequence()
        self.setup_orderer()

    def setup_order_number_sequence(self):
        sequence = create_party_sequence(self.party,
                                         PartySequencePurpose.order,
                                         value=4)
        self.db.session.add(sequence)
        self.db.session.commit()

    def setup_orderer(self):
        self.orderer = create_user(1)
        self.db.session.add(self.orderer)
        self.db.session.commit()

    def test_order_article(self):
        article_before = create_article(party=self.party, quantity=5)
        self.db.session.add(article_before)
        self.db.session.commit()

        self.assertEqual(article_before.quantity, 5)

        url = '/shop/order_single/{}'.format(str(article_before.id))
        form_data = {
            'first_names': 'Hiro',
            'last_name': 'Protagonist',
            'date_of_birth': '01.01.1970',
            'zip_code': '31337',
            'city': 'Atrocity',
            'street': 'L33t Street 101',
            'quantity': 1,  # TODO: Test with `3` if limitation is removed.
        }
        with self.client(user=self.orderer) as client:
            response = client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'), 'http://example.com/shop/order_placed')

        article_afterwards = Article.query.get(article_before.id)
        self.assertEqual(article_afterwards.quantity, 4)

        order = Order.query.filter_by(placed_by=self.orderer).one()
        self.assertEqual(order.order_number, 'AEC-01-B00005')
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].article.id, article_before.id)
        self.assertEqual(order.items[0].price, article_before.price)
        self.assertEqual(order.items[0].tax_rate, article_before.tax_rate)
        self.assertEqual(order.items[0].quantity, 1)

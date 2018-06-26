"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.services.shop.article.models.article import Article
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.sequence.models import Purpose

from testfixtures.shop_article import create_article
from testfixtures.shop_sequence import create_sequence
from testfixtures.shop_shop import create_shop

from tests.base import AbstractAppTestCase


class ShopTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.app.add_url_rule('/shop/order_placed', 'snippet.order_placed',
                              lambda: None)

        self.setup_shop()
        self.setup_order_number_prefix_and_sequence()
        self.setup_orderer()
        self.setup_article()

    def setup_shop(self):
        self.shop = create_shop(self.party.id)

        self.db.session.add(self.shop)
        self.db.session.commit()

    def setup_order_number_prefix_and_sequence(self):
        purpose = Purpose.order
        prefix = 'AEC-01-B'

        sequence = create_sequence(self.party.id, purpose, prefix, value=4)

        self.db.session.add(sequence)
        self.db.session.commit()

    def setup_orderer(self):
        self.orderer = self.create_user()
        self.create_session_token(self.orderer.id)

    def setup_article(self):
        article = create_article(party_id=self.party.id, shop_id=self.shop.id,
                                 quantity=5)
        self.db.session.add(article)
        self.db.session.commit()

        self.article_id = article.id

    @patch('byceps.blueprints.shop_order.signals.order_placed.send')
    def test_order(self, order_placed_mock):
        article_before = self.get_article()
        assert article_before.quantity == 5

        url = '/shop/order'
        article_quantity_key = 'article_{}'.format(self.article_id)
        form_data = {
            'first_names': 'Hiro',
            'last_name': 'Protagonist',
            'country': 'State of Mind',
            'zip_code': '31337',
            'city': 'Atrocity',
            'street': 'L33t Street 101',
            article_quantity_key: 3,
        }
        with self.client(user=self.orderer) as client:
            response = client.post(url, data=form_data)

        assert_response_headers(response)

        article_afterwards = self.get_article()
        assert article_afterwards.quantity == 2

        order = Order.query.filter_by(placed_by=self.orderer).one()
        assert_order(order, 'AEC-01-B00005', 1)

        first_order_item = order.items[0]
        assert_order_item(first_order_item, self.article_id,
                          article_before.price, article_before.tax_rate, 3)

        order_placed_mock.assert_called_once_with(None, order_id=order.id)

    @patch('byceps.blueprints.shop_order.signals.order_placed.send')
    def test_order_single(self, order_placed_mock):
        article_before = self.get_article()
        assert article_before.quantity == 5

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

        assert_response_headers(response)

        article_afterwards = self.get_article()
        assert article_afterwards.quantity == 4

        order = Order.query.filter_by(placed_by=self.orderer).one()
        assert_order(order, 'AEC-01-B00005', 1)

        first_order_item = order.items[0]
        assert_order_item(first_order_item, self.article_id,
                          article_before.price, article_before.tax_rate, 1)

        order_placed_mock.assert_called_once_with(None, order_id=order.id)

    # helpers

    def get_article(self):
        return Article.query.get(self.article_id)


def assert_response_headers(response):
    assert response.status_code == 302
    assert response.headers.get('Location') == 'http://example.com/shop/order_placed'


def assert_order(order, order_number, item_quantity):
    assert order.order_number == order_number
    assert len(order.items) == item_quantity


def assert_order_item(order_item, article_id, price, tax_rate, quantity):
    assert order_item.article.id == article_id
    assert order_item.price == price
    assert order_item.tax_rate == tax_rate
    assert order_item.quantity == quantity

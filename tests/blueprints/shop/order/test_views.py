"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.services.shop.article.models.article import Article
from byceps.services.shop.order.models.order import Order

from testfixtures.shop_article import create_article

from tests.services.shop.base import ShopTestBase


class ShopOrderTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

        self.admin = self.create_user('Admin')
        self.setup_orderer()

        self.shop = self.create_shop(self.party.id)
        self.setup_order_number_prefix_and_sequence()
        self.create_payment_instructions_snippet(self.shop.id, self.admin.id)
        self.setup_article()

    def setup_order_number_prefix_and_sequence(self):
        self.create_order_number_sequence(self.shop.id, 'AEC-01-B', value=4)

    def setup_orderer(self):
        self.orderer = self.create_user()
        self.create_session_token(self.orderer.id)

    def setup_article(self):
        article = create_article(self.shop.id, quantity=5)

        self.db.session.add(article)
        self.db.session.commit()

        self.article_id = article.id

    @patch('byceps.blueprints.shop.order.signals.order_placed.send')
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
        with self.client(user_id=self.orderer.id) as client:
            response = client.post(url, data=form_data)

        article_afterwards = self.get_article()
        assert article_afterwards.quantity == 2

        order = Order.query.filter_by(placed_by=self.orderer).one()
        assert_order(order, 'AEC-01-B00005', 1)

        first_order_item = order.items[0]
        assert_order_item(first_order_item, self.article_id,
                          article_before.price, article_before.tax_rate, 3)

        order_placed_mock.assert_called_once_with(None, order_id=order.id)

        order_detail_page_url = 'http://example.com/shop/orders/{}' \
            .format(order.id)

        assert_response_headers(response, order_detail_page_url)

        with self.client(user_id=self.orderer.id) as client:
            assert_order_detail_page_works(client, order_detail_page_url,
                                           order.order_number)

    @patch('byceps.blueprints.shop.order.signals.order_placed.send')
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
        with self.client(user_id=self.orderer.id) as client:
            response = client.post(url, data=form_data)

        article_afterwards = self.get_article()
        assert article_afterwards.quantity == 4

        order = Order.query.filter_by(placed_by=self.orderer).one()
        assert_order(order, 'AEC-01-B00005', 1)

        first_order_item = order.items[0]
        assert_order_item(first_order_item, self.article_id,
                          article_before.price, article_before.tax_rate, 1)

        order_placed_mock.assert_called_once_with(None, order_id=order.id)

        order_detail_page_url = 'http://example.com/shop/orders/{}' \
            .format(order.id)

        assert_response_headers(response, order_detail_page_url)

        with self.client(user_id=self.orderer.id) as client:
            assert_order_detail_page_works(client, order_detail_page_url,
                                           order.order_number)

    # helpers

    def get_article(self):
        return Article.query.get(self.article_id)


def assert_response_headers(response, order_detail_page_url):
    assert response.status_code == 302
    assert response.headers.get('Location') == order_detail_page_url


def assert_order(order, order_number, item_quantity):
    assert order.order_number == order_number
    assert len(order.items) == item_quantity


def assert_order_item(order_item, article_id, unit_price, tax_rate, quantity):
    assert order_item.article.id == article_id
    assert order_item.unit_price == unit_price
    assert order_item.tax_rate == tax_rate
    assert order_item.quantity == quantity


def assert_order_detail_page_works(client, order_detail_page_url, order_number):
    response = client.get(order_detail_page_url)
    assert response.status_code == 200
    assert 'AEC-01-B00005' in response.get_data(as_text=True)

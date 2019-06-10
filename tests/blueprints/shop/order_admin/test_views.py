"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.services.shop.article.models.article import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod, \
    PaymentState

from testfixtures.shop_order import create_orderer

from tests.base import CONFIG_FILENAME_TEST_ADMIN
from tests.helpers import assign_permissions_to_user
from tests.services.shop.base import ShopTestBase


class ShopAdminTestCase(ShopTestBase):

    def setUp(self):
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

        self.admin = self.create_admin()

        self.orderer = self.create_user_with_detail('Besteller')

        self.create_brand_and_party()

        self.shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(self.shop.id, 'AEC-05-B')
        self.create_shop_fragment(self.shop.id, 'email_footer', 'kthxbye')

    def create_admin(self):
        admin = self.create_user('Admin')

        permission_ids = {
            'admin.access',
            'shop_order.cancel',
            'shop_order.mark_as_paid',
        }
        assign_permissions_to_user(admin.id, 'admin', permission_ids)

        self.create_session_token(admin.id)

        return admin

    @patch('byceps.blueprints.shop.order.signals.order_canceled.send')
    def test_cancel_before_paid(self, order_canceled_signal_send_mock):
        article_before = self.create_article(self.shop.id, quantity=8)

        quantified_articles_to_order = {(article_before, 3)}
        placed_order = self.place_order(quantified_articles_to_order)
        order_before = get_order(placed_order.id)

        assert article_before.quantity == 5

        assert_payment_is_open(order_before)

        url = '/admin/shop/orders/{}/cancel'.format(order_before.id)
        form_data = {'reason': 'Dein Vorname ist albern!'}
        with self.client(user_id=self.admin.id) as client:
            response = client.post(url, data=form_data)

        order_afterwards = get_order(order_before.id)
        assert response.status_code == 302
        assert_payment(order_afterwards, PaymentMethod.bank_transfer,
                       PaymentState.canceled_before_paid, self.admin.id)

        article_afterwards = Article.query.get(article_before.id)
        assert article_afterwards.quantity == 8

        order_canceled_signal_send_mock \
            .assert_called_once_with(None, order_id=placed_order.id)

    @patch('byceps.blueprints.shop.order.signals.order_paid.send')
    def test_mark_order_as_paid(self, order_paid_signal_send_mock):
        placed_order = self.place_order([])
        order_before = get_order(placed_order.id)

        assert_payment_is_open(order_before)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        form_data = {'payment_method': 'direct_debit'}
        with self.client(user_id=self.admin.id) as client:
            response = client.post(url, data=form_data)

        order_afterwards = get_order(order_before.id)
        assert response.status_code == 302
        assert_payment(order_afterwards, PaymentMethod.direct_debit,
                       PaymentState.paid, self.admin.id)

        order_paid_signal_send_mock \
            .assert_called_once_with(None, order_id=placed_order.id)

    @patch('byceps.blueprints.shop.order.signals.order_canceled.send')
    @patch('byceps.blueprints.shop.order.signals.order_paid.send')
    def test_cancel_after_paid(self, order_paid_signal_send_mock,
                               order_canceled_signal_send_mock):
        article_before = self.create_article(self.shop.id, quantity=8)

        quantified_articles_to_order = {(article_before, 3)}
        placed_order = self.place_order(quantified_articles_to_order)
        order_before = get_order(placed_order.id)

        assert article_before.quantity == 5

        assert_payment_is_open(order_before)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        form_data = {'payment_method': 'bank_transfer'}
        with self.client(user_id=self.admin.id) as client:
            response = client.post(url, data=form_data)

        url = '/admin/shop/orders/{}/cancel'.format(order_before.id)
        form_data = {'reason': 'Dein Vorname ist albern!'}
        with self.client(user_id=self.admin.id) as client:
            response = client.post(url, data=form_data)

        order_afterwards = get_order(order_before.id)
        assert response.status_code == 302
        assert_payment(order_afterwards, PaymentMethod.bank_transfer,
                       PaymentState.canceled_after_paid, self.admin.id)

        article_afterwards = Article.query.get(article_before.id)
        assert article_afterwards.quantity == 8

        order_canceled_signal_send_mock \
            .assert_called_once_with(None, order_id=placed_order.id)

    # helpers

    def place_order(self, quantified_articles):
        orderer = create_orderer(self.orderer)
        payment_method = PaymentMethod.bank_transfer
        cart = Cart()

        for article, quantity_to_order in quantified_articles:
            cart.add_item(article, quantity_to_order)

        return order_service.place_order(self.shop.id, orderer, payment_method,
                                         cart)


def assert_payment_is_open(order):
    assert order.payment_method == PaymentMethod.bank_transfer  # default
    assert order.payment_state == PaymentState.open
    assert order.payment_state_updated_at is None
    assert order.payment_state_updated_by_id is None


def assert_payment(order, method, state, updated_by_id):
    assert order.payment_method == method
    assert order.payment_state == state
    assert order.payment_state_updated_at is not None
    assert order.payment_state_updated_by_id == updated_by_id


def get_order(order_id):
    return Order.query.get(order_id)

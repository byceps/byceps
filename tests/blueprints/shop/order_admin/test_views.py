"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.article.models.article import Article
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order.transfer.models import PaymentMethod, \
    PaymentState

from testfixtures.shop_order import create_order, create_order_item

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

    def test_cancel_before_paid(self):
        article_before = self.create_article(self.shop.id, quantity=5)

        quantified_articles_to_order = {(article_before, 3)}
        order_before = self.create_order(quantified_articles_to_order)

        assert article_before.quantity == 5

        assert_payment_is_open(order_before)

        url = '/admin/shop/orders/{}/cancel'.format(order_before.id)
        form_data = {'reason': 'Dein Vorname ist albern!'}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        order_afterwards = Order.query.get(order_before.id)
        assert response.status_code == 302
        assert_payment(order_afterwards, PaymentMethod.bank_transfer,
                       PaymentState.canceled_before_paid, self.admin.id)

        article_afterwards = Article.query.get(article_before.id)
        assert article_afterwards.quantity == 8

    def test_mark_order_as_paid(self):
        order_before = self.create_order([])
        self.db.session.commit()

        assert_payment_is_open(order_before)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        form_data = {'payment_method': 'direct_debit'}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        order_afterwards = Order.query.get(order_before.id)
        assert response.status_code == 302
        assert_payment(order_afterwards, PaymentMethod.direct_debit,
                       PaymentState.paid, self.admin.id)

    def test_cancel_after_paid(self):
        article_before = self.create_article(self.shop.id, quantity=5)

        quantified_articles_to_order = {(article_before, 3)}
        order_before = self.create_order(quantified_articles_to_order)

        assert article_before.quantity == 5

        assert_payment_is_open(order_before)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        form_data = {'payment_method': 'bank_transfer'}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        url = '/admin/shop/orders/{}/cancel'.format(order_before.id)
        form_data = {'reason': 'Dein Vorname ist albern!'}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        order_afterwards = Order.query.get(order_before.id)
        assert response.status_code == 302
        assert_payment(order_afterwards, PaymentMethod.bank_transfer,
                       PaymentState.canceled_after_paid, self.admin.id)

        article_afterwards = Article.query.get(article_before.id)
        assert article_afterwards.quantity == 8

    # helpers

    def create_order(self, quantified_articles):
        order = create_order(self.party.id, self.orderer)
        self.db.session.add(order)

        for article, quantity_to_order in quantified_articles:
            order_item = create_order_item(order, article, quantity_to_order)
            self.db.session.add(order_item)

        self.db.session.commit()

        return order


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

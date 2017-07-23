"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.article.models.article import Article
from byceps.services.shop.order.models.order import Order, PaymentState

from testfixtures.shop_article import create_article
from testfixtures.shop_order import create_order, create_order_item
from testfixtures.user import create_user_with_detail

from tests.base import AbstractAppTestCase, CONFIG_FILENAME_TEST_ADMIN
from tests.helpers import assign_permissions_to_user


class ShopAdminTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

        self.setup_admin()
        self.orderer = self.create_user()

    def setup_admin(self):
        permission_ids = {'admin.access', 'shop_order.update'}
        assign_permissions_to_user(self.admin.id, 'admin', permission_ids)

    def test_cancel_before_paid(self):
        article_before = self.create_article(5)

        quantified_articles_to_order = {(article_before, 3)}
        order_before = self.create_order(quantified_articles_to_order)

        self.assertEqual(article_before.quantity, 5)

        self.assertEqual(order_before.payment_state, PaymentState.open)
        self.assertIsNone(order_before.payment_state_updated_at)
        self.assertIsNone(order_before.payment_state_updated_by)

        url = '/admin/shop/orders/{}/cancel'.format(order_before.id)
        form_data = {'reason': 'Dein Vorname ist albern!'}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        order_afterwards = Order.query.get(order_before.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order_afterwards.payment_state, PaymentState.canceled_before_paid)
        self.assertIsNotNone(order_afterwards.payment_state_updated_at)
        self.assertEqual(order_afterwards.payment_state_updated_by, self.admin)

        article_afterwards = Article.query.get(article_before.id)
        self.assertEqual(article_afterwards.quantity, 8)

    def test_mark_order_as_paid(self):
        order_before = self.create_order([])
        self.db.session.commit()

        self.assertEqual(order_before.payment_state, PaymentState.open)
        self.assertIsNone(order_before.payment_state_updated_at)
        self.assertIsNone(order_before.payment_state_updated_by)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        order_afterwards = Order.query.get(order_before.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order_afterwards.payment_state, PaymentState.paid)
        self.assertIsNotNone(order_afterwards.payment_state_updated_at)
        self.assertEqual(order_afterwards.payment_state_updated_by, self.admin)

    def test_cancel_after_paid(self):
        article_before = self.create_article(5)

        quantified_articles_to_order = {(article_before, 3)}
        order_before = self.create_order(quantified_articles_to_order)

        self.assertEqual(article_before.quantity, 5)

        self.assertEqual(order_before.payment_state, PaymentState.open)
        self.assertIsNone(order_before.payment_state_updated_at)
        self.assertIsNone(order_before.payment_state_updated_by)

        url = '/admin/shop/orders/{}/mark_as_paid'.format(order_before.id)
        with self.client(user=self.admin) as client:
            response = client.post(url)

        url = '/admin/shop/orders/{}/cancel'.format(order_before.id)
        form_data = {'reason': 'Dein Vorname ist albern!'}
        with self.client(user=self.admin) as client:
            response = client.post(url, data=form_data)

        order_afterwards = Order.query.get(order_before.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order_afterwards.payment_state, PaymentState.canceled_after_paid)
        self.assertIsNotNone(order_afterwards.payment_state_updated_at)
        self.assertEqual(order_afterwards.payment_state_updated_by, self.admin)

        article_afterwards = Article.query.get(article_before.id)
        self.assertEqual(article_afterwards.quantity, 8)

    # helpers

    def create_user(self):
        user = create_user_with_detail()

        self.db.session.add(user)
        self.db.session.commit()

        return user

    def create_article(self, quantity):
        article = create_article(party=self.party, quantity=quantity)

        self.db.session.add(article)
        self.db.session.commit()

        return article

    def create_order(self, quantified_articles):
        order = create_order(self.party.id, self.orderer)
        self.db.session.add(order)

        for article, quantity_to_order in quantified_articles:
            order_item = create_order_item(order, article, quantity_to_order)
            self.db.session.add(order_item)

        self.db.session.commit()

        return order

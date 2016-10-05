# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from byceps.blueprints.shop.models.order import Order, PaymentState
from byceps.services.authorization import service as authorization_service
from byceps.services.shop.article.models import Article

from testfixtures.shop_article import create_article
from testfixtures.shop_order import create_order, create_order_item
from testfixtures.user import create_user_with_detail

from tests.base import AbstractAppTestCase


class ShopAdminTestCase(AbstractAppTestCase):

    def setUp(self):
        super(ShopAdminTestCase, self).setUp(env='test_admin')

        self.setup_admin()
        self.orderer = self.create_user(1)

    def setup_admin(self):
        permission_id = 'shop_order.update'
        permission = authorization_service.create_permission(permission_id,
                                                             permission_id)

        role_id = 'shop_admin'
        role = authorization_service.create_role(role_id, role_id)

        authorization_service.assign_permission_to_role(permission, role)
        authorization_service.assign_role_to_user(role, self.admin)

    def test_cancel(self):
        article_before = self.create_article(5)
        quantified_articles_to_order = {(article_before, 3)}
        order_before = self.create_order(quantified_articles_to_order)
        self.db.session.commit()

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
        self.assertEqual(order_afterwards.payment_state, PaymentState.canceled)
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

    # helpers

    def create_user(self, number):
        user = create_user_with_detail(number)
        self.db.session.add(user)
        return user

    def create_article(self, quantity):
        article = create_article(party=self.party, quantity=quantity)
        self.db.session.add(article)
        return article

    def create_order(self, quantified_articles):
        order = create_order(party=self.party, placed_by=self.orderer)
        self.db.session.add(order)

        for article, quantity_to_order in quantified_articles:
            order_item = create_order_item(order, article, quantity_to_order)
            self.db.session.add(order_item)

        return order

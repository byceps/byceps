# -*- coding: utf-8 -*-

from datetime import date

from byceps.blueprints.shop.models import Article, Order, PaymentState
from byceps.blueprints.snippet.models import Snippet
from byceps.blueprints.user.models import User

from testfixtures.shop import create_article
from testfixtures.user import create_user

from tests import AbstractAppTestCase


class ShopTestCase(AbstractAppTestCase):

    def setUp(self):
        super(ShopTestCase, self).setUp()

        self.app.add_url_rule('/shop/order_placed', 'snippet.order_placed',
                              lambda: None)

        self.setUp_current_user()

    def setUp_current_user(self):
        self.current_user = self.create_user(99, enabled=True)
        self.db.session.commit()

    def test_order_article(self):
        article_before = create_article(party=self.party, quantity=5)
        self.db.session.add(article_before)
        self.db.session.commit()

        self.assertEqual(article_before.quantity, 5)

        url = '/shop/order_single?article_id={}'.format(str(article_before.id))
        with self.client.session_transaction() as session:
            session['user_id'] = str(self.current_user.id)
        form_data = {
            'first_names': 'Hiro',
            'last_name': 'Protagonist',
            'date_of_birth': '01.01.1970',
            'zip_code': '31337',
            'city': 'Atrocity',
            'street': 'L33t Street 101',
            'quantity': 1,  # TODO: Test with `3` if limitation is removed.
        }
        response = self.client.post(url, data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('Location'), 'http://localhost/shop/order_placed')

        article_afterwards = Article.query.get(article_before.id)
        self.assertEqual(article_afterwards.quantity, 4)

        order = Order.query.filter_by(placed_by=self.current_user).one()
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].article.id, article_before.id)
        self.assertEqual(order.items[0].quantity, 1)

    def create_user(self, number, *, enabled=True):
        user = create_user(number, enabled=enabled)
        self.db.session.add(user)
        return user

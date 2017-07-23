"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from testfixtures.authentication import create_session_token
from testfixtures.party import create_party
from testfixtures.shop_order import create_order
from testfixtures.user import create_user_with_detail

from tests.base import AbstractAppTestCase


class ShopOrdersTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user1 = self.create_user('User1')
        self.user2 = self.create_user('User2')

    def test_view_matching_user_and_party(self):
        order = self.create_order(self.party.id, self.user1, 'LF-02-B00014')

        response = self.request_view(self.user1, order)

        self.assertEqual(response.status_code, 200)

    def test_view_matching_party_but_different_user(self):
        order = self.create_order(self.party.id, self.user1, 'LF-02-B00014')

        response = self.request_view(self.user2, order)

        self.assertEqual(response.status_code, 404)

    def test_view_matching_user_but_different_party(self):
        other_party = self.create_party('otherlan-2013', 'OtherLAN 2013')
        order = self.create_order(other_party.id, self.user1, 'LF-02-B00014')

        response = self.request_view(self.user1, order)

        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------------------------- #
    # helpers

    def create_party(self, party_id, title):
        party = create_party(id=party_id, title=title, brand=self.brand)

        self.db.session.add(party)
        self.db.session.commit()

        return party

    def create_user(self, screen_name):
        user = create_user_with_detail(screen_name)

        self.db.session.add(user)
        self.db.session.commit()

        return user

    def create_session(self, user_id):
        session_token = create_session_token(user_id)

        self.db.session.add(session_token)
        self.db.session.commit()

    def create_order(self, party_id, user, order_number):
        order = create_order(party_id, user, order_number=order_number)

        self.db.session.add(order)
        self.db.session.commit()

        return order.to_tuple()

    def request_view(self, current_user, order):
        self.create_session(current_user.id)

        url = '/shop/orders/{}'.format(str(order.id))

        with self.client(user=current_user) as client:
            response = client.get(url)

        return response

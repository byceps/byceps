"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from testfixtures.shop_order import create_order

from tests.base import AbstractAppTestCase


class ShopOrdersTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user1 = self.create_user_with_detail('User1')
        self.user2 = self.create_user_with_detail('User2')

        self.create_brand_and_party()

    def test_view_matching_user_and_party(self):
        order = self.create_order(self.party.id, self.user1, 'LF-02-B00014')

        response = self.request_view(self.user1, order)

        assert response.status_code == 200

    def test_view_matching_party_but_different_user(self):
        order = self.create_order(self.party.id, self.user1, 'LF-02-B00014')

        response = self.request_view(self.user2, order)

        assert response.status_code == 404

    def test_view_matching_user_but_different_party(self):
        other_party = self.create_party(self.brand.id, 'otherlan-2013',
                                        'OtherLAN 2013')
        order = self.create_order(other_party.id, self.user1, 'LF-02-B00014')

        response = self.request_view(self.user1, order)

        assert response.status_code == 404

    # -------------------------------------------------------------------- #
    # helpers

    def create_order(self, party_id, user, order_number):
        order = create_order(party_id, user, order_number=order_number)

        self.db.session.add(order)
        self.db.session.commit()

        return order.to_tuple()

    def request_view(self, current_user, order):
        self.create_session_token(current_user.id)

        url = '/shop/orders/{}'.format(str(order.id))

        with self.client(user=current_user) as client:
            response = client.get(url)

        return response

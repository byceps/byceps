"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.order import service

from testfixtures.party import create_party
from testfixtures.shop_order import create_order
from testfixtures.user import create_user_with_detail

from tests.base import AbstractAppTestCase


class ShopOrdersServiceTestCase(AbstractAppTestCase):

    def test_get_orders_placed_by_user_for_party(self):
        party1 = self.create_party('lafiesta-2012', 'La Fiesta 2012')
        party2 = self.create_party('lafiesta-2013', 'La Fiesta 2013')

        user1 = self.create_user('User1')
        user2 = self.create_user('User2')

        order1 = self.create_order(party1.id, user1, 'LF-02-B00014')
        order2 = self.create_order(party1.id, user2, 'LF-02-B00015')  # other user
        order3 = self.create_order(party1.id, user1, 'LF-02-B00016')
        order4 = self.create_order(party1.id, user1, 'LF-02-B00023')
        order5 = self.create_order(party2.id, user1, 'LF-03-B00008')  # other party

        orders_user1_party2012 = service.get_orders_placed_by_user_for_party(user1.id, party1.id)
        self.assertListEqual(orders_user1_party2012, [order4, order3, order1])

        orders_user2_party2012 = service.get_orders_placed_by_user_for_party(user2.id, party1.id)
        self.assertListEqual(orders_user2_party2012, [order2])

        orders_user1_party2013 = service.get_orders_placed_by_user_for_party(user1.id, party2.id)
        self.assertListEqual(orders_user1_party2013, [order5])

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

    def create_order(self, party_id, user, order_number):
        order = create_order(party_id, user, order_number=order_number)

        self.db.session.add(order)
        self.db.session.commit()

        return order.to_tuple()

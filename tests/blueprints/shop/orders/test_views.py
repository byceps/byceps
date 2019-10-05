"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod

from testfixtures.shop_order import create_orderer

from tests.helpers import (
    create_brand,
    create_email_config,
    create_party,
    create_site,
    create_user_with_detail,
    http_client,
    login_user,
)
from tests.services.shop.base import ShopTestBase


class ShopOrdersTestCase(ShopTestBase):

    def setUp(self):
        super().setUp()

        self.user1 = create_user_with_detail('User1')
        self.user2 = create_user_with_detail('User2')

        create_email_config()

        self.shop = self.create_shop('shop-1')

        self.brand = create_brand()

    def test_view_matching_user_and_party_and_shop(self):
        party = create_party(self.brand.id, shop_id=self.shop.id)
        create_site(party_id=party.id)

        self.create_order_number_sequence(self.shop.id, 'LF-02-B')
        self.create_payment_instructions_snippet(self.shop.id)

        order_id = self.place_order(self.shop.id, self.user1)

        response = self.request_view(self.user1, order_id)

        assert response.status_code == 200

    def test_view_matching_party_and_shop_but_different_user(self):
        party = create_party(self.brand.id, shop_id=self.shop.id)
        create_site(party_id=party.id)

        self.create_order_number_sequence(self.shop.id, 'LF-02-B')
        self.create_payment_instructions_snippet(self.shop.id)

        order_id = self.place_order(self.shop.id, self.user1)

        response = self.request_view(self.user2, order_id)

        assert response.status_code == 404

    def test_view_matching_user_but_different_party_and_shop(self):
        shop = self.create_shop('shop-2')
        other_party = create_party(
            self.brand.id, 'otherlan-2013', 'OtherLAN 2013', shop_id=shop.id
        )
        create_site(party_id=other_party.id)

        self.create_order_number_sequence(self.shop.id, 'LF-02-B')
        self.create_payment_instructions_snippet(self.shop.id)

        order_id = self.place_order(self.shop.id, self.user1)

        response = self.request_view(self.user1, order_id)

        assert response.status_code == 404

    # helpers

    def create_payment_instructions_snippet(self, shop_id):
        self.create_shop_fragment(
            shop_id, 'payment_instructions', 'Send all ur moneyz!'
        )

    def place_order(self, shop_id, user):
        orderer = create_orderer(user)
        payment_method = PaymentMethod.bank_transfer
        cart = Cart()

        order = order_service.place_order(
            shop_id, orderer, payment_method, cart
        )

        return order.id

    def request_view(self, current_user, order_id):
        login_user(current_user.id)

        url = f'/shop/orders/{order_id!s}'

        with http_client(self.app, user_id=current_user.id) as client:
            response = client.get(url)

        return response

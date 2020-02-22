"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service

from tests.base import CONFIG_FILENAME_TEST_ADMIN
from tests.helpers import (
    assign_permissions_to_user,
    create_brand,
    create_email_config,
    create_party,
    create_user,
    http_client,
    login_user,
)
from tests.services.shop.base import ShopTestBase


class ExportTestCase(ShopTestBase):

    def setUp(self):
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

        self.admin = self.create_admin()

        create_email_config()

        self.create_brand_and_party()

        self.shop = self.create_shop()
        self.create_order_number_sequence(self.shop.id, 'LR-08-B', value=26)
        self.create_articles()
        self.order = self.place_order()

    @freeze_time('2015-04-15 07:54:18')  # UTC
    def test_serialize_order(self):
        filename = 'testfixtures/shop/order_export.xml'
        with codecs.open(filename, encoding='iso-8859-1') as f:
            expected = f.read().rstrip()

        url = f'/admin/shop/orders/{self.order.id}/export'
        with http_client(self.app, user_id=self.admin.id) as client:
            response = client.get(url)

        assert response.status_code == 200
        assert response.content_type == 'application/xml; charset=iso-8859-1'

        body = response.get_data().decode('utf-8')
        assert body == expected

    # helpers

    def create_admin(self):
        admin = create_user('Admin')

        permission_ids = {'admin.access', 'shop_order.view'}
        assign_permissions_to_user(admin.id, 'admin', permission_ids)

        login_user(admin.id)

        return admin

    def create_brand_and_party(self):
        self.brand = create_brand('lanresort', 'LANresort')
        self.party = create_party(
            self.brand.id, 'lanresort-2015', 'LANresort 2015'
        )

    def create_articles(self):
        self.article_table = self.create_article(
            'LR-08-A00002',
            'Tisch (zur Miete), 200 x 80 cm',
            Decimal('20.00'),
            Decimal('0.19'),
        )

        self.article_bungalow = self.create_article(
            'LR-08-A00003',
            'LANresort 2015: Bungalow 4 Plätze',
            Decimal('355.00'),
            Decimal('0.07'),
        )

        self.article_guest_fee = self.create_article(
            'LR-08-A00006',
            'Touristische Gästeabgabe (BispingenCard), pauschal für 4 Personen',
            Decimal('6.00'),
            Decimal('0.19'),
        )

    def create_article(self, item_number, description, price, tax_rate):
        return super().create_article(
            self.shop.id,
            item_number=item_number,
            description=description,
            price=price,
            tax_rate=tax_rate,
            quantity=10,
        )

    def place_order(self):
        orderer = self.create_orderer()
        cart = self.create_cart()
        created_at = datetime(2015, 2, 26, 12, 26, 24)  # UTC

        order, _ = order_service.place_order(
            self.shop.id, orderer, cart, created_at=created_at
        )

        return order

    def create_orderer(self):
        user = create_user(
            'Besteller', email_address='h-w.mustermann@example.com'
        )

        return Orderer(
            user.id,
            'Hans-Werner',
            'Mustermann',
            'Deutschland',
            '42000',
            'Hauptstadt',
            'Nebenstraße 23a',
        )

    def create_cart(self):
        cart = Cart()

        cart.add_item(self.article_bungalow, 1)
        cart.add_item(self.article_guest_fee, 1)
        cart.add_item(self.article_table, 2)

        return cart

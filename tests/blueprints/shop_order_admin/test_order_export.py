"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time

from testfixtures.brand import create_brand
from testfixtures.party import create_party
from testfixtures.shop_article import create_article
from testfixtures.shop_order import create_order, create_order_item
from testfixtures.user import create_user_with_detail

from tests.base import AbstractAppTestCase, CONFIG_FILENAME_TEST_ADMIN
from tests.helpers import assign_permissions_to_user


class ExportTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp(config_filename=CONFIG_FILENAME_TEST_ADMIN)

        self.setup_admin()
        self.create_articles()
        self.create_order()

    def create_brand_and_party(self):
        self.brand = create_brand(
            id='lanresort',
            title='LANresort')
        self.db.session.add(self.brand)

        self.party = create_party(
            id='lanresort-2015',
            brand=self.brand,
            title='LANresort 2015')
        self.db.session.add(self.party)

        self.db.session.commit()

    @freeze_time('2015-04-15 09:54:18')
    def test_serialize_order(self):
        filename = 'testfixtures/shop/order_export.xml'
        with codecs.open(filename, encoding='iso-8859-1') as f:
            expected = f.read().rstrip()

        url = '/admin/shop/orders/{}/export'.format(self.order.id)
        with self.client(user=self.admin) as client:
            response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/xml; charset=iso-8859-1')
        body = response.get_data().decode('utf-8')
        self.assertEqual(body, expected)

    # helpers

    def setup_admin(self):
        permission_ids = {'admin.access', 'shop_order.view'}
        assign_permissions_to_user(self.admin.id, 'admin', permission_ids)

    def create_articles(self):
        self.article_table = self.build_article(
            'LR-08-A00002',
            'Tisch (zur Miete), 200 x 80 cm',
            Decimal('20.00'),
            Decimal('0.19'),
        )

        self.article_bungalow = self.build_article(
            'LR-08-A00003',
            'LANresort 2015: Bungalow 4 Plätze',
            Decimal('355.00'),
            Decimal('0.07'),
        )

        self.article_guest_fee = self.build_article(
            'LR-08-A00006',
            'Touristische Gästeabgabe (BispingenCard), pauschal für 4 Personen',
            Decimal('6.00'),
            Decimal('0.19'),
        )

        self.db.session.add(self.article_table)
        self.db.session.add(self.article_bungalow)
        self.db.session.add(self.article_guest_fee)
        self.db.session.commit()

    def build_article(self, item_number, description, price, tax_rate):
        return create_article(
            party=self.party,
            item_number=item_number,
            description=description,
            price=price,
            tax_rate=tax_rate,
            quantity=10)

    def create_order(self):
        orderer = self.build_orderer()
        self.db.session.add(orderer)

        self.order = create_order(self.party.id, orderer,
                                  order_number='LR-08-B00027')
        self.order.created_at = datetime(2015, 2, 26, 13, 26, 24)
        self.db.session.add(self.order)

        order_items = self.build_order_items()
        self.db.session.add_all(order_items)

        self.db.session.commit()

    def build_orderer(self):
        email_address = 'h-w.mustermann@example.com'
        orderer = create_user_with_detail(email_address=email_address)
        orderer.detail.last_name = 'Mustermann'
        orderer.detail.first_names = 'Hans-Werner'
        orderer.detail.country = 'Deutschland'
        orderer.detail.zip_code = '42000'
        orderer.detail.city = 'Hauptstadt'
        orderer.detail.street = 'Nebenstraße 23a'
        orderer.detail.phone_number = '555-1234'
        return orderer

    def build_order_items(self):
        for article, quantity in [
            (self.article_bungalow, 1),
            (self.article_guest_fee, 1),
            (self.article_table, 2),
        ]:
            yield create_order_item(self.order, article, quantity)

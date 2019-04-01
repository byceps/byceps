"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from byceps.blueprints.shop.order.signals import order_placed
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod

from tests.helpers import current_party_set, current_user_set

from .base import OrderEmailTestBase


class EmailOnOrderPlacedSignalTest(OrderEmailTestBase):

    def setUp(self):
        super().setUp()

        brand = self.create_brand('acmecon', 'Acme Entertainment Convention')
        self.set_brand_email_sender_address(brand.id, 'acmecon@example.com')

        self.party = self.create_party(brand.id, 'acmecon-2014',
                                       'Acme Entertainment Convention 2014')

        self.shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(self.shop.id, 'AC-14-B', value=252)

        self.create_articles()

        self.user = self.create_user_with_detail('Interessent')

        self.order_id = self.place_order(self.user)

        order_service.mark_order_as_paid(self.order_id,
                                         PaymentMethod.bank_transfer,
                                         self.admin.id)

    @patch('byceps.email.send')
    def test_email_on_order_placed(self, send_email_mock):
        self.send_event(self.order_id)

        expected_to_orderer_sender = 'acmecon@example.com'
        expected_to_orderer_recipients = [self.user.email_address]
        expected_to_orderer_subject = 'Deine Bestellung (AC-14-B00253) ist eingegangen.'
        expected_to_orderer_body = '''
Hallo Interessent,

vielen Dank für deine Bestellung mit der Nummer AC-14-B00253 am 15.08.2014 über unsere Website.

Folgende Artikel hast du bestellt:

  Bezeichnung: Einzelticket, Kategorie Loge
  Anzahl: 5
  Stückpreis: 99,00 €

  Bezeichnung: T-Shirt, Größe L
  Anzahl: 2
  Stückpreis: 14,95 €

  Gesamtbetrag: 524,90 €

Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AC-14-B00253

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.example.com/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: acmecon@example.com
        '''.strip()

        send_email_mock.assert_called_once_with(
            expected_to_orderer_sender,
            expected_to_orderer_recipients,
            expected_to_orderer_subject,
            expected_to_orderer_body)

    # helpers

    def create_articles(self):
        self.article1 = self.create_article(self.shop.id, 'AC-14-A00003', 'Einzelticket, Kategorie Loge', Decimal('99.00'), 123)
        self.article2 = self.create_article(self.shop.id, 'AC-14-A00007', 'T-Shirt, Größe L', Decimal('14.95'), 50)

    def place_order(self, orderer):
        created_at = datetime(2014, 8, 15, 20, 7, 43)

        items_with_quantity = [
            (self.article1, 5),
            (self.article2, 2),
        ]

        return self.place_order_with_items(self.party.id, orderer, created_at,
                                           items_with_quantity)

    def send_event(self, order_id):
        with \
                current_party_set(self.app, self.party), \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_placed.send(None, order_id=order_id)

"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service

from tests.helpers import (
    create_email_config,
    create_user_with_detail,
    current_user_set,
)

from .base import OrderEmailTestBase


class EmailOnOrderPlacedTest(OrderEmailTestBase):

    def setUp(self):
        super().setUp()

        create_email_config(sender_address='acmecon@example.com')

        self.shop = self.create_shop()
        sequence_service.create_order_number_sequence(self.shop.id, 'AC-14-B', value=252)

        self.create_email_payment_instructions_snippet()
        self.create_email_footer_snippet()

        self.create_articles()

        self.user = create_user_with_detail(
            'Interessent',
            email_address='interessent@example.com',
        )

        self.order_id = self.place_order(self.user)

    def create_email_payment_instructions_snippet(self):
        self.create_shop_fragment(
            self.shop.id,
            'email_payment_instructions',
            '''
Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: {{ order_number }}

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.example.com/shop/orders
''',
        )

    def create_email_footer_snippet(self):
        self.create_shop_fragment(
            self.shop.id,
            'email_footer',
            '''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: acmecon@example.com
''',
        )

    @patch('byceps.email.send')
    def test_email_on_order_placed(self, send_email_mock):
        with \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_email_service \
                .send_email_for_incoming_order_to_orderer(self.order_id)

        expected_to_orderer_sender = 'acmecon@example.com'
        expected_to_orderer_recipients = ['interessent@example.com']
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
            expected_to_orderer_body,
        )

    # helpers

    def create_articles(self):
        self.article1 = self.create_article(
            self.shop.id,
            'AC-14-A00003',
            'Einzelticket, Kategorie Loge',
            Decimal('99.00'),
            123,
        )
        self.article2 = self.create_article(
            self.shop.id,
            'AC-14-A00007',
            'T-Shirt, Größe L',
            Decimal('14.95'),
            50,
        )

    def place_order(self, orderer):
        created_at = datetime(2014, 8, 15, 20, 7, 43)

        items_with_quantity = [
            (self.article1, 5),
            (self.article2, 2),
        ]

        return self.place_order_with_items(
            self.shop.id, orderer, created_at, items_with_quantity
        )

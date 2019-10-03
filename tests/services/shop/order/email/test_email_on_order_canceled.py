"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service

from tests.helpers import (
    create_brand,
    create_email_config,
    create_party,
    create_user_with_detail,
    current_party_set,
    current_user_set,
)

from .base import OrderEmailTestBase


class EmailOnOrderCanceledTest(OrderEmailTestBase):

    def setUp(self):
        super().setUp()

        create_email_config(sender_address='acmecon@example.com')

        self.shop = self.create_shop()
        self.create_order_number_sequence(self.shop.id, 'AC-14-B', value=16)

        self.create_email_footer_snippet()

        brand = create_brand()

        self.party = create_party(brand.id)

        self.user = create_user_with_detail('Versager')

        self.order_id = self.place_order(self.user)

        reason = 'Du hast nicht rechtzeitig bezahlt.'
        order_service.cancel_order(self.order_id, self.admin.id, reason)

    def create_email_footer_snippet(self):
        self.create_shop_fragment(self.shop.id, 'email_footer', '''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: acmecon@example.com
''')

    @patch('byceps.email.send')
    def test_email_on_order_canceled(self, send_email_mock):
        with \
                current_party_set(self.app, self.party), \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_email_service \
                .send_email_for_canceled_order_to_orderer(self.order_id)

        expected_sender = 'acmecon@example.com'
        expected_recipients = [self.user.email_address]
        expected_subject = '\u274c Deine Bestellung (AC-14-B00017) wurde storniert.'
        expected_body = '''
Hallo Versager,

deine Bestellung mit der Nummer AC-14-B00017 vom 06.11.2014 wurde von uns aus folgendem Grund storniert:

Du hast nicht rechtzeitig bezahlt.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: acmecon@example.com
        '''.strip()

        send_email_mock.assert_called_once_with(
            expected_sender,
            expected_recipients,
            expected_subject,
            expected_body)

    # helpers

    def place_order(self, orderer):
        created_at = datetime(2014, 11, 5, 23, 32, 9)

        return self.place_order_with_items(self.shop.id, orderer, created_at,
                                           [])

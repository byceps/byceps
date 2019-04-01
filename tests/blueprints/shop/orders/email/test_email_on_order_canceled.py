"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

from byceps.blueprints.shop.order.signals import order_canceled
from byceps.services.shop.order import service as order_service

from tests.helpers import current_party_set, current_user_set

from .base import OrderEmailTestBase


class EmailOnOrderCanceledSignalTest(OrderEmailTestBase):

    def setUp(self):
        super().setUp()

        brand = self.create_brand('acmecon', 'Acme Entertainment Convention')
        self.set_brand_email_sender_address(brand.id, 'acmecon@example.com')

        self.party = self.create_party(brand.id,
                                       'acmecon-2014',
                                       'Acme Entertainment Convention 2014')

        self.shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(self.shop.id, 'AC-14-B', value=16)

        self.user = self.create_user_with_detail('Versager')

        self.order_id = self.place_order(self.user)

        reason = 'Du hast nicht rechtzeitig bezahlt.'
        order_service.cancel_order(self.order_id, self.admin.id, reason)

    @patch('byceps.email.send')
    def test_email_on_order_canceled(self, send_email_mock):
        self.send_event(self.order_id)

        expected_sender = 'acmecon@example.com'
        expected_recipients = [self.user.email_address]
        expected_subject = '\u274c Deine Bestellung (AC-14-B00017) wurde storniert.'
        expected_body = '''
Hallo Versager,

deine Bestellung mit der Bestellnummer AC-14-B00017 wurde von uns aus folgendem Grund storniert:

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
        return self.place_order_with_items(self.shop.id, orderer, None, [])

    def send_event(self, order_id):
        with \
                current_party_set(self.app, self.party), \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_canceled.send(None, order_id=order_id)

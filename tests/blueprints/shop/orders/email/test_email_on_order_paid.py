"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

from byceps.blueprints.shop_order.signals import order_paid
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod

from tests.helpers import current_party_set, current_user_set

from .base import OrderEmailTestBase


class EmailOnOrderPaidSignalTest(OrderEmailTestBase):

    def setUp(self):
        super().setUp()

        brand = self.create_brand('acmecon', 'Acme Entertainment Convention')
        self.set_brand_email_sender_address(brand.id, 'acmecon@example.com')

        self.party = self.create_party(brand.id, 'acmecon-2014',
                                       'Acme Entertainment Convention 2014')

        self.shop = self.create_shop(self.party.id)
        self.create_order_number_sequence(self.shop.id, 'AC-14-B', value=21)

        self.user = self.create_user_with_detail('Vorbild')

        self.order_id = self.place_order(self.user)

        order_service.mark_order_as_paid(self.order_id,
                                         PaymentMethod.bank_transfer,
                                         self.admin.id)

    @patch('byceps.email.send')
    def test_email_on_order_paid(self, send_email_mock):
        self.send_event(self.order_id)

        expected_sender = 'acmecon@example.com'
        expected_recipients = [self.user.email_address]
        expected_subject = '\u2705 Deine Bestellung (AC-14-B00022) ist bezahlt worden.'
        expected_body = '''
Hallo Vorbild,

vielen Dank für deine Bestellung mit der Nummer AC-14-B00022 am 23.09.2014 über unsere Website.

Wir haben deine Zahlung erhalten und deine Bestellung als „bezahlt“ erfasst.

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
        created_at = datetime(2014, 9, 23, 18, 40, 53)

        return self.place_order_with_items(self.shop.id, orderer,
                                           'AC-14-B00022', created_at, [])

    def send_event(self, order_id):
        with \
                current_party_set(self.app, self.party), \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_paid.send(None, order_id=order_id)

"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod

from tests.helpers import (
    create_email_config,
    create_user_with_detail,
    current_user_set,
)

from .base import OrderEmailTestBase


class EmailOnOrderPaidTest(OrderEmailTestBase):

    def setUp(self):
        super().setUp()

        create_email_config(sender_address='acmecon@example.com')

        self.shop = self.create_shop()
        self.create_order_number_sequence(self.shop.id, 'AC-14-B', value=21)

        self.create_email_footer_snippet()

        self.user = create_user_with_detail(
            'Vorbild',
            email_address='vorbild@example.com',
        )


        self.order_id = self.place_order(self.user)

        order_service.mark_order_as_paid(
            self.order_id, PaymentMethod.bank_transfer, self.admin.id
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
    def test_email_on_order_paid(self, send_email_mock):
        with \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_email_service \
                .send_email_for_paid_order_to_orderer(self.order_id)

        expected_sender = 'acmecon@example.com'
        expected_recipients = ['vorbild@example.com']
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
            expected_body,
        )

    # helpers

    def place_order(self, orderer):
        created_at = datetime(2014, 9, 23, 18, 40, 53)

        return self.place_order_with_items(
            self.shop.id, orderer, created_at, []
        )

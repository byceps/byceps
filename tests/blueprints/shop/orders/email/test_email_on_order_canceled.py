from unittest.mock import patch

from byceps.blueprints.shop_order.signals import order_canceled
from byceps.database import db
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

        self.user = self.create_user_with_detail('Versager')

        self.order = self.create_order(self.user)

        order_service.cancel_order(self.order, self.admin.id, 'dubious reason')

    @patch('byceps.email.send')
    def test_email_on_order_canceled(self, send_email_mock):
        self.order.cancelation_reason = 'Du hast nicht rechtzeitig bezahlt.'

        self.send_event(self.order.id)

        expected_sender = 'acmecon@example.com'
        expected_recipients = [self.user.email_address]
        expected_subject = 'Deine Bestellung (AC-14-B00017) wurde storniert.'
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

    @patch('byceps.blueprints.shop_order.signals.order_placed.send')
    def create_order(self, orderer, order_placed_mock):
        return self.create_order_with_items(self.shop.id, orderer,
                                            'AC-14-B00017', None, [])

    def send_event(self, order_id):
        with \
                current_party_set(self.app, self.party), \
                current_user_set(self.app, self.user), \
                self.app.app_context():
            order_canceled.send(None, order_id=order_id)

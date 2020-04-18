"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod
from byceps.services.shop.sequence import service as sequence_service

from tests.helpers import create_user_with_detail, current_user_set
from tests.services.shop.helpers import create_shop_fragment

from .base import place_order_with_items


@patch('byceps.email.send')
def test_email_on_order_paid(
    send_email_mock, party_app_with_db, shop, order_admin
):
    app = party_app_with_db

    user = create_user_with_detail(
        'Vorbild', email_address='vorbild@example.com'
    )

    sequence_service.create_order_number_sequence(shop.id, 'AC-14-B', value=21)
    create_email_footer_snippet(shop.id, order_admin.id)

    order_id = place_order(shop.id, user)

    order_service.mark_order_as_paid(
        order_id, PaymentMethod.bank_transfer, order_admin.id
    )

    with current_user_set(app, user), app.app_context():
        order_email_service.send_email_for_paid_order_to_orderer(order_id)

    expected_sender = 'info@shop.example'
    expected_recipients = ['vorbild@example.com']
    expected_subject = (
        '\u2705 Deine Bestellung (AC-14-B00022) ist bezahlt worden.'
    )
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
        expected_sender, expected_recipients, expected_subject, expected_body
    )

    order_service.delete_order(order_id)


# helpers


def create_email_footer_snippet(shop_id, admin_id):
    create_shop_fragment(
        shop_id,
        admin_id,
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


def place_order(shop_id, user):
    created_at = datetime(2014, 9, 23, 18, 40, 53)

    return place_order_with_items(shop_id, user, created_at, [])

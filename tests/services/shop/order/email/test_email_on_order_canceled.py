"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service

from tests.helpers import create_user_with_detail, current_user_set
from tests.services.shop.helpers import create_shop_fragment

from .base import place_order_with_items


@patch('byceps.email.send')
def test_email_on_order_canceled(
    send_email_mock, party_app_with_db, shop, admin_user
):
    app = party_app_with_db

    user = create_user_with_detail(
        'Versager', email_address='versager@example.com'
    )

    sequence_service.create_order_number_sequence(shop.id, 'AC-14-B', value=16)
    create_email_footer_snippet(shop.id, admin_user.id)

    order_id = place_order(shop.id, user)

    reason = 'Du hast nicht rechtzeitig bezahlt.'
    order_service.cancel_order(order_id, admin_user.id, reason)

    with current_user_set(app, user), app.app_context():
        order_email_service.send_email_for_canceled_order_to_orderer(order_id)

    expected_sender = 'info@shop.example'
    expected_recipients = ['versager@example.com']
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
        expected_body,
    )


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
    created_at = datetime(2014, 11, 5, 23, 32, 9)

    return place_order_with_items(shop_id, user, created_at, [])

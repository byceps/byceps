"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.snippet import service as snippet_service
from byceps.services.user import command_service as user_command_service

from tests.helpers import create_user_with_detail, current_user_set
from tests.services.shop.helpers import create_shop_fragment

from .base import place_order_with_items


@pytest.fixture
def customer(party_app):
    user = create_user_with_detail(
        'Versager', email_address='versager@users.test'
    )
    user_id = user.id
    yield user
    user_command_service.delete_account(user_id, user_id, 'clean up')


@pytest.fixture
def order(shop, customer, order_admin):
    sequence_service.create_order_number_sequence(shop.id, 'AC-14-B', value=16)

    email_footer_snippet_id = create_email_footer_snippet(
        shop.id, order_admin.id
    )

    created_at = datetime(2014, 11, 5, 23, 32, 9)

    order = place_order_with_items(shop.id, customer, created_at, [])

    yield order

    snippet_service.delete_snippet(email_footer_snippet_id)
    order_service.delete_order(order.id)
    sequence_service.delete_order_number_sequence(shop.id)


@patch('byceps.email.send')
def test_email_on_order_canceled(
    send_email_mock, party_app, customer, order_admin, order
):
    app = party_app

    reason = 'Du hast nicht rechtzeitig bezahlt.'
    order_service.cancel_order(order.id, order_admin.id, reason)

    with current_user_set(app, customer), app.app_context():
        order_email_service.send_email_for_canceled_order_to_orderer(order.id)

    expected_sender = 'noreply@acmecon.test'
    expected_recipients = ['versager@users.test']
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

E-Mail: noreply@acmecon.test
    '''.strip()

    send_email_mock.assert_called_once_with(
        expected_sender, expected_recipients, expected_subject, expected_body,
    )


# helpers


def create_email_footer_snippet(shop_id, admin_id):
    return create_shop_fragment(
        shop_id,
        admin_id,
        'email_footer',
        '''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
    )

"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import PaymentMethod
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.snippet import service as snippet_service
from byceps.services.user import command_service as user_command_service

from tests.helpers import create_user_with_detail, current_user_set
from tests.services.shop.helpers import create_shop_fragment

from .base import place_order_with_items


@pytest.fixture
def customer(party_app):
    user = create_user_with_detail(
        'Vorbild', email_address='vorbild@example.com'
    )
    user_id = user.id
    yield user
    user_command_service.delete_account(user_id, user_id, 'clean up')


@pytest.fixture
def order(shop, customer, order_admin):
    sequence_service.create_order_number_sequence(shop.id, 'AC-14-B', value=21)

    email_footer_snippet_id = create_email_footer_snippet(
        shop.id, order_admin.id
    )

    created_at = datetime(2014, 9, 23, 18, 40, 53)

    order = place_order_with_items(shop.id, customer, created_at, [])

    yield order

    snippet_service.delete_snippet(email_footer_snippet_id)
    order_service.delete_order(order.id)
    sequence_service.delete_order_number_sequence(shop.id)


@patch('byceps.email.send')
def test_email_on_order_paid(
    send_email_mock, party_app, customer, order_admin, order
):
    app = party_app

    order_service.mark_order_as_paid(
        order.id, PaymentMethod.bank_transfer, order_admin.id
    )

    with current_user_set(app, customer), app.app_context():
        order_email_service.send_email_for_paid_order_to_orderer(order.id)

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

E-Mail: acmecon@example.com
''',
    )

"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
    service as order_service,
)
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.snippet import service as snippet_service

from tests.helpers import current_user_set
from tests.integration.services.shop.helpers import create_shop_fragment

from .helpers import get_current_user_for_user, place_order_with_items


@pytest.fixture
def order_admin(make_user):
    return make_user('PaidEmailShopOrderAdmin')


@pytest.fixture
def customer(make_user_with_detail):
    return make_user_with_detail(
        'Vorbild', email_address='vorbild@users.test'
    )


@pytest.fixture
def order_number_sequence_id(shop) -> None:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop.id, 'AC-14-B', value=21
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture
def storefront(shop, order_number_sequence_id) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront',
        shop.id,
        order_number_sequence_id,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def order(storefront, customer, order_admin):
    email_footer_snippet_id = create_email_footer_snippet(
        storefront.shop_id, order_admin.id
    )

    created_at = datetime(2014, 9, 23, 18, 40, 53)

    order = place_order_with_items(storefront.id, customer, created_at, [])

    yield order

    snippet_service.delete_snippet(email_footer_snippet_id)
    order_service.delete_order(order.id)


@patch('byceps.email.send')
def test_email_on_order_paid(
    send_email_mock, site_app, customer, order_admin, order
):
    app = site_app

    order_service.mark_order_as_paid(order.id, 'bank_transfer', order_admin.id)

    current_user = get_current_user_for_user(customer)
    with current_user_set(app, current_user), app.app_context():
        order_email_service.send_email_for_paid_order_to_orderer(order.id)

    expected_sender = 'noreply@acmecon.test'
    expected_recipients = ['vorbild@users.test']
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

E-Mail: noreply@acmecon.test
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

E-Mail: noreply@acmecon.test
''',
    )

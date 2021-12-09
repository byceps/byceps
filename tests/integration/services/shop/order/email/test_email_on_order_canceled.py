"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Iterator
from unittest.mock import patch

import pytest

from byceps.services.shop.order.email import service as order_email_service
from byceps.services.shop.order import service as order_service
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.shop.storefront.transfer.models import Storefront
from byceps.services.snippet import service as snippet_service

from tests.helpers import current_user_set

from .helpers import (
    assert_email,
    get_current_user_for_user,
    place_order_with_items,
)


@pytest.fixture
def customer(make_user):
    return make_user('Versager', email_address='versager@users.test')


@pytest.fixture
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Iterator[Storefront]:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='CD-22-B', value=16
    )
    storefront = make_storefront(shop.id, order_number_sequence.id)

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def order(storefront, customer, email_footer_snippet_id):
    created_at = datetime(2014, 11, 5, 23, 32, 9)

    order = place_order_with_items(storefront.id, customer, created_at, [])

    yield order

    snippet_service.delete_snippet(email_footer_snippet_id)
    order_service.delete_order(order.id)


@patch('byceps.email.send')
def test_email_on_order_canceled(
    send_email_mock, site_app, customer, order_admin, order
):
    app = site_app

    reason = 'Du hast nicht rechtzeitig bezahlt.'
    order_service.cancel_order(order.id, order_admin.id, reason)

    current_user = get_current_user_for_user(customer, 'de')
    with current_user_set(app, current_user), app.app_context():
        order_email_service.send_email_for_canceled_order_to_orderer(order.id)

    expected_sender = 'noreply@acmecon.test'
    expected_recipients = ['versager@users.test']
    expected_subject = (
        '\u274c Deine Bestellung (CD-22-B00017) ist storniert worden.'
    )
    expected_body = '''
Hallo Versager,

deine Bestellung mit der Nummer CD-22-B00017 vom 06.11.2014 wurde von uns aus folgendem Grund storniert:

Du hast nicht rechtzeitig bezahlt.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
    '''.strip()

    assert_email(
        send_email_mock,
        expected_sender,
        expected_recipients,
        expected_subject,
        expected_body,
    )

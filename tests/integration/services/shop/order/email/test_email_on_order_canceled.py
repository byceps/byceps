"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from byceps.services.brand.models import Brand
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.models.order import Order, Orderer
from byceps.services.shop.order import order_service
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.user.models.user import User

from tests.helpers import current_user_set

from .helpers import (
    assert_email,
    get_current_user_for_user,
    place_order_with_items,
)


@pytest.fixture
def customer(make_user) -> User:
    return make_user('Versager', email_address='versager@users.test')


@pytest.fixture
def orderer(make_orderer, customer: User) -> Orderer:
    return make_orderer(customer.id)


@pytest.fixture
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='CD-22-B', value=16
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def order(storefront: Storefront, orderer: Orderer, email_footer_snippets):
    created_at = datetime(2014, 11, 5, 23, 32, 9)

    return place_order_with_items(storefront.id, orderer, created_at, [])


@patch('byceps.services.email.email_service.send')
def test_email_on_order_canceled(
    send_email_mock,
    site_app,
    customer: User,
    order_admin,
    shop_brand: Brand,
    order: Order,
):
    app = site_app

    reason = 'Du hast nicht rechtzeitig bezahlt.'
    order_service.cancel_order(order.id, order_admin.id, reason).unwrap()

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
das Team der {brand_title}

-- 
{brand_title}

E-Mail: info@acmecon.test
    '''.strip().format(
        brand_title=shop_brand.title
    )

    assert_email(
        send_email_mock,
        expected_sender,
        expected_recipients,
        expected_subject,
        expected_body,
    )

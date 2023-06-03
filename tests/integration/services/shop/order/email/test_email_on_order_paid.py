"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.services.brand.models import Brand
from byceps.services.email.models import NameAndAddress
from byceps.services.shop.order import order_service
from byceps.services.shop.order.email import order_email_service
from byceps.services.shop.order.email.order_email_service import OrderEmailData
from byceps.services.shop.order.models.order import Order, Orderer
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.user.models.user import User

from tests.helpers import current_user_set

from .helpers import get_current_user_for_user, place_order_with_items


@pytest.fixture()
def customer(make_user) -> User:
    return make_user('Vorbild', email_address='vorbild@users.test')


@pytest.fixture()
def orderer(make_orderer, customer: User) -> Orderer:
    return make_orderer(customer.id)


@pytest.fixture()
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='EF-33-B', value=21
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture()
def order(storefront: Storefront, orderer: Orderer, email_footer_snippets):
    created_at = datetime(2014, 9, 23, 18, 40, 53)

    return place_order_with_items(storefront.id, orderer, created_at, [])


def test_email_on_order_paid(
    site_app,
    customer: User,
    order_admin,
    shop_brand: Brand,
    order: Order,
):
    app = site_app

    order_service.mark_order_as_paid(
        order.id, 'bank_transfer', order_admin.id
    ).unwrap()
    order = order_service.get_order(order.id)

    language_code = 'de'
    order_email_data = OrderEmailData(
        order=order,
        brand_id=shop_brand.id,
        orderer=customer,
        orderer_email_address='vorbild@users.test',
        language_code=language_code,
    )
    current_user = get_current_user_for_user(customer, language_code)

    with current_user_set(app, current_user), app.app_context():
        actual = order_email_service.assemble_email_for_paid_order_to_orderer(
            order_email_data
        )

    assert actual.sender == NameAndAddress(
        name=None, address='noreply@acmecon.test'
    )
    assert actual.recipients == ['vorbild@users.test']
    assert (
        actual.subject
        == '\u2705 Deine Bestellung (EF-33-B00022) ist bezahlt worden.'
    )
    assert (
        actual.body
        == '''
Hallo Vorbild,

vielen Dank für deine Bestellung mit der Nummer EF-33-B00022 am 23.09.2014 über unsere Website.

Wir haben deine Zahlung erhalten und deine Bestellung als bezahlt markiert.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der {brand_title}

--\x20
{brand_title}

E-Mail: info@acmecon.test
    '''.strip().format(
            brand_title=shop_brand.title
        )
    )

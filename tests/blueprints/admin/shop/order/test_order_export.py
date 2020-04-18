"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import codecs
from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service

from tests.helpers import (
    assign_permissions_to_user,
    create_user,
    http_client,
    login_user,
)
from tests.services.shop.helpers import create_article as _create_article


@pytest.fixture(scope='module')
def admin_user(app):
    admin = create_user('ShopOrderAdmin')
    authorize_admin(admin.id)
    login_user(admin.id)
    return admin


@pytest.fixture
def article_bungalow(shop):
    return create_article(
        shop.id,
        'LR-08-A00003',
        'LANresort 2015: Bungalow 4 Plätze',
        Decimal('355.00'),
        Decimal('0.07'),
    )


@pytest.fixture
def article_guest_fee(shop):
    return create_article(
        shop.id,
        'LR-08-A00006',
        'Touristische Gästeabgabe (BispingenCard), pauschal für 4 Personen',
        Decimal('6.00'),
        Decimal('0.19'),
    )


@pytest.fixture
def article_table(shop):
    return create_article(
        shop.id,
        'LR-08-A00002',
        'Tisch (zur Miete), 200 x 80 cm',
        Decimal('20.00'),
        Decimal('0.19'),
    )


@pytest.fixture
def cart(article_bungalow, article_guest_fee, article_table):
    cart = Cart()

    cart.add_item(article_bungalow, 1)
    cart.add_item(article_guest_fee, 1)
    cart.add_item(article_table, 2)

    return cart


@pytest.fixture
def orderer():
    user = create_user('Besteller', email_address='h-w.mustermann@example.com')

    return Orderer(
        user.id,
        'Hans-Werner',
        'Mustermann',
        'Deutschland',
        '42000',
        'Hauptstadt',
        'Nebenstraße 23a',
    )


@pytest.fixture
def order_number_sequence(shop) -> None:
    sequence_service.create_order_number_sequence(shop.id, 'LR-08-B', value=26)


@pytest.fixture
def order(shop, order_number_sequence, cart, orderer):
    created_at = datetime(2015, 2, 26, 12, 26, 24)  # UTC

    order, _ = order_service.place_order(
        shop.id, orderer, cart, created_at=created_at
    )

    return order


@freeze_time('2015-04-15 07:54:18')  # UTC
def test_serialize_existing_order(app, shop, order, admin_user):
    filename = 'testfixtures/shop/order_export.xml'
    with codecs.open(filename, encoding='iso-8859-1') as f:
        expected = f.read().rstrip()

    url = f'/admin/shop/orders/{order.id}/export'
    with http_client(app, user_id=admin_user.id) as client:
        response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=iso-8859-1'

    body = response.get_data().decode('utf-8')
    assert body == expected


@freeze_time('2015-04-15 07:54:18')  # UTC
def test_serialize_unknown_order(app, shop, admin_user):
    unknown_order_id = '00000000-0000-0000-0000-000000000000'

    url = f'/admin/shop/orders/{unknown_order_id}/export'
    with http_client(app, user_id=admin_user.id) as client:
        response = client.get(url)

    assert response.status_code == 404


# helpers


def authorize_admin(admin_id):
    permission_ids = {'admin.access', 'shop_order.view'}
    assign_permissions_to_user(admin_id, 'admin', permission_ids)


def create_article(shop_id, item_number, description, price, tax_rate):
    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        tax_rate=tax_rate,
        quantity=10,
    )

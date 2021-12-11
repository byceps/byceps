"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
import pytest

from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.order import Orderer
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront.transfer.models import Storefront

from tests.helpers import login_user
from tests.integration.services.shop.helpers import (
    create_article as _create_article,
)


@pytest.fixture(scope='package')
def shop_order_admin(make_admin):
    permission_ids = {'admin.access', 'shop_order.view'}
    return make_admin('ShopOrderExportAdmin', permission_ids)


@pytest.fixture
def article_bungalow(shop: Shop) -> Article:
    return create_article(
        shop.id,
        'LR-08-A00003',
        'LANresort 2015: Bungalow 4 Plätze',
        Decimal('355.00'),
        Decimal('0.07'),
    )


@pytest.fixture
def article_guest_fee(shop: Shop) -> Article:
    return create_article(
        shop.id,
        'LR-08-A00006',
        'Touristische Gästeabgabe (BispingenCard), pauschal für 4 Personen',
        Decimal('6.00'),
        Decimal('0.19'),
    )


@pytest.fixture
def article_table(shop: Shop) -> Article:
    return create_article(
        shop.id,
        'LR-08-A00002',
        'Tisch (zur Miete), 200 x 80 cm',
        Decimal('20.00'),
        Decimal('0.19'),
    )


@pytest.fixture
def cart(
    article_bungalow: Article,
    article_guest_fee: Article,
    article_table: Article,
) -> Cart:
    cart = Cart()

    cart.add_item(article_bungalow, 1)
    cart.add_item(article_guest_fee, 1)
    cart.add_item(article_table, 2)

    return cart


@pytest.fixture
def orderer(make_user):
    user = make_user(email_address='h-w.mustermann@users.test')

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
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='LR-08-B', value=26
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def order(storefront: Storefront, cart: Cart, orderer):
    created_at = datetime(2015, 2, 26, 12, 26, 24)  # UTC

    order, _ = order_service.place_order(
        storefront.id, orderer, cart, created_at=created_at
    )

    yield order

    order_service.delete_order(order.id)


@freeze_time('2015-04-15 07:54:18')  # UTC
def test_serialize_existing_order(
    request, admin_app, shop_order_admin, make_client, order
):
    filename = request.fspath.dirpath('order_export.xml')
    expected = filename.read_text('iso-8859-1').rstrip()

    login_user(shop_order_admin.id)
    client = make_client(admin_app, user_id=shop_order_admin.id)

    url = f'/admin/shop/orders/{order.id}/export'
    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=iso-8859-1'

    body = response.get_data().decode('utf-8')
    assert body == expected


@freeze_time('2015-04-15 07:54:18')  # UTC
def test_serialize_unknown_order(admin_app, shop_order_admin, make_client):
    unknown_order_id = '00000000-0000-0000-0000-000000000000'

    login_user(shop_order_admin.id)
    client = make_client(admin_app, user_id=shop_order_admin.id)

    url = f'/admin/shop/orders/{unknown_order_id}/export'
    response = client.get(url)

    assert response.status_code == 404


# helpers


def create_article(
    shop_id: ShopID,
    item_number: str,
    description: str,
    price: Decimal,
    tax_rate: Decimal,
) -> Article:
    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        tax_rate=tax_rate,
        total_quantity=10,
    )

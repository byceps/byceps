"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from flask import Flask
from freezegun import freeze_time
from moneyed import EUR, Money
import pytest

from byceps.services.shop.article.models import Article, ArticleNumber
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order.models.order import Order, Orderer
from byceps.services.shop.order import order_checkout_service
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.user.models.user import User

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def shop_order_admin(make_admin) -> User:
    permission_ids = {'admin.access', 'shop_order.view'}
    return make_admin(permission_ids)


@pytest.fixture
def article_bungalow(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('LR-08-A00003'),
        description='LANresort 2015: Bungalow 4 Plätze',
        price=Money('355.00', EUR),
        tax_rate=Decimal('0.07'),
    )


@pytest.fixture
def article_guest_fee(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('LR-08-A00006'),
        description='Touristische Gästeabgabe (BispingenCard), pauschal für 4 Personen',
        price=Money('6.00', EUR),
        tax_rate=Decimal('0.19'),
    )


@pytest.fixture
def article_table(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('LR-08-A00002'),
        description='Tisch (zur Miete), 200 x 80 cm',
        price=Money('20.00', EUR),
        tax_rate=Decimal('0.19'),
    )


@pytest.fixture
def cart(
    article_bungalow: Article,
    article_guest_fee: Article,
    article_table: Article,
) -> Cart:
    cart = Cart(EUR)

    cart.add_item(article_bungalow, 1)
    cart.add_item(article_guest_fee, 1)
    cart.add_item(article_table, 2)

    return cart


@pytest.fixture
def orderer(make_user) -> Orderer:
    user = make_user(email_address='h-w.mustermann@users.test')

    return Orderer(
        user_id=user.id,
        company=None,
        first_name='Hans-Werner',
        last_name='Mustermann',
        country='Deutschland',
        zip_code='42000',
        city='Hauptstadt',
        street='Nebenstraße 23a',
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
def order(storefront: Storefront, cart: Cart, orderer: Orderer):
    created_at = datetime(2015, 2, 26, 12, 26, 24)  # UTC

    order, _ = order_checkout_service.place_order(
        storefront.id, orderer, cart, created_at=created_at
    )

    return order


@freeze_time('2015-04-15 07:54:18')  # UTC
def test_serialize_existing_order(
    request, admin_app: Flask, shop_order_admin: User, make_client, order: Order
):
    filename = request.fspath.dirpath('order_export.xml')
    expected = filename.read_text('iso-8859-1').rstrip()

    log_in_user(shop_order_admin.id)
    client = make_client(admin_app, user_id=shop_order_admin.id)

    url = f'/admin/shop/orders/{order.id}/export'
    response = client.get(url)

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=iso-8859-1'

    body = response.get_data().decode('utf-8')
    assert body == expected


@freeze_time('2015-04-15 07:54:18')  # UTC
def test_serialize_unknown_order(
    admin_app: Flask, shop_order_admin: User, make_client
):
    unknown_order_id = '00000000-0000-0000-0000-000000000000'

    log_in_user(shop_order_admin.id)
    client = make_client(admin_app, user_id=shop_order_admin.id)

    url = f'/admin/shop/orders/{unknown_order_id}/export'
    response = client.get(url)

    assert response.status_code == 404

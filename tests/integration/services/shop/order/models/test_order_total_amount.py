"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from decimal import Decimal
from typing import Iterable

from flask import Flask
import pytest

from byceps.services.shop.article.transfer.models import Article, ArticleNumber
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.order import Order, Orderer
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)

from tests.integration.services.shop.helpers import (
    create_article as _create_article,
    create_orderer,
)


@pytest.fixture(scope='module')
def shop(make_brand, make_email_config, make_shop):
    brand = make_brand()
    email_config = make_email_config(
        brand.id, sender_address='noreply@acmecon.test'
    )

    return make_shop(brand.id)


@pytest.fixture(scope='module')
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def article1(shop: Shop) -> Article:
    return create_article(shop.id, 1, Decimal('49.95'))


@pytest.fixture(scope='module')
def article2(shop: Shop) -> Article:
    return create_article(shop.id, 2, Decimal('6.20'))


@pytest.fixture(scope='module')
def article3(shop: Shop) -> Article:
    return create_article(shop.id, 3, Decimal('12.53'))


@pytest.fixture(scope='module')
def orderer(make_user) -> Orderer:
    user = make_user()
    return create_orderer(user.id)


def test_without_any_items(
    site_app: Flask, storefront: Storefront, orderer: Orderer
):
    order = place_order(storefront.id, orderer, [])

    assert order.total_amount == Decimal('0.00')

    order_service.delete_order(order.id)


def test_with_single_item(
    site_app: Flask, storefront: Storefront, orderer: Orderer, article1: Article
):
    order = place_order(
        storefront.id,
        orderer,
        [
            (article1, 1),
        ],
    )

    assert order.total_amount == Decimal('49.95')

    order_service.delete_order(order.id)


def test_with_multiple_items(
    site_app: Flask,
    storefront: Storefront,
    orderer: Orderer,
    article1: Article,
    article2: Article,
    article3: Article,
):
    order = place_order(
        storefront.id,
        orderer,
        [
            (article1, 3),
            (article2, 1),
            (article3, 4),
        ],
    )

    assert order.total_amount == Decimal('206.17')

    order_service.delete_order(order.id)


# helpers


def create_article(shop_id: ShopID, number: int, price: Decimal) -> Article:
    item_number = ArticleNumber(f'LF-01-A{number:05d}')
    description = f'Artikel #{number:d}'

    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        total_quantity=50,
    )


def place_order(
    storefront_id: StorefrontID,
    orderer: Orderer,
    articles: Iterable[tuple[Article, int]],
) -> Order:
    cart = Cart()
    for article, quantity in articles:
        cart.add_item(article, quantity)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order

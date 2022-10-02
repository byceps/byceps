"""
:Copyright: 2014-2022 Jochen Kupperschmidt
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
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)


@pytest.fixture(scope='module')
def shop(make_brand, make_email_config, make_shop):
    brand = make_brand()
    make_email_config(brand.id, sender_address='noreply@acmecon.test')

    return make_shop(brand.id)


@pytest.fixture(scope='module')
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def article1(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('LF-01-A00001'),
        description='Artikel #1',
        price=Decimal('49.95'),
    )


@pytest.fixture(scope='module')
def article2(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('LF-01-A00002'),
        description='Artikel #2',
        price=Decimal('6.20'),
    )


@pytest.fixture(scope='module')
def article3(make_article, shop: Shop) -> Article:
    return make_article(
        shop.id,
        item_number=ArticleNumber('LF-01-A00003'),
        description='Artikel #3',
        price=Decimal('12.53'),
    )


@pytest.fixture(scope='module')
def orderer(make_user, make_orderer) -> Orderer:
    user = make_user()
    return make_orderer(user.id)


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

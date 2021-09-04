"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

import pytest

from byceps.services.shop.article import service as article_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service

from tests.integration.services.shop.helpers import (
    create_article as _create_article,
    create_orderer,
)


@pytest.fixture
def article1(shop):
    article = create_article(shop.id, 1, Decimal('49.95'))
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def article2(shop):
    article = create_article(shop.id, 2, Decimal('6.20'))
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def article3(shop):
    article = create_article(shop.id, 3, Decimal('12.53'))
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture(scope='module')
def orderer(make_user):
    return create_orderer(make_user('TotalAmountOrderer'))


def test_without_any_items(site_app, storefront, orderer):
    order = place_order(storefront.id, orderer, [])

    assert order.total_amount == Decimal('0.00')

    order_service.delete_order(order.id)


def test_with_single_item(site_app, storefront, orderer, article1):
    order = place_order(storefront.id, orderer, [
        (article1, 1),
    ])

    assert order.total_amount == Decimal('49.95')

    order_service.delete_order(order.id)


def test_with_multiple_items(
    site_app,
    storefront,
    orderer,
    article1,
    article2,
    article3,
):
    order = place_order(storefront.id, orderer, [
        (article1, 3),
        (article2, 1),
        (article3, 4),
    ])

    assert order.total_amount == Decimal('206.17')

    order_service.delete_order(order.id)


# helpers


def create_article(shop_id, number, price):
    item_number = f'LF-01-A{number:05d}'
    description = f'Artikel #{number:d}'

    return _create_article(
        shop_id,
        item_number=item_number,
        description=description,
        price=price,
        total_quantity=50,
    )


def place_order(storefront_id, orderer, articles):
    cart = Cart()
    for article, quantity in articles:
        cart.add_item(article, quantity)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order

"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

import pytest

from byceps.services.shop.article import service as article_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service

from tests.services.shop.helpers import create_article as _create_article


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


def test_without_any_items(party_app, shop, order_number_sequence, orderer):
    order = place_order(shop.id, orderer, [])

    assert order.total_amount == Decimal('0.00')

    order_service.delete_order(order.id)


def test_with_single_item(
    party_app, shop, order_number_sequence, orderer, article1
):
    order = place_order(shop.id, orderer, [
        (article1, 1),
    ])

    assert order.total_amount == Decimal('49.95')

    order_service.delete_order(order.id)


def test_with_multiple_items(
    party_app,
    shop,
    order_number_sequence,
    orderer,
    article1,
    article2,
    article3,
):
    order = place_order(shop.id, orderer, [
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
        quantity=50,
    )


def place_order(shop_id, orderer, articles):
    cart = Cart()
    for article, quantity in articles:
        cart.add_item(article, quantity)

    order, _ = order_service.place_order(shop_id, orderer, cart)

    return order

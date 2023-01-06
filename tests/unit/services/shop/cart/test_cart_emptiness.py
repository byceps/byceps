"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from moneyed import EUR, Money

from byceps.database import generate_uuid
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.shop.transfer.models import ShopID


def test_is_empty_without_items():
    cart = create_empty_cart()

    assert cart.is_empty()


def test_is_empty_with_one_item():
    cart = create_empty_cart()

    add_item(cart, 1)

    assert not cart.is_empty()


def test_is_empty_with_multiple_items():
    cart = create_empty_cart()

    add_item(cart, 3)
    add_item(cart, 1)
    add_item(cart, 6)

    assert not cart.is_empty()


# helpers


def create_empty_cart() -> Cart:
    return Cart(EUR)


def add_item(cart: Cart, quantity: int) -> None:
    article = create_article()
    cart.add_item(article, quantity)


def create_article() -> Article:
    return Article(
        id=ArticleID(generate_uuid()),
        shop_id=ShopID('any-shop'),
        item_number=ArticleNumber('article-123'),
        type_=ArticleType.other,
        type_params={},
        description='Cool thing',
        price=Money('1.99', EUR),
        tax_rate=Decimal('0.19'),
        available_from=None,
        available_until=None,
        total_quantity=1,
        quantity=1,
        max_quantity_per_order=1,
        not_directly_orderable=False,
        separate_order_required=False,
        processing_required=False,
    )

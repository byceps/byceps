"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from moneyed import EUR, Money, USD
from pytest import raises

from byceps.database import generate_uuid
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.shop.transfer.models import ShopID


def test_add_item_with_cart_currency():
    cart = Cart(EUR)
    article = create_article()

    cart.add_item(article, 1)

    assert not cart.is_empty()


def test_add_item_with_different_currency():
    cart = Cart(USD)
    article = create_article()

    with raises(ValueError):
        cart.add_item(article, 1)


# helpers


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

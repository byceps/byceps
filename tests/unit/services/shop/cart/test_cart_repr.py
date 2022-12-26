"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from byceps.database import generate_uuid
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.util.money import Money


def test_cart_empty_repr():
    cart = Cart()
    assert repr(cart) == '<Cart(0 items)>'


def test_cart_filled_repr():
    article1 = create_article(
        ArticleNumber('a-001'), 'Article #1', Decimal('19.99'), Decimal('0.19')
    )
    article2 = create_article(
        ArticleNumber('a-002'), 'Article #2', Decimal('24.99'), Decimal('0.19')
    )

    cart = Cart()
    cart.add_item(article1, 5)
    cart.add_item(article2, 3)

    assert repr(cart) == '<Cart(2 items)>'


# helpers


def create_article(
    item_number: ArticleNumber,
    description: str,
    price_amount: Decimal,
    tax_rate: Decimal,
) -> Article:
    return Article(
        id=ArticleID(generate_uuid()),
        shop_id=ShopID('any-shop'),
        item_number=item_number,
        type_=ArticleType.other,
        type_params={},
        description=description,
        price=Money(price_amount, 'EUR'),
        tax_rate=tax_rate,
        available_from=None,
        available_until=None,
        total_quantity=99,
        quantity=1,
        max_quantity_per_order=10,
        not_directly_orderable=False,
        separate_order_required=False,
        processing_required=False,
    )

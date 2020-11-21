"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from pytest import raises

from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.cart.models import CartItem


def test_init_with_positive_quantity():
    quantity = 1

    item = create_item(quantity)

    assert item.quantity == quantity


def test_init_with_zero_quantity():
    with raises(ValueError):
        create_item(0)


def test_init_with_negative_quantity():
    with raises(ValueError):
        create_item(-1)


# helpers


def create_item(quantity: int) -> CartItem:
    article = create_article()
    return CartItem(article, quantity)


def create_article() -> Article:
    return Article(
        id='00000000-0000-0000-0000-000000000001',
        shop_id='any-shop',
        item_number='article-123',
        description='Cool thing',
        price=Decimal('1.99'),
        tax_rate=Decimal('0.19'),
        available_from=None,
        available_until=None,
        total_quantity=1,
        quantity=1,
        max_quantity_per_order=1,
        not_directly_orderable=False,
        requires_separate_order=False,
        shipping_required=False,
    )

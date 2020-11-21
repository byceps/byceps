"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal

from byceps.services.shop.article.transfer.models import Article
from byceps.services.shop.cart.models import Cart


def test_cart_empty_repr():
    cart = Cart()
    assert repr(cart) == '<Cart(0 items)>'


def test_cart_filled_repr():
    article1 = create_article(
        'a-001', 'Article #1', Decimal('19.99'), Decimal('0.19')
    )
    article2 = create_article(
        'a-002', 'Article #2', Decimal('24.99'), Decimal('0.19')
    )

    cart = Cart()
    cart.add_item(article1, 5)
    cart.add_item(article1, 3)

    assert repr(cart) == '<Cart(2 items)>'


# helpers


def create_article(item_number, description, price, tax_rate):
    return Article(
        id='00000000-0000-0000-0000-000000000001',
        shop_id='any-shop',
        item_number=item_number,
        description=description,
        price=price,
        tax_rate=tax_rate,
        available_from=None,
        available_until=None,
        total_quantity=99,
        quantity=1,
        max_quantity_per_order=10,
        not_directly_orderable=False,
        requires_separate_order=False,
        shipping_required=False,
    )

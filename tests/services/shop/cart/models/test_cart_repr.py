"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from decimal import Decimal

from byceps.services.shop.article.models.article import Article
from byceps.services.shop.cart.models import Cart


def test_cart_empty_repr():
    cart = Cart()
    assert repr(cart) == '<Cart(0 items)>'


def test_cart_filled_repr():
    article1 = Article(
        'leshop', 'a-001', 'Article #1', Decimal('19.99'), Decimal('0.19'), 99
    )
    article2 = Article(
        'leshop', 'a-002', 'Article #2', Decimal('24.99'), Decimal('0.19'), 99
    )

    cart = Cart()
    cart.add_item(article1, 5)
    cart.add_item(article1, 3)

    assert repr(cart) == '<Cart(2 items)>'

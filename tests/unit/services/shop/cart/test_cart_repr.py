"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.services.shop.cart.models import Cart


def test_cart_empty_repr():
    cart = Cart(EUR)
    assert repr(cart) == '<Cart(0 items)>'


def test_cart_filled_repr(make_article):
    article1 = make_article()
    article2 = make_article()

    cart = Cart(EUR)
    cart.add_item(article1, 5)
    cart.add_item(article2, 3)

    assert repr(cart) == '<Cart(2 items)>'

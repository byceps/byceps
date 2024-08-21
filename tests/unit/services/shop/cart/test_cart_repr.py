"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.services.shop.cart.models import Cart


def test_cart_empty_repr():
    cart = Cart(EUR)
    assert repr(cart) == '<Cart(0 items)>'


def test_cart_filled_repr(make_product):
    product1 = make_product()
    product2 = make_product()

    cart = Cart(EUR)
    cart.add_item(product1, 5)
    cart.add_item(product2, 3)

    assert repr(cart) == '<Cart(2 items)>'

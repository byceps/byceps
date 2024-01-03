"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR

from byceps.services.shop.cart.models import Cart


def test_is_empty_without_items():
    cart = create_empty_cart()

    assert cart.is_empty()


def test_is_empty_with_one_item(make_article):
    cart = create_empty_cart()

    cart.add_item(make_article(), 1)

    assert not cart.is_empty()


def test_is_empty_with_multiple_items(make_article):
    cart = create_empty_cart()

    cart.add_item(make_article(), 3)
    cart.add_item(make_article(), 1)
    cart.add_item(make_article(), 6)

    assert not cart.is_empty()


# helpers


def create_empty_cart() -> Cart:
    return Cart(EUR)

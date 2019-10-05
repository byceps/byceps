"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart

from testfixtures.shop_article import create_article


def test_is_empty_without_items():
    cart = Cart()

    assert cart.is_empty()


def test_is_empty_with_one_item():
    cart = Cart()

    add_item(cart, 1)

    assert not cart.is_empty()


def test_is_empty_with_multiple_items():
    cart = Cart()

    add_item(cart, 3)
    add_item(cart, 1)
    add_item(cart, 6)

    assert not cart.is_empty()


# helpers


def add_item(cart, quantity):
    article = create_article('shop-123')
    cart.add_item(article, quantity)

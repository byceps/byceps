"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pytest import raises

from byceps.services.shop.cart.models import CartItem

from testfixtures.shop_article import create_article


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


def create_item(quantity):
    article = create_article('shop-123')
    return CartItem(article, quantity)

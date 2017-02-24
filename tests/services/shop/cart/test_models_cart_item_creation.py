"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools.such import helper

from byceps.services.shop.cart.models import CartItem

from testfixtures.shop_article import create_article


def test_init_with_positive_quantity():
    quantity = 1

    item = create_item(quantity)

    assert item.quantity == quantity


def test_init_with_zero_quantity():
    with helper.assertRaises(ValueError):
        create_item(0)


def test_init_with_negative_quantity():
    with helper.assertRaises(ValueError):
        create_item(-1)


# helpers

def create_item(quantity):
    article = create_article()
    return CartItem(article, quantity)

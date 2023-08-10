"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, USD
import pytest

from byceps.services.shop.cart.models import Cart


def test_add_item_with_cart_currency(make_article):
    cart = Cart(EUR)
    article = make_article()

    cart.add_item(article, 1)

    assert not cart.is_empty()


def test_add_item_with_different_currency(make_article):
    cart = Cart(USD)
    article = make_article()

    with pytest.raises(ValueError):
        cart.add_item(article, 1)

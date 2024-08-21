"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, USD
import pytest

from byceps.services.shop.cart.models import Cart


def test_add_item_with_cart_currency(make_product):
    cart = Cart(EUR)
    product = make_product()

    cart.add_item(product, 1)

    assert not cart.is_empty()


def test_add_item_with_different_currency(make_product):
    cart = Cart(USD)
    product = make_product()

    with pytest.raises(ValueError):
        cart.add_item(product, 1)

"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, Money
import pytest

from byceps.services.shop.cart.models import CartItem


@pytest.mark.parametrize(
    ('quantity', 'expected_line_amount'),
    [
        (1, Money('1.99', EUR)),
        (2, Money('3.98', EUR)),
        (6, Money('11.94', EUR)),
    ],
)
def test_init_with_positive_quantity(
    make_article, quantity: int, expected_line_amount: Money
):
    item = CartItem(make_article(), quantity)

    assert item.quantity == quantity
    assert item.line_amount == expected_line_amount


def test_init_with_zero_quantity(make_article):
    with pytest.raises(ValueError):
        CartItem(make_article(), 0)


def test_init_with_negative_quantity(make_article):
    with pytest.raises(ValueError):
        CartItem(make_article(), -1)

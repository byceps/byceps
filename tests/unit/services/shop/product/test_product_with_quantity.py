"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, Money
import pytest

from byceps.services.shop.product.models import ProductWithQuantity


@pytest.mark.parametrize(
    ('quantity', 'expected_amount'),
    [
        (1, Money('1.99', EUR)),
        (2, Money('3.98', EUR)),
        (6, Money('11.94', EUR)),
    ],
)
def test_init_with_positive_quantity(
    make_product, quantity: int, expected_amount: Money
):
    product = make_product()

    pwq = ProductWithQuantity(product, quantity)

    assert pwq.product == product
    assert pwq.quantity == quantity
    assert pwq.amount == expected_amount


def test_init_with_zero_quantity(make_product):
    with pytest.raises(ValueError):
        ProductWithQuantity(make_product(), 0)


def test_init_with_negative_quantity(make_product):
    with pytest.raises(ValueError):
        ProductWithQuantity(make_product(), -1)

"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR, Money
import pytest

from byceps.services.shop.product import product_domain_service
from byceps.services.shop.product.models import ProductWithQuantity


def test_calculate_total_amount_without_products():
    with pytest.raises(ValueError):
        product_domain_service.calculate_total_amount([])


@pytest.mark.parametrize(
    ('price_strs_and_quantities', 'expected_total_str'),
    [
        (
            [
                ('0.00', 3),
            ],
            '0.00',
        ),
        (
            [
                ('1.99', 2),
            ],
            '3.98',
        ),
        (
            [
                ('1.99', 3),
                ('3.50', 1),
                ('16.25', 8),
            ],
            '139.47',
        ),
    ],
)
def test_calculate_total_amount_with_products(
    make_product, price_strs_and_quantities, expected_total_str: str
):
    products_with_quantities = [
        ProductWithQuantity(make_product(price=Money(price, EUR)), quantity)
        for price, quantity in price_strs_and_quantities
    ]

    expected = Money(expected_total_str, EUR)

    actual = product_domain_service.calculate_total_amount(
        products_with_quantities
    )

    assert actual == expected

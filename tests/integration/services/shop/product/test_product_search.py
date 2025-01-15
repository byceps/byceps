"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.product import product_service


@pytest.fixture(scope='module')
def shop(make_brand, make_shop):
    brand = make_brand()
    return make_shop(brand)


@pytest.fixture(scope='module')
def product1(shop, make_product):
    return make_product(
        shop.id, item_number='TICKET-2022', name='Ticket for 2022'
    )


@pytest.fixture(scope='module')
def product2(shop, make_product):
    return make_product(
        shop.id, item_number='TICKET-2023', name='Ticket for 2023'
    )


@pytest.fixture(scope='module')
def product3(shop, make_product):
    return make_product(
        shop.id, item_number='SHIRT-2023', name='Shirt for 2023'
    )


@pytest.mark.parametrize(
    ('search_term', 'expected_product_numbers'),
    [
        ('2022', {'TICKET-2022'}),
        ('2023', {'TICKET-2023', 'SHIRT-2023'}),
        ('shirt', {'SHIRT-2023'}),
        ('ticket', {'TICKET-2022', 'TICKET-2023'}),
        # match two terms (AND)
        ('shirt 2022', set()),
        ('shirt 2023', {'SHIRT-2023'}),
        ('ticket 2023', {'TICKET-2023'}),
    ],
)
def test_search_multiple_terms(
    admin_app,
    shop,
    product1,
    product2,
    product3,
    search_term,
    expected_product_numbers,
):
    actual = product_service.get_products_for_shop_paginated(
        shop.id, 1, 10, search_term=search_term
    )

    actual_product_numbers = {product.item_number for product in actual.items}

    assert actual_product_numbers == expected_product_numbers

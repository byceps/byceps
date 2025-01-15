"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.product import product_sequence_service


@pytest.fixture(scope='module')
def shop1(make_brand, make_shop):
    brand = make_brand()
    return make_shop(brand)


@pytest.fixture(scope='module')
def shop2(make_brand, make_shop):
    brand = make_brand()
    return make_shop(brand)


def test_generate_product_number_default(admin_app, shop1):
    shop = shop1

    sequence = product_sequence_service.create_product_number_sequence(
        shop.id, 'ONE-01-A'
    ).unwrap()

    actual = product_sequence_service.generate_product_number(
        sequence.id
    ).unwrap()

    assert actual == 'ONE-01-A00001'


def test_generate_product_number_custom(admin_app, shop2):
    shop = shop2

    sequence = product_sequence_service.create_product_number_sequence(
        shop.id, 'TWO-02-A', value=41
    ).unwrap()

    actual = product_sequence_service.generate_product_number(
        sequence.id
    ).unwrap()

    assert actual == 'TWO-02-A00042'

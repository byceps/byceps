"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)


@pytest.fixture(scope='module')
def shop1(make_brand, make_shop):
    brand = make_brand()

    return make_shop(brand.id)


@pytest.fixture(scope='module')
def shop2(make_brand, make_shop):
    brand = make_brand()

    return make_shop(brand.id)


def test_generate_order_number_default(admin_app, shop1):
    shop = shop1

    sequence = order_sequence_service.create_order_number_sequence(
        shop.id, 'ONE-01-B'
    )

    actual = order_sequence_service.generate_order_number(sequence.id)

    assert actual == 'ONE-01-B00001'


def test_generate_order_number_custom(admin_app, shop2):
    shop = shop2

    last_assigned_order_sequence_number = 206

    sequence = order_sequence_service.create_order_number_sequence(
        shop.id, 'LOL-03-B', value=last_assigned_order_sequence_number
    )

    actual = order_sequence_service.generate_order_number(sequence.id)

    assert actual == 'LOL-03-B00207'

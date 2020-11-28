"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service


@pytest.fixture
def shop(brand):
    shop = shop_service.create_shop('shop-01', brand.id, 'Some Shop')

    yield shop

    shop_service.delete_shop(shop.id)


@pytest.fixture
def order_number_sequence_id(shop) -> None:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop.id, 'order-'
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture
def storefront(shop, order_number_sequence_id) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront',
        shop.id,
        order_number_sequence_id,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()

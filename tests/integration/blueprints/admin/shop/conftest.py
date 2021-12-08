"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterator

import pytest

from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)
from byceps.services.shop.order.transfer.models.number import (
    OrderNumberSequenceID,
)
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)

from tests.integration.services.shop.helpers import create_shop


@pytest.fixture(scope='module')
def shop(make_brand):
    brand = make_brand()
    shop = create_shop(brand.id)

    yield shop

    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def order_number_sequence_id(shop) -> Iterator[OrderNumberSequenceID]:
    sequence_id = order_sequence_service.create_order_number_sequence(
        shop.id, 'ORDER-'
    )

    yield sequence_id

    order_sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture(scope='module')
def storefront(shop, order_number_sequence_id) -> Iterator[Storefront]:
    storefront_id = StorefrontID(f'{shop.id}-storefront')

    storefront = storefront_service.create_storefront(
        storefront_id, shop.id, order_number_sequence_id, closed=False
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)

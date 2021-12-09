"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

import pytest

from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
)
from byceps.services.shop.order.transfer.models.number import (
    OrderNumberSequence,
    OrderNumberSequenceID,
)
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)

from tests.helpers import generate_token


@pytest.fixture(scope='session')
def make_order_number_sequence():
    def _wrapper(
        shop_id: ShopID,
        *,
        prefix: Optional[str] = None,
        value: Optional[int] = None,
    ) -> OrderNumberSequence:
        if prefix is None:
            prefix = f'{generate_token()}-O'

        return order_sequence_service.create_order_number_sequence(
            shop_id, prefix, value=value
        )

    return _wrapper


@pytest.fixture(scope='session')
def make_storefront():
    def _wrapper(
        shop_id: ShopID, order_number_sequence_id: OrderNumberSequenceID
    ) -> Storefront:
        storefront_id = StorefrontID(generate_token())
        return storefront_service.create_storefront(
            storefront_id, shop_id, order_number_sequence_id, closed=False
        )

    return _wrapper

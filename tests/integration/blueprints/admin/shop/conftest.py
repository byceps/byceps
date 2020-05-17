"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service


@pytest.fixture(scope='module')
def shop(email_config):
    shop = shop_service.create_shop('shop-01', 'Some Shop', email_config.id)

    yield shop

    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def order_number_sequence_id(shop) -> None:
    sequence_id = sequence_service.create_order_number_sequence(
        shop.id, 'ORDER-'
    )

    yield sequence_id

    sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture(scope='module')
def storefront(shop, order_number_sequence_id) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront',
        shop.id,
        order_number_sequence_id,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)

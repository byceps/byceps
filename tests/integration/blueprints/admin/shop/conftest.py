"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.storefront.transfer.models import Storefront

from tests.integration.services.shop.helpers import create_shop


@pytest.fixture(scope='module')
def shop(make_brand):
    brand = make_brand()

    return create_shop(brand.id)


@pytest.fixture(scope='module')
def storefront(shop, make_order_number_sequence, make_storefront) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)

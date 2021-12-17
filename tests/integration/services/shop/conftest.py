"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.storefront.transfer.models import Storefront


@pytest.fixture
def shop(make_brand, make_email_config, make_shop):
    brand = make_brand()
    email_config = make_email_config(
        brand.id, sender_address='noreply@acmecon.test'
    )

    return make_shop(brand.id)


@pytest.fixture
def storefront(shop, make_order_number_sequence, make_storefront) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()

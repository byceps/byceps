"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.shop.storefront.transfer.models import StorefrontID

from tests.integration.services.shop.helpers import create_shop


@pytest.fixture
def shop(make_brand, make_email_config):
    brand = make_brand()
    email_config = make_email_config(
        brand.id, sender_address='noreply@acmecon.test'
    )

    return create_shop(brand.id)


@pytest.fixture
def storefront(shop, make_order_number_sequence):
    storefront_id = StorefrontID(f'{shop.id}-storefront')
    order_number_sequence = make_order_number_sequence(shop.id)

    storefront = storefront_service.create_storefront(
        storefront_id, shop.id, order_number_sequence.id, closed=False
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()

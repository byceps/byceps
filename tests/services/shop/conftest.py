"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.email import service as email_service
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service

from testfixtures.shop_order import create_orderer

from tests.helpers import create_user_with_detail


@pytest.fixture
def email_config():
    config_id = 'email-config-01'
    sender_address = 'info@shop.example'

    email_service.set_config(config_id, sender_address)

    return email_service.get_config(config_id)


@pytest.fixture
def shop(email_config):
    return shop_service.create_shop('shop-01', 'Some Shop', email_config.id)


@pytest.fixture
def orderer(normal_user):
    user = create_user_with_detail('Besteller')
    return create_orderer(user)


@pytest.fixture
def empty_cart() -> Cart:
    return Cart()


@pytest.fixture
def order_number_sequence(shop) -> None:
    sequence_service.create_order_number_sequence(shop.id, 'order-')

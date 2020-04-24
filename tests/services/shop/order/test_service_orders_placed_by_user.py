"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service

from testfixtures.shop_order import create_orderer as _create_orderer

from tests.helpers import create_user_with_detail
from tests.services.shop.helpers import create_shop


@pytest.fixture
def shop1(email_config):
    shop = create_shop('first-nice-shop')
    sequence_service.create_order_number_sequence(shop.id, 'LF-02-B')

    yield shop

    sequence_service.delete_order_number_sequence(shop.id)
    shop_service.delete_shop(shop.id)


@pytest.fixture
def shop2(email_config):
    shop = create_shop('second-nice-shop')
    sequence_service.create_order_number_sequence(shop.id, 'LF-03-B')

    yield shop

    sequence_service.delete_order_number_sequence(shop.id)
    shop_service.delete_shop(shop.id)


@pytest.fixture
def orderer1(admin_app):
    return create_orderer('Orderer1')


@pytest.fixture
def orderer2(admin_app):
    return create_orderer('Orderer2')


def test_get_orders_placed_by_user(admin_app, shop1, shop2, orderer1, orderer2):
    order1 = place_order(shop1.id, orderer1)
    order2 = place_order(shop1.id, orderer2)  # different user
    order3 = place_order(shop1.id, orderer1)
    order4 = place_order(shop1.id, orderer1)
    order5 = place_order(shop2.id, orderer1)  # different shop

    orders_orderer1_shop1 = get_orders_by_user(orderer1, shop1.id)
    assert orders_orderer1_shop1 == [order4, order3, order1]

    orders_orderer2_shop1 = get_orders_by_user(orderer2, shop1.id)
    assert orders_orderer2_shop1 == [order2]

    orders_orderer1_shop2 = get_orders_by_user(orderer1, shop2.id)
    assert orders_orderer1_shop2 == [order5]

    for order in order1, order2, order3, order4, order5:
        order_service.delete_order(order.id)


# helpers


def create_orderer(screen_name):
    user = create_user_with_detail(screen_name)
    return _create_orderer(user)


def place_order(shop_id, orderer):
    cart = Cart()

    order, _ = order_service.place_order(shop_id, orderer, cart)

    return order


def get_orders_by_user(orderer, shop_id):
    return order_service.get_orders_placed_by_user_for_shop(
        orderer.user_id, shop_id
    )

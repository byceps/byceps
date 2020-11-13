"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import (
    sequence_service as order_sequence_service,
    service as order_service,
)
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service

from testfixtures.shop_order import create_orderer

from tests.integration.services.shop.helpers import create_shop


@pytest.fixture
def storefront1(email_config):
    shop = create_shop('first-nice-shop')
    order_number_sequence_id = (
        order_sequence_service.create_order_number_sequence(shop.id, 'LF-02-B')
    )
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront',
        shop.id,
        order_number_sequence_id,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)
    order_sequence_service.delete_order_number_sequence(
        order_number_sequence_id
    )
    shop_service.delete_shop(shop.id)


@pytest.fixture
def storefront2(email_config):
    shop = create_shop('second-nice-shop')
    order_number_sequence_id = (
        order_sequence_service.create_order_number_sequence(shop.id, 'LF-03-B')
    )
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront',
        shop.id,
        order_number_sequence_id,
        closed=False,
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)
    order_sequence_service.delete_order_number_sequence(
        order_number_sequence_id
    )
    shop_service.delete_shop(shop.id)


@pytest.fixture(scope='module')
def orderer1(make_user_with_detail):
    user = make_user_with_detail('Orderer1')
    return create_orderer(user)


@pytest.fixture(scope='module')
def orderer2(make_user_with_detail):
    user = make_user_with_detail('Orderer2')
    return create_orderer(user)


def test_get_orders_placed_by_user(
    admin_app, storefront1, storefront2, orderer1, orderer2
):
    order1 = place_order(storefront1.id, orderer1)
    order2 = place_order(storefront1.id, orderer2)  # different user
    order3 = place_order(storefront1.id, orderer1)
    order4 = place_order(storefront1.id, orderer1)
    order5 = place_order(storefront2.id, orderer1)  # different shop

    orders_orderer1_shop1 = get_orders_by_user(orderer1, storefront1.shop_id)
    assert orders_orderer1_shop1 == [order4, order3, order1]

    orders_orderer2_shop1 = get_orders_by_user(orderer2, storefront1.shop_id)
    assert orders_orderer2_shop1 == [order2]

    orders_orderer1_shop2 = get_orders_by_user(orderer1, storefront2.shop_id)
    assert orders_orderer1_shop2 == [order5]

    for order in order1, order2, order3, order4, order5:
        order_service.delete_order(order.id)


# helpers


def place_order(storefront_id, orderer):
    cart = Cart()

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order


def get_orders_by_user(orderer, shop_id):
    return order_service.get_orders_placed_by_user_for_shop(
        orderer.user_id, shop_id
    )

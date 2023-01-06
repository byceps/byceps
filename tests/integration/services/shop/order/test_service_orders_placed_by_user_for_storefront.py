"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR
import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_service
from byceps.services.shop.order.transfer.order import Order, Orderer
from byceps.services.shop.shop.transfer.models import Shop
from byceps.services.shop.storefront.transfer.models import (
    Storefront,
    StorefrontID,
)


@pytest.fixture
def shop(make_brand, make_shop) -> Shop:
    brand = make_brand()

    return make_shop(brand.id)


@pytest.fixture
def storefront1(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='LF-02-B'
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture
def storefront2(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='LF-03-B'
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def orderer1(make_user, make_orderer) -> Orderer:
    user = make_user()
    return make_orderer(user.id)


@pytest.fixture(scope='module')
def orderer2(make_user, make_orderer) -> Orderer:
    user = make_user()
    return make_orderer(user.id)


def test_get_orders_placed_by_user(
    admin_app,
    storefront1: Storefront,
    storefront2: Storefront,
    orderer1: Orderer,
    orderer2: Orderer,
):
    order1 = place_order(storefront1.id, orderer1)
    order2 = place_order(storefront1.id, orderer2)  # different user
    order3 = place_order(storefront1.id, orderer1)
    order4 = place_order(storefront1.id, orderer1)
    order5 = place_order(storefront2.id, orderer1)  # different storefront

    orders_orderer1_storefront1 = get_orders_by_user(orderer1, storefront1.id)
    assert orders_orderer1_storefront1 == [order4, order3, order1]

    orders_orderer2_storefront1 = get_orders_by_user(orderer2, storefront1.id)
    assert orders_orderer2_storefront1 == [order2]

    orders_orderer1_storefront2 = get_orders_by_user(orderer1, storefront2.id)
    assert orders_orderer1_storefront2 == [order5]


# helpers


def place_order(storefront_id: StorefrontID, orderer: Orderer) -> Order:
    cart = Cart(EUR)

    order, _ = order_service.place_order(storefront_id, orderer, cart)

    return order


def get_orders_by_user(
    orderer: Orderer, storefront_id: StorefrontID
) -> list[Order]:
    return order_service.get_orders_placed_by_user_for_storefront(
        orderer.user_id, storefront_id
    )

"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import EUR
import pytest

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.order.models.order import Order, Orderer, OrderID
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront, StorefrontID


@pytest.fixture()
def shop(make_brand, make_shop) -> Shop:
    brand = make_brand()

    return make_shop(brand.id)


@pytest.fixture()
def storefront1(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='LF-02-B'
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture()
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
    return make_orderer(user)


@pytest.fixture(scope='module')
def orderer2(make_user, make_orderer) -> Orderer:
    user = make_user()
    return make_orderer(user)


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

    assert get_order_ids_by_user(orderer1, storefront1.id) == {
        order4.id,
        order3.id,
        order1.id,
    }
    assert get_order_ids_by_user(orderer2, storefront1.id) == {order2.id}
    assert get_order_ids_by_user(orderer1, storefront2.id) == {order5.id}


# helpers


def place_order(storefront_id: StorefrontID, orderer: Orderer) -> Order:
    cart = Cart(EUR)

    order, _ = order_checkout_service.place_order(
        storefront_id, orderer, cart
    ).unwrap()

    return order


def get_order_ids_by_user(
    orderer: Orderer, storefront_id: StorefrontID
) -> set[OrderID]:
    orders = order_service.get_orders_placed_by_user_for_storefront(
        orderer.user.id, storefront_id
    )
    return {order.id for order in orders}

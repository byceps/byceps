"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service

from testfixtures.shop_order import create_orderer as _create_orderer

from tests.helpers import create_user_with_detail
from tests.services.shop.helpers import create_shop


def test_get_orders_placed_by_user(admin_app_with_db, email_config):
    shop1_id = create_shop('first-nice-shop').id
    shop2_id = create_shop('second-nice-shop').id

    sequence_service.create_order_number_sequence(shop1_id, 'LF-02-B')
    sequence_service.create_order_number_sequence(shop2_id, 'LF-03-B')

    orderer1 = create_orderer('User1')
    orderer2 = create_orderer('User2')

    order1 = place_order(shop1_id, orderer1)
    order2 = place_order(shop1_id, orderer2)  # different user
    order3 = place_order(shop1_id, orderer1)
    order4 = place_order(shop1_id, orderer1)
    order5 = place_order(shop2_id, orderer1)  # different shop

    orders_orderer1_shop1 = get_orders_by_user(orderer1, shop1_id)
    assert orders_orderer1_shop1 == [order4, order3, order1]

    orders_orderer2_shop1 = get_orders_by_user(orderer2, shop1_id)
    assert orders_orderer2_shop1 == [order2]

    orders_orderer1_shop2 = get_orders_by_user(orderer1, shop2_id)
    assert orders_orderer1_shop2 == [order5]

    for order in order1, order2, order3, order4, order5:
        order_service.delete_order(order.id)


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

"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import (
    PaymentMethod,
    PaymentState,
)


@pytest.fixture
def order(admin_app_with_db, shop, order_number_sequence, orderer, empty_cart):
    order, _ = order_service.place_order(shop.id, orderer, empty_cart)
    return order


def test_mark_order_as_paid(order, admin_user):
    order_before = order
    assert order_before.payment_method is None
    assert order_before.payment_state == PaymentState.open
    assert order_before.is_open
    assert not order_before.is_paid

    order_service.mark_order_as_paid(
        order.id, PaymentMethod.cash, admin_user.id
    )

    order_after = order_service.find_order(order.id)
    assert order_after.payment_method == PaymentMethod.cash
    assert order_after.payment_state == PaymentState.paid
    assert not order_after.is_open
    assert order_after.is_paid

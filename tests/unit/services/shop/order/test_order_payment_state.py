"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.models.order import Order as DbOrder
from byceps.services.shop.order.transfer.models import OrderNumber, PaymentState
from byceps.services.user.models.user import User as DbUser

from testfixtures.user import create_user


def test_is_open():
    payment_state = PaymentState.open

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == True
    assert order.is_canceled == False
    assert order.is_paid == False


def test_is_canceled():
    payment_state = PaymentState.canceled_before_paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == False
    assert order.is_canceled == True
    assert order.is_paid == False


def test_is_paid():
    payment_state = PaymentState.paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == False
    assert order.is_canceled == False
    assert order.is_paid == True


def test_is_canceled_after_paid():
    payment_state = PaymentState.canceled_after_paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == False
    assert order.is_canceled == True
    assert order.is_paid == False


# helpers


def create_order_with_payment_state(payment_state: PaymentState) -> DbOrder:
    shop_id = 'shop-123'
    order_number = 'AEC-03-B00074'
    placed_by = create_user()

    order = DbOrder(
        shop_id,
        order_number,
        placed_by.id,
        placed_by.detail.first_names,
        placed_by.detail.last_name,
        placed_by.detail.country,
        placed_by.detail.zip_code,
        placed_by.detail.city,
        placed_by.detail.street,
    )

    order.payment_state = payment_state

    return order

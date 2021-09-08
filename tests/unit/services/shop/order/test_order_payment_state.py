"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import (
    Order,
    Orderer,
    OrderNumber,
    PaymentState,
)


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


def create_order_with_payment_state(payment_state: PaymentState) -> Order:
    shop_id = 'shop-123'
    order_number = 'AEC-03-B00074'
    orderer = create_orderer()
    created_at = None

    order = order_service._build_order(
        shop_id, order_number, orderer, created_at
    )
    order.payment_state = payment_state

    return order_service._order_to_transfer_object(order)


def create_orderer() -> Orderer:
    return Orderer(
        user_id='d8a9c61c-2286-41b3-85ae-7d9f7a2f3357',
        first_names='John Joseph',
        last_name='Doe',
        country='State of Mind',
        zip_code='31337',
        city='Atrocity',
        street='Elite Street 1337',
    )

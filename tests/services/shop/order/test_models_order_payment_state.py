"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.shop.order.models import PaymentState

from testfixtures.shop_order import create_order
from testfixtures.user import create_user


def test_is_open():
    payment_state = PaymentState.open

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == True
    assert order.is_canceled == False
    assert order.is_paid == False


def test_is_open():
    payment_state = PaymentState.canceled

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == False
    assert order.is_canceled == True
    assert order.is_paid == False


def test_is_open():
    payment_state = PaymentState.paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open == False
    assert order.is_canceled == False
    assert order.is_paid == True


# helpers

def create_order_with_payment_state(payment_state):
    user = create_user(42)

    party_id = 'acme-party-2016'
    placed_by = user

    order = create_order(party_id, placed_by)
    order.payment_state = payment_state

    return order

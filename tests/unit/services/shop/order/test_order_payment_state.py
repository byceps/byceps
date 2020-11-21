"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.shop.order.models.order import Order as DbOrder
from byceps.services.shop.order.service import _build_order
from byceps.services.shop.order.transfer.models import OrderNumber, PaymentState
from byceps.services.user.models.user import User as DbUser
from byceps.services.user.models.detail import UserDetail as DbUserDetail

from tests.integration.services.shop.helpers import create_orderer


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
    orderer = create_orderer(placed_by)
    created_at = None

    order = _build_order(shop_id, order_number, orderer, created_at)
    order.payment_state = payment_state

    return order


def create_user(
    screen_name='Faith',
    *,
    first_names='John Joseph',
    last_name='Doe',
    country='State of Mind',
    zip_code='31337',
    city='Atrocity',
    street='Elite Street 1337',
):
    created_at = datetime.utcnow()
    screen_name = 'HerrDamit'
    email_address = 'herr.damit@users.test'

    user = DbUser(created_at, screen_name, email_address)
    detail = DbUserDetail(user=user)

    return user

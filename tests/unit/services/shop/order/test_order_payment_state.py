"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from moneyed import EUR

from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import (
    Order,
    Orderer,
    PaymentState,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.typing import UserID


def test_is_open():
    payment_state = PaymentState.open

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert order.is_open
    assert not order.is_canceled
    assert not order.is_paid


def test_is_canceled():
    payment_state = PaymentState.canceled_before_paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert not order.is_open
    assert order.is_canceled
    assert not order.is_paid


def test_is_paid():
    payment_state = PaymentState.paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert not order.is_open
    assert not order.is_canceled
    assert order.is_paid


def test_is_canceled_after_paid():
    payment_state = PaymentState.canceled_after_paid

    order = create_order_with_payment_state(payment_state)

    assert order.payment_state == payment_state
    assert not order.is_open
    assert order.is_canceled
    assert not order.is_paid


# helpers


def create_order_with_payment_state(payment_state: PaymentState) -> Order:
    shop_id = ShopID('shop-123')
    storefront_id = StorefrontID('storefront-123')
    order_number = OrderNumber('AEC-03-B00074')
    orderer = create_orderer()
    created_at = datetime.utcnow()

    db_order = order_checkout_service._build_order(
        created_at, shop_id, storefront_id, order_number, orderer, EUR
    )
    db_order.payment_state = payment_state

    return order_service._order_to_transfer_object(db_order)


def create_orderer() -> Orderer:
    return Orderer(
        user_id=UserID(UUID('d8a9c61c-2286-41b3-85ae-7d9f7a2f3357')),
        company='JJD, LLC',
        first_name='John Joseph',
        last_name='Doe',
        country='State of Mind',
        zip_code='31337',
        city='Atrocity',
        street='Elite Street 1337',
    )

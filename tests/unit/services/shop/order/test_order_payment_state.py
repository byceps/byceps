"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from moneyed import EUR

from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.order.models.checkout import IncomingOrder
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import (
    Order,
    Orderer,
    PaymentState,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID


def test_is_open(orderer):
    payment_state = PaymentState.open

    order = create_order_with_payment_state(orderer, payment_state)

    assert order.payment_state == payment_state
    assert order.is_open
    assert not order.is_canceled
    assert not order.is_paid


def test_is_canceled(orderer):
    payment_state = PaymentState.canceled_before_paid

    order = create_order_with_payment_state(orderer, payment_state)

    assert order.payment_state == payment_state
    assert not order.is_open
    assert order.is_canceled
    assert not order.is_paid


def test_is_paid(orderer):
    payment_state = PaymentState.paid

    order = create_order_with_payment_state(orderer, payment_state)

    assert order.payment_state == payment_state
    assert not order.is_open
    assert not order.is_canceled
    assert order.is_paid


def test_is_canceled_after_paid(orderer):
    payment_state = PaymentState.canceled_after_paid

    order = create_order_with_payment_state(orderer, payment_state)

    assert order.payment_state == payment_state
    assert not order.is_open
    assert order.is_canceled
    assert not order.is_paid


# helpers


def create_order_with_payment_state(
    orderer: Orderer, payment_state: PaymentState
) -> Order:
    order_number = OrderNumber('AEC-03-B00074')
    created_at = datetime.utcnow()

    incoming_order = IncomingOrder(
        created_at=created_at,
        shop_id=ShopID('shop-123'),
        storefront_id=StorefrontID('storefront-123'),
        orderer=orderer,
        line_items=[],
        total_amount=EUR.zero,
        processing_required=False,
    )

    db_order = order_checkout_service._build_db_order(
        incoming_order, order_number
    )
    db_order.payment_state = payment_state

    return order_service._order_to_transfer_object(db_order, orderer.user)

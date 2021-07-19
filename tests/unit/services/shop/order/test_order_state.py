"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

import pytest

from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models import (
    Order,
    OrderNumber,
    OrderState,
    PaymentState,
)
from byceps.services.shop.shop.transfer.models import ShopID


SHIPPING_REQUIRED = True
SHIPPED = True


@pytest.mark.parametrize(
    'payment_state, shipping_required, shipped, expected',
    [
        (PaymentState.open,                 not SHIPPING_REQUIRED,  not SHIPPED, OrderState.open    ),
        (PaymentState.open,                     SHIPPING_REQUIRED,  not SHIPPED, OrderState.open    ),
        (PaymentState.open,                     SHIPPING_REQUIRED,      SHIPPED, OrderState.open    ),
        (PaymentState.canceled_before_paid, not SHIPPING_REQUIRED,  not SHIPPED, OrderState.canceled),
        (PaymentState.canceled_before_paid,     SHIPPING_REQUIRED,  not SHIPPED, OrderState.canceled),
        (PaymentState.canceled_before_paid,     SHIPPING_REQUIRED,      SHIPPED, OrderState.canceled),
        (PaymentState.canceled_after_paid,  not SHIPPING_REQUIRED,  not SHIPPED, OrderState.canceled),
        (PaymentState.canceled_after_paid,      SHIPPING_REQUIRED,  not SHIPPED, OrderState.canceled),
        (PaymentState.canceled_after_paid,      SHIPPING_REQUIRED,      SHIPPED, OrderState.canceled),
        (PaymentState.paid,                 not SHIPPING_REQUIRED,  not SHIPPED, OrderState.complete),
        (PaymentState.paid,                     SHIPPING_REQUIRED,  not SHIPPED, OrderState.open    ),
        (PaymentState.paid,                     SHIPPING_REQUIRED,      SHIPPED, OrderState.complete),
    ],
)
def test_order_state(
    payment_state: PaymentState,
    shipping_required: bool,
    shipped: bool,
    expected: OrderState,
):
    order = create_order(payment_state, shipping_required, shipped)
    assert order.state == expected


# helpers


def create_order(
    payment_state: PaymentState, shipping_required: bool, shipped: bool
) -> Order:
    shop_id = ShopID('shop-123')
    order_number = OrderNumber('ORDER-42')
    orderer = create_orderer()
    created_at = datetime.utcnow()

    order = order_service._build_order(
        shop_id, order_number, orderer, created_at
    )
    order.payment_state = payment_state
    order.shipping_required = shipping_required
    order.shipped_at = created_at if shipped else None

    return order_service._order_to_transfer_object(order)


def create_orderer() -> Orderer:
    return Orderer(
        user_id='937a2112-62b5-4824-b5c0-430396b94591',
        first_names='Burkhardt',
        last_name='Playhardt',
        country='Country',
        zip_code='55555',
        city='City',
        street='Street',
    )

"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

import pytest

from byceps.services.shop.order import service as order_service
from byceps.services.shop.order.transfer.models.order import (
    Order,
    Orderer,
    OrderNumber,
    OrderState,
    PaymentState,
)
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.services.shop.storefront.transfer.models import StorefrontID
from byceps.typing import UserID


PROCESSING_REQUIRED = True
PROCESSED = True


@pytest.mark.parametrize(
    'payment_state, processing_required, processed, expected',
    [
        (PaymentState.open,                 not PROCESSING_REQUIRED,  not PROCESSED, OrderState.open    ),
        (PaymentState.open,                     PROCESSING_REQUIRED,  not PROCESSED, OrderState.open    ),
        (PaymentState.open,                     PROCESSING_REQUIRED,      PROCESSED, OrderState.open    ),
        (PaymentState.canceled_before_paid, not PROCESSING_REQUIRED,  not PROCESSED, OrderState.canceled),
        (PaymentState.canceled_before_paid,     PROCESSING_REQUIRED,  not PROCESSED, OrderState.canceled),
        (PaymentState.canceled_before_paid,     PROCESSING_REQUIRED,      PROCESSED, OrderState.canceled),
        (PaymentState.canceled_after_paid,  not PROCESSING_REQUIRED,  not PROCESSED, OrderState.canceled),
        (PaymentState.canceled_after_paid,      PROCESSING_REQUIRED,  not PROCESSED, OrderState.canceled),
        (PaymentState.canceled_after_paid,      PROCESSING_REQUIRED,      PROCESSED, OrderState.canceled),
        (PaymentState.paid,                 not PROCESSING_REQUIRED,  not PROCESSED, OrderState.complete),
        (PaymentState.paid,                     PROCESSING_REQUIRED,  not PROCESSED, OrderState.open    ),
        (PaymentState.paid,                     PROCESSING_REQUIRED,      PROCESSED, OrderState.complete),
    ],
)
def test_order_state(
    payment_state: PaymentState,
    processing_required: bool,
    processed: bool,
    expected: OrderState,
):
    order = create_order(payment_state, processing_required, processed)
    assert order.state == expected


# helpers


def create_order(
    payment_state: PaymentState, processing_required: bool, processed: bool
) -> Order:
    shop_id = ShopID('shop-123')
    storefront_id = StorefrontID('storefront-123')
    order_number = OrderNumber('ORDER-42')
    orderer = create_orderer()
    created_at = datetime.utcnow()

    order = order_service._build_order(
        shop_id, storefront_id, order_number, orderer, created_at
    )
    order.payment_state = payment_state
    order.processing_required = processing_required
    order.processed_at = created_at if processed else None

    return order_service._order_to_transfer_object(order)


def create_orderer() -> Orderer:
    return Orderer(
        user_id=UserID(UUID('937a2112-62b5-4824-b5c0-430396b94591')),
        first_names='Burkhardt',
        last_name='Playhardt',
        country='Country',
        zip_code='55555',
        city='City',
        street='Street',
    )

"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from moneyed import EUR
import pytest

from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import (
    Order,
    Orderer,
    OrderState,
    PaymentState,
)
from byceps.services.shop.order import order_service
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
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

    db_order = order_service._build_order(
        created_at, shop_id, storefront_id, order_number, orderer, EUR
    )
    db_order.payment_state = payment_state
    db_order.processing_required = processing_required
    db_order.processed_at = created_at if processed else None

    return order_service._order_to_transfer_object(db_order)


def create_orderer() -> Orderer:
    return Orderer(
        user_id=UserID(UUID('937a2112-62b5-4824-b5c0-430396b94591')),
        company=None,
        first_name='Burkhardt',
        last_name='Playhardt',
        country='Country',
        zip_code='55555',
        city='City',
        street='Street',
    )

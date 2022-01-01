"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from freezegun import freeze_time
import pytest

from byceps.services.shop.order.transfer.number import OrderNumber
from byceps.services.shop.order.transfer.order import (
    Address,
    Order,
    OrderID,
    OrderState,
    PaymentState,
)
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.services.shop.storefront.transfer.models import StorefrontID
from byceps.typing import UserID


@pytest.mark.parametrize(
    'created_at, payment_state, expected',
    [
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.open,                 True),
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.canceled_before_paid, True),
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.paid,                 True),
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.canceled_after_paid,  True),
        (datetime(2021, 6, 13, 20, 0, 0), PaymentState.open,                 False),
        (datetime(2021, 6, 13, 20, 0, 1), PaymentState.open,                 False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.open,                 False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.canceled_before_paid, False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.paid,                 False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.canceled_after_paid,  False),
    ],
)
def test_is_overdue(
    created_at: datetime, payment_state: PaymentState, expected: bool
):
    order = create_order(created_at)

    with freeze_time(datetime(2021, 6, 27, 20, 0, 0)) as now:
        assert order.is_overdue == expected


def create_order(created_at: datetime) -> Order:
    return Order(
        id=OrderID(UUID('000414c5-4474-4f5a-970a-47fd286557d4')),
        created_at=created_at,
        shop_id=ShopID('anyshop'),
        storefront_id=StorefrontID('anyshop-99'),
        order_number=OrderNumber('ORDER-31337'),
        placed_by_id=UserID(UUID('b1a18832-22d4-4df5-8077-848611633332')),
        first_names='n/a',
        last_name='n/a',
        address=Address('n/a', 'n/a', 'n/a', 'n/a'),
        total_amount=Decimal('31337.00'),
        line_items=[],
        payment_method=None,
        payment_state=PaymentState.open,
        state=OrderState.open,
        is_open=True,
        is_canceled=False,
        is_paid=False,
        is_invoiced=False,
        is_processing_required=False,
        is_processed=False,
        cancelation_reason=None,
    )

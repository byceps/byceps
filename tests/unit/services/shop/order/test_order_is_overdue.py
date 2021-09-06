"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.shop.order.transfer.models import (
    Order,
    OrderState,
    PaymentState,
)


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
        id=None,
        shop_id=None,
        order_number=None,
        created_at=created_at,
        placed_by_id=None,
        first_names=None,
        last_name=None,
        address=None,
        total_amount=None,
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

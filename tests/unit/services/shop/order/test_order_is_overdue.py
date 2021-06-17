"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.shop.order.transfer.models import Order, PaymentState


@pytest.mark.parametrize(
    'created_at, expected',
    [
        (datetime(2021, 6, 12, 12, 0, 0), True),
        (datetime(2021, 6, 13, 20, 0, 0), False),
        (datetime(2021, 6, 13, 20, 0, 1), False),
        (datetime(2021, 6, 14, 12, 0, 0), False),
    ],
)
def test_is_overdue(created_at, expected):
    order = create_order(created_at)

    with freeze_time(datetime(2021, 6, 27, 20, 0, 0)) as now:
        print('\n', order, now)
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
        items=[],
        payment_method=None,
        payment_state=PaymentState.open,
        is_open=True,
        is_canceled=False,
        is_paid=False,
        is_invoiced=False,
        is_shipping_required=False,
        is_shipped=False,
        cancelation_reason=None,
    )

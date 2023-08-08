"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from freezegun import freeze_time
import pytest

from byceps.services.shop.order import order_domain_service
from byceps.services.shop.order.models.order import PaymentState


@pytest.mark.parametrize(
    ('checked_at', 'payment_state', 'expected'),
    [
        (datetime(2021, 6, 25, 11, 59, 59), PaymentState.open,                 False ),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.open,                 True ),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.canceled_before_paid, False),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.paid,                 False),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.canceled_after_paid,  False),
        (datetime(2021, 6, 25, 12,  0,  1), PaymentState.open,                 True ),
    ],
)
def test_is_overdue(
    checked_at: datetime, payment_state: PaymentState, expected: bool
):
    created_at = datetime(2021, 6, 11, 12, 0, 0)

    with freeze_time(checked_at):
        assert (
            order_domain_service.is_overdue(created_at, payment_state)
            == expected
        )

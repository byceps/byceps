"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.blueprints.admin.shop.order.models import OrderStateFilter
from byceps.services.shop.order.models.order import PaymentState


@pytest.mark.parametrize(
    ('only_payment_state', 'only_overdue', 'only_processed', 'expected'),
    [
        (None,                              None,  None,  OrderStateFilter.none),
        (PaymentState.open,                 False, None,  OrderStateFilter.payment_state_open),
        (PaymentState.open,                 True,  None,  OrderStateFilter.payment_state_open_and_overdue),
        (PaymentState.open,                 None,  None,  OrderStateFilter.payment_state_open),
        (PaymentState.canceled_before_paid, None,  None,  OrderStateFilter.payment_state_canceled_before_paid),
        (PaymentState.paid,                 None,  None,  OrderStateFilter.payment_state_paid),
        (PaymentState.canceled_after_paid,  None,  None,  OrderStateFilter.payment_state_canceled_after_paid),
        (PaymentState.paid,                 None,  False, OrderStateFilter.waiting_for_processing),
        (PaymentState.paid,                 None,  True,  OrderStateFilter.none),
    ],
)
def test_find(only_payment_state, only_overdue, only_processed, expected):
    assert (
        OrderStateFilter.find(only_payment_state, only_overdue, only_processed)
        == expected
    )

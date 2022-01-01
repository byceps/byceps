"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.blueprints.admin.shop.order.models import OrderStateFilter
from byceps.services.shop.order.transfer.order import PaymentState


@pytest.mark.parametrize(
    'only_payment_state, only_processed, expected',
    [
        (None,                              None,  OrderStateFilter.none),
        (PaymentState.open,                 None,  OrderStateFilter.payment_state_open),
        (PaymentState.canceled_before_paid, None,  OrderStateFilter.payment_state_canceled_before_paid),
        (PaymentState.paid,                 None,  OrderStateFilter.payment_state_paid),
        (PaymentState.canceled_after_paid,  None,  OrderStateFilter.payment_state_canceled_after_paid),
        (PaymentState.paid,                 False, OrderStateFilter.waiting_for_processing),
        (PaymentState.paid,                 True,  OrderStateFilter.none),
    ],
)
def test_find(only_payment_state, only_processed, expected):
    assert OrderStateFilter.find(only_payment_state, only_processed) == expected

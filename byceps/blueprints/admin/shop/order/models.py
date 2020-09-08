"""
byceps.blueprints.admin.shop.order.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum

from .....services.shop.order.transfer.models import PaymentState
from .....util import iterables


IGNORED = None
NOT_YET_SHIPPED = False
SHIPPED = True


class OrderStateFilter(Enum):

    none                               = (None,                              IGNORED)
    payment_state_open                 = (PaymentState.open,                 IGNORED)
    payment_state_canceled_before_paid = (PaymentState.canceled_before_paid, IGNORED)
    payment_state_paid                 = (PaymentState.paid,                 IGNORED)
    payment_state_canceled_after_paid  = (PaymentState.canceled_after_paid,  IGNORED)
    waiting_for_shipping               = (None,                              NOT_YET_SHIPPED)

    def __init__(self, payment_state, shipped):
        self.payment_state = payment_state
        self.shipped = shipped

    @classmethod
    def find(cls, only_payment_state, only_shipped):
        if only_payment_state == PaymentState.paid and not only_shipped:
            return cls.waiting_for_shipping
        elif only_payment_state is not None:
            return cls.find_for_payment_state(only_payment_state)
        else:
            return cls.none

    @classmethod
    def find_for_payment_state(cls, payment_state):
        def match(order_state_filter):
            return (
                order_state_filter.payment_state == payment_state
                and order_state_filter.shipped is None
            )

        return iterables.find(cls, match)

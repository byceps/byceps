"""
byceps.blueprints.admin.shop.order.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from enum import Enum
from typing import Optional

from .....services.shop.order.transfer.order import PaymentState
from .....util import iterables


IGNORED = None
NOT_YET_PROCESSED = False
OVERDUE = True
PROCESSED = True


class OrderStateFilter(Enum):

    none                               = (None,                              IGNORED, IGNORED)
    payment_state_open_and_overdue     = (PaymentState.open,                 OVERDUE, IGNORED)
    payment_state_open                 = (PaymentState.open,                 IGNORED, IGNORED)
    payment_state_canceled_before_paid = (PaymentState.canceled_before_paid, IGNORED, IGNORED)
    payment_state_paid                 = (PaymentState.paid,                 IGNORED, IGNORED)
    payment_state_canceled_after_paid  = (PaymentState.canceled_after_paid,  IGNORED, IGNORED)
    waiting_for_processing             = (None,                              IGNORED, NOT_YET_PROCESSED)

    def __init__(
        self,
        payment_state: Optional[PaymentState],
        overdue: Optional[bool],
        processed: Optional[bool],
    ) -> None:
        self.payment_state = payment_state
        self.overdue = overdue
        self.processed = processed

    @classmethod
    def find(
        cls,
        only_payment_state: Optional[PaymentState],
        only_overdue: Optional[bool],
        only_processed: Optional[bool],
    ) -> OrderStateFilter:
        if (only_payment_state == PaymentState.open) and (
            only_overdue is not None
        ):
            return (
                cls.payment_state_open_and_overdue
                if only_overdue
                else cls.payment_state_open
            )
        elif (only_payment_state == PaymentState.paid) and (
            only_processed is not None
        ):
            return (
                cls.waiting_for_processing if not only_processed else cls.none
            )
        elif only_payment_state is not None:
            return cls.find_for_payment_state(only_payment_state) or cls.none
        else:
            return cls.none

    @classmethod
    def find_for_payment_state(
        cls, payment_state: PaymentState
    ) -> Optional[OrderStateFilter]:
        def match(order_state_filter):
            return (
                order_state_filter.payment_state == payment_state
                and order_state_filter.overdue is None
                and order_state_filter.processed is None
            )

        return iterables.find(cls, match)

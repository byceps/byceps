"""
byceps.services.shop.order.models.payment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from moneyed import Money

from .order import OrderID


AdditionalPaymentData = dict[str, str]


@dataclass(frozen=True, kw_only=True)
class Payment:
    id: UUID
    order_id: OrderID
    created_at: datetime
    method: str
    amount: Money
    additional_data: AdditionalPaymentData


DEFAULT_PAYMENT_METHODS = {
    'bank_transfer',
    'cash',
    'direct_debit',
    'free',
}

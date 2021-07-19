"""
byceps.services.shop.order.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, NewType, Optional
from uuid import UUID

from .....typing import UserID

from ...article.transfer.models import ArticleNumber
from ...shop.transfer.models import ShopID


OrderID = NewType('OrderID', UUID)


OrderNumber = NewType('OrderNumber', str)


OrderNumberSequenceID = NewType('OrderNumberSequenceID', UUID)


@dataclass(frozen=True)
class OrderNumberSequence:
    id: OrderNumberSequenceID
    shop_id: ShopID
    prefix: str
    value: int


OrderState = Enum(
    'OrderState',
    [
        'open',
        'canceled',
        'complete',
    ],
)


PaymentMethod = Enum(
    'PaymentMethod',
    [
        'bank_transfer',
        'cash',
        'direct_debit',
        'free',
    ],
)


PaymentState = Enum(
    'PaymentState',
    [
        'open',
        'canceled_before_paid',
        'paid',
        'canceled_after_paid',
    ],
)


@dataclass(frozen=True)
class Address:
    country: str
    zip_code: str
    city: str
    street: str


@dataclass(frozen=True)
class OrderItem:
    order_number: OrderNumber
    article_number: ArticleNumber
    description: str
    unit_price: Decimal
    tax_rate: Decimal
    quantity: int
    line_amount: Decimal


OVERDUE_THRESHOLD = timedelta(days=14)


@dataclass(frozen=True)
class Order:
    id: OrderID
    shop_id: ShopID
    order_number: OrderNumber
    created_at: datetime
    placed_by_id: UserID
    first_names: str
    last_name: str
    address: Address
    total_amount: Decimal
    items: list[OrderItem]
    payment_method: Optional[PaymentMethod]
    payment_state: PaymentState
    state: OrderState
    is_open: bool
    is_canceled: bool
    is_paid: bool
    is_invoiced: bool
    is_shipping_required: bool
    is_shipped: bool
    cancelation_reason: Optional[str]

    @property
    def is_overdue(self) -> bool:
        """Return `True` if payment of the order is overdue."""
        if self.payment_state != PaymentState.open:
            return False

        return datetime.utcnow() > (self.created_at + OVERDUE_THRESHOLD)


ActionParameters = Dict[str, Any]


@dataclass(frozen=True)
class Action:
    id: UUID
    article_number: ArticleNumber
    payment_state: PaymentState
    procedure_name: str
    parameters: ActionParameters

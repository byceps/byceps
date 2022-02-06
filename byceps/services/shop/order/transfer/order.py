"""
byceps.services.shop.order.transfer.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import NewType, Optional
from uuid import UUID

from .....typing import UserID

from ...article.transfer.models import ArticleNumber, ArticleType
from ...shop.transfer.models import ShopID
from ...storefront.transfer.models import StorefrontID

from .number import OrderNumber


OrderID = NewType('OrderID', UUID)


OrderState = Enum(
    'OrderState',
    [
        'open',
        'canceled',
        'complete',
    ],
)


PAYMENT_METHODS = set(
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
class Orderer:
    """Someone who orders articles."""

    user_id: UserID
    first_name: str
    last_name: str
    country: str
    zip_code: str
    city: str
    street: str


@dataclass(frozen=True)
class LineItem:
    order_number: OrderNumber
    article_number: ArticleNumber
    article_type: ArticleType
    description: str
    unit_price: Decimal
    tax_rate: Decimal
    quantity: int
    line_amount: Decimal


OVERDUE_THRESHOLD = timedelta(days=14)


@dataclass(frozen=True)
class Order:
    id: OrderID
    created_at: datetime
    shop_id: ShopID
    storefront_id: StorefrontID
    order_number: OrderNumber
    placed_by_id: UserID
    first_name: str
    last_name: str
    address: Address
    total_amount: Decimal
    line_items: list[LineItem]
    payment_method: Optional[str]
    payment_state: PaymentState
    state: OrderState
    is_open: bool
    is_canceled: bool
    is_paid: bool
    is_invoiced: bool
    is_processing_required: bool
    is_processed: bool
    cancelation_reason: Optional[str]

    @property
    def is_overdue(self) -> bool:
        """Return `True` if payment of the order is overdue."""
        if self.payment_state != PaymentState.open:
            return False

        return datetime.utcnow() > (self.created_at + OVERDUE_THRESHOLD)

"""
byceps.services.shop.order.transfer.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NewType, Optional
from uuid import UUID

from .....typing import UserID

from ...article.transfer.models import ArticleNumber, ArticleType
from ...shop.transfer.models import ShopID
from ...storefront.transfer.models import StorefrontID

from .number import OrderNumber


LineItemID = NewType('LineItemID', UUID)


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
    company: Optional[str]
    first_name: str
    last_name: str
    country: str
    zip_code: str
    city: str
    street: str


@dataclass(frozen=True)
class LineItem:
    id: LineItemID
    order_number: OrderNumber
    article_number: ArticleNumber
    article_type: ArticleType
    description: str
    unit_price: Decimal
    tax_rate: Decimal
    quantity: int
    line_amount: Decimal
    processing_result: dict[str, str]


@dataclass(frozen=True)
class Order:
    id: OrderID
    created_at: datetime
    shop_id: ShopID
    storefront_id: StorefrontID
    order_number: OrderNumber
    placed_by_id: UserID
    company: Optional[str]
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
    is_overdue: bool
    is_processing_required: bool
    is_processed: bool
    cancelation_reason: Optional[str]

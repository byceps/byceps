"""
byceps.services.shop.order.models.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NewType
from uuid import UUID

from moneyed import Money

from byceps.services.shop.article.models import (
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.models.user import User
from byceps.typing import UserID

from .number import OrderNumber


LineItemID = NewType('LineItemID', UUID)


LineItemProcessingState = Enum(
    'LineItemProcessingState',
    [
        'not_applicable',
        'pending',
        'canceled',
        'complete',
    ],
)


OrderID = NewType('OrderID', UUID)


OrderState = Enum(
    'OrderState',
    [
        'open',
        'canceled',
        'complete',
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
    company: str | None
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
    article_id: ArticleID
    article_number: ArticleNumber
    article_type: ArticleType
    description: str
    unit_price: Money
    tax_rate: Decimal
    quantity: int
    line_amount: Money
    processing_required: bool
    processing_result: dict[str, str]
    processed_at: datetime | None
    processing_state: LineItemProcessingState


@dataclass(frozen=True)
class BaseOrder:
    id: OrderID
    created_at: datetime
    order_number: OrderNumber
    placed_by_id: UserID
    total_amount: Money
    payment_state: PaymentState
    state: OrderState
    is_open: bool
    is_canceled: bool
    is_paid: bool
    is_overdue: bool


@dataclass(frozen=True)
class Order(BaseOrder):
    shop_id: ShopID
    storefront_id: StorefrontID
    company: str | None
    first_name: str
    last_name: str
    address: Address
    line_items: list[LineItem]
    payment_method: str | None
    is_invoiced: bool
    is_processing_required: bool
    is_processed: bool
    cancelation_reason: str | None


@dataclass(frozen=True)
class AdminOrderListItem(BaseOrder):
    placed_by: User
    first_name: str
    last_name: str
    is_invoiced: bool
    is_processing_required: bool
    is_processed: bool


@dataclass(frozen=True)
class SiteOrderListItem(BaseOrder):
    pass

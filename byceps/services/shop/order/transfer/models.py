"""
byceps.services.shop.order.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, NewType
from uuid import UUID

from attr import attrs

from .....typing import UserID

from ...article.transfer.models import ArticleNumber
from ...shop.transfer.models import ShopID


OrderID = NewType('OrderID', UUID)


OrderNumber = NewType('OrderNumber', str)


PaymentMethod = Enum('PaymentMethod', [
    'bank_transfer',
    'cash',
    'direct_debit',
    'free',
])


PaymentState = Enum('PaymentState', [
    'open',
    'canceled_before_paid',
    'paid',
    'canceled_after_paid',
])


@attrs(auto_attribs=True, frozen=True, slots=True)
class Address:
    country: str
    zip_code: str
    city: str
    street: str


@attrs(auto_attribs=True, frozen=True, slots=True)
class OrderItem:
    order_number: OrderNumber
    article_number: ArticleNumber
    description: str
    unit_price: Decimal
    tax_rate: Decimal
    quantity: int
    line_amount: Decimal


@attrs(auto_attribs=True, frozen=True, slots=True)
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
    items: List[OrderItem]
    payment_method: PaymentMethod
    payment_state: PaymentState
    is_open: bool
    is_canceled: bool
    is_paid: bool
    is_invoiced: bool
    is_shipping_required: bool
    is_shipped: bool
    cancelation_reason: str

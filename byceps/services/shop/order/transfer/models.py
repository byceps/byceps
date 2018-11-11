"""
byceps.services.shop.order.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from .....typing import UserID

from ...article.transfer.models import ArticleNumber
from ...shop.transfer.models import ShopID


OrderID = NewType('OrderID', UUID)


OrderNumber = NewType('OrderNumber', str)


PaymentMethod = Enum('PaymentMethod', [
    'bank_transfer',
    'cash',
    'direct_debit',
])


PaymentState = Enum('PaymentState', [
    'open',
    'canceled_before_paid',
    'paid',
    'canceled_after_paid',
])


@attrs(frozen=True, slots=True)
class Order:
    id = attrib(type=OrderID)
    shop_id = attrib(type=ShopID)
    order_number = attrib(type=OrderNumber)
    created_at = attrib(type=datetime)
    placed_by_id = attrib(type=UserID)
    first_names = attrib(type=str)
    last_name = attrib(type=str)
    country = attrib(type=str)
    zip_code = attrib(type=str)
    city = attrib(type=str)
    street = attrib(type=str)
    payment_method = attrib(type=PaymentMethod)
    payment_state = attrib(type=PaymentState)
    is_open = attrib(type=bool)
    is_canceled = attrib(type=bool)
    is_paid = attrib(type=bool)
    is_invoiced = attrib(type=bool)
    is_shipping_required = attrib(type=bool)
    is_shipped = attrib(type=bool)
    cancelation_reason = attrib(type=str)
    items = attrib()  # List[OrderItem]
    total_price = attrib(type=Decimal)


@attrs(frozen=True, slots=True)
class OrderItem:
    order_number = attrib(type=OrderNumber)
    article_number = attrib(type=ArticleNumber)
    description = attrib(type=str)
    unit_price = attrib(type=Decimal)
    tax_rate = attrib(type=Decimal)
    quantity = attrib(type=int)
    line_amount = attrib(type=Decimal)

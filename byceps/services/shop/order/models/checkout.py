"""
byceps.services.shop.order.models.checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from moneyed import Money

from byceps.services.shop.product.models import (
    ProductID,
    ProductNumber,
    ProductType,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID

from .order import LineItemID, Orderer, OrderID


@dataclass(frozen=True, kw_only=True)
class IncomingLineItem:
    id: LineItemID
    product_id: ProductID
    product_number: ProductNumber
    product_type: ProductType
    name: str
    unit_price: Money
    tax_rate: Decimal
    quantity: int
    line_amount: Money
    processing_required: bool


@dataclass(frozen=True, kw_only=True)
class IncomingOrder:
    id: OrderID
    created_at: datetime
    shop_id: ShopID
    storefront_id: StorefrontID
    orderer: Orderer
    line_items: list[IncomingLineItem]
    total_amount: Money
    processing_required: bool

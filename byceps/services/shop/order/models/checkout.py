"""
byceps.services.shop.order.models.checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from moneyed import Money

from byceps.services.shop.article.models import (
    ArticleID,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID

from .order import Orderer


@dataclass(frozen=True)
class IncomingLineItem:
    article_id: ArticleID
    article_number: ArticleNumber
    article_type: ArticleType
    description: str
    unit_price: Money
    tax_rate: Decimal
    quantity: int
    line_amount: Money
    processing_required: bool


@dataclass(frozen=True)
class IncomingOrder:
    created_at: datetime
    shop_id: ShopID
    storefront_id: StorefrontID
    orderer: Orderer
    line_items: list[IncomingLineItem]
    total_amount: Money
    processing_required: bool

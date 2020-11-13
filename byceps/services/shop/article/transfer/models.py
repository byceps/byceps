"""
byceps.services.shop.article.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import NewType, Optional
from uuid import UUID

from ...shop.transfer.models import ShopID


ArticleID = NewType('ArticleID', UUID)


ArticleNumber = NewType('ArticleNumber', str)


ArticleNumberSequenceID = NewType('ArticleNumberSequenceID', UUID)


@dataclass(frozen=True)
class ArticleNumberSequence:
    id: ArticleNumberSequenceID
    shop_id: ShopID
    prefix: str
    value: int


AttachedArticleID = NewType('AttachedArticleID', UUID)


@dataclass(frozen=True)
class Article:
    id: ArticleID
    shop_id: ShopID
    item_number: ArticleNumber
    description: str
    price: Decimal
    tax_rate: Decimal
    available_from: Optional[datetime]
    available_until: Optional[datetime]
    total_quantity: int
    quantity: int
    max_quantity_per_order: int
    not_directly_orderable: bool
    requires_separate_order: bool
    shipping_required: bool

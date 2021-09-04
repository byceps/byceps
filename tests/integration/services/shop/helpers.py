"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from byceps.services.shop.article import service as article_service
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleNumber,
    ArticleType,
)
from byceps.services.shop.order.models.orderer import Orderer
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope
from byceps.services.user.transfer.models import UserWithDetail

from tests.helpers import generate_token


def create_shop(brand_id, *, shop_id=None, title=None):
    if shop_id is None:
        shop_id = generate_token()

    if title is None:
        title = shop_id

    return shop_service.create_shop(shop_id, brand_id, title)


def create_shop_fragment(shop_id, admin_id, name, body):
    scope = Scope('shop', shop_id)

    version, _ = snippet_service.create_fragment(scope, name, admin_id, body)

    return version.snippet_id


ANY_ARTICLE_ITEM_NUMBER = ArticleNumber('AEC-05-A00009')


def create_article(
    shop_id: ShopID,
    *,
    item_number: ArticleNumber = ANY_ARTICLE_ITEM_NUMBER,
    type_: ArticleType = ArticleType.other,
    description: str = 'Cool thing',
    price: Optional[Decimal] = None,
    tax_rate: Optional[Decimal] = None,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    total_quantity: int = 1,
    max_quantity_per_order: int = 10,
    processing_required: bool = False,
) -> Article:
    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    quantity = total_quantity

    return article_service.create_article(
        shop_id,
        item_number,
        type_,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        processing_required,
    )


def create_orderer(user: UserWithDetail) -> Orderer:
    return Orderer(
        user.id,
        user.detail.first_names,
        user.detail.last_name,
        user.detail.country,
        user.detail.zip_code,
        user.detail.city,
        user.detail.street,
    )

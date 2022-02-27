"""
:Copyright: 2006-2022 Jochen Kupperschmidt
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
    ArticleTypeParams,
)
from byceps.services.shop.order.transfer.order import Orderer
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope, SnippetID
from byceps.services.ticketing.transfer.models import TicketCategoryID
from byceps.services.user import service as user_service
from byceps.typing import UserID

from tests.helpers import generate_token


def create_shop_fragment(
    shop_id: ShopID, creator_id: UserID, name: str, body: str
) -> SnippetID:
    scope = Scope('shop', shop_id)

    version, _ = snippet_service.create_fragment(scope, name, creator_id, body)

    return version.snippet_id


def create_article(
    shop_id: ShopID,
    *,
    item_number: Optional[ArticleNumber] = None,
    type_: ArticleType = ArticleType.other,
    type_params: Optional[ArticleTypeParams] = None,
    description: Optional[str] = None,
    price: Optional[Decimal] = None,
    tax_rate: Optional[Decimal] = None,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    total_quantity: int = 999,
    max_quantity_per_order: int = 10,
    processing_required: bool = False,
) -> Article:
    if item_number is None:
        item_number = ArticleNumber(generate_token())

    if description is None:
        description = generate_token()

    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

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
        type_params=type_params,
    )


def create_ticket_article(
    shop_id: ShopID,
    ticket_category_id: TicketCategoryID,
    *,
    item_number: Optional[ArticleNumber] = None,
    description: Optional[str] = None,
    price: Optional[Decimal] = None,
    tax_rate: Optional[Decimal] = None,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    total_quantity: int = 999,
    max_quantity_per_order: int = 10,
) -> Article:
    if item_number is None:
        item_number = ArticleNumber(generate_token())

    if description is None:
        description = generate_token()

    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return article_service.create_ticket_article(
        shop_id,
        item_number,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        ticket_category_id,
    )


def create_ticket_bundle_article(
    shop_id: ShopID,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
    *,
    item_number: Optional[ArticleNumber] = None,
    description: Optional[str] = None,
    price: Optional[Decimal] = None,
    tax_rate: Optional[Decimal] = None,
    available_from: Optional[datetime] = None,
    available_until: Optional[datetime] = None,
    total_quantity: int = 999,
    max_quantity_per_order: int = 10,
) -> Article:
    if item_number is None:
        item_number = ArticleNumber(generate_token())

    if description is None:
        description = generate_token()

    if price is None:
        price = Decimal('24.95')

    if tax_rate is None:
        tax_rate = Decimal('0.19')

    return article_service.create_ticket_bundle_article(
        shop_id,
        item_number,
        description,
        price,
        tax_rate,
        total_quantity,
        max_quantity_per_order,
        ticket_category_id,
        ticket_quantity,
    )


def create_orderer(user_id: UserID) -> Orderer:
    detail = user_service.get_detail(user_id)

    return Orderer(
        user_id,
        detail.first_name or 'n/a',
        detail.last_name or 'n/a',
        detail.country or 'n/a',
        detail.zip_code or 'n/a',
        detail.city or 'n/a',
        detail.street or 'n/a',
    )

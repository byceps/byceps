"""
tests.helpers.shop
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from moneyed import EUR, Money

from byceps.services.shop.article.models import (
    Article,
    ArticleNumber,
    ArticleType,
    ArticleTypeParams,
)
from byceps.services.shop.article import article_service
from byceps.services.shop.order.models.order import Orderer
from byceps.services.shop.shop.models import ShopID
from byceps.services.snippet.models import SnippetID, SnippetScope
from byceps.services.snippet import snippet_service
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.user import user_service
from byceps.typing import UserID

from . import generate_token


def create_shop_snippet(
    shop_id: ShopID,
    creator_id: UserID,
    name: str,
    language_code: str,
    body: str,
) -> SnippetID:
    scope = SnippetScope('shop', shop_id)

    version, _ = snippet_service.create_snippet(
        scope, name, language_code, creator_id, body
    )

    return version.snippet_id


def create_article(
    shop_id: ShopID,
    *,
    item_number: Optional[ArticleNumber] = None,
    type_: ArticleType = ArticleType.other,
    type_params: Optional[ArticleTypeParams] = None,
    description: Optional[str] = None,
    price: Optional[Money] = None,
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
        price = Money('24.95', EUR)

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
        available_from=available_from,
        available_until=available_until,
    )


def create_ticket_article(
    shop_id: ShopID,
    ticket_category_id: TicketCategoryID,
    *,
    item_number: Optional[ArticleNumber] = None,
    description: Optional[str] = None,
    price: Optional[Money] = None,
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
        price = Money('24.95', EUR)

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
        available_from=available_from,
        available_until=available_until,
    )


def create_ticket_bundle_article(
    shop_id: ShopID,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
    *,
    item_number: Optional[ArticleNumber] = None,
    description: Optional[str] = None,
    price: Optional[Money] = None,
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
        price = Money('24.95', EUR)

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
        available_from=available_from,
        available_until=available_until,
    )


def create_orderer(user_id: UserID) -> Orderer:
    detail = user_service.get_detail(user_id)

    return Orderer(
        user_id=user_id,
        company=None,
        first_name=detail.first_name or 'n/a',
        last_name=detail.last_name or 'n/a',
        country=detail.country or 'n/a',
        zip_code=detail.zip_code or 'n/a',
        city=detail.city or 'n/a',
        street=detail.street or 'n/a',
    )

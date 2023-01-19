"""
byceps.services.shop.shipping.shipping_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterator

from sqlalchemy import select

from ....database import db

from ..article.dbmodels.article import DbArticle
from ..article.models import ArticleID
from ..order.dbmodels.line_item import DbLineItem
from ..order.dbmodels.order import DbOrder
from ..order.models.order import PaymentState
from ..shop.models import ShopID

from .models import ArticleToShip


def get_articles_to_ship(shop_id: ShopID) -> list[ArticleToShip]:
    """Return articles that need, or likely need, to be shipped soon."""
    line_item_quantities = list(_find_line_items(shop_id))

    article_ids = {liq.article_id for liq in line_item_quantities}
    article_descriptions = _get_article_descriptions(article_ids)

    return list(
        _aggregate_ordered_article_quantites(
            line_item_quantities, article_descriptions
        )
    )


@dataclass(frozen=True)
class LineItemQuantity:
    article_id: ArticleID
    payment_state: PaymentState
    quantity: int


def _find_line_items(shop_id: ShopID) -> Iterator[LineItemQuantity]:
    """Return relevant line items with quantities."""
    common_stmt = (
        select(DbLineItem)
        .join(DbOrder)
        .filter(DbOrder.shop_id == shop_id)
        .options(db.joinedload(DbLineItem.order))
        .filter(DbLineItem.processing_required == True)  # noqa: E712
    )

    definitive_line_items = db.session.scalars(
        common_stmt.filter(
            DbOrder._payment_state == PaymentState.paid.name
        ).filter(DbOrder.processed_at.is_(None))
    ).all()

    potential_line_items = db.session.scalars(
        common_stmt.filter(DbOrder._payment_state == PaymentState.open.name)
    ).all()

    db_line_items = definitive_line_items + potential_line_items

    for db_line_item in db_line_items:
        yield LineItemQuantity(
            article_id=db_line_item.article_id,
            payment_state=db_line_item.order.payment_state,
            quantity=db_line_item.quantity,
        )


def _aggregate_ordered_article_quantites(
    line_item_quantities: list[LineItemQuantity],
    article_descriptions: dict[ArticleID, str],
) -> Iterator[ArticleToShip]:
    """Aggregate article quantities per payment state."""
    d: defaultdict[ArticleID, Counter] = defaultdict(Counter)

    for liq in line_item_quantities:
        d[liq.article_id][liq.payment_state] += liq.quantity

    for article_id, counter in d.items():
        description = article_descriptions[article_id]
        quantity_paid = counter[PaymentState.paid]
        quantity_open = counter[PaymentState.open]

        yield ArticleToShip(
            article_id=article_id,
            description=description,
            quantity_paid=quantity_paid,
            quantity_open=quantity_open,
            quantity_total=quantity_paid + quantity_open,
        )


def _get_article_descriptions(
    article_ids: set[ArticleID],
) -> dict[ArticleID, str]:
    """Look up description texts of the specified articles."""
    if not article_ids:
        return {}

    db_articles = db.session.scalars(
        select(DbArticle)
        .options(db.load_only('id', 'description'))
        .filter(DbArticle.id.in_(article_ids))
    ).all()

    return {db_article.id: db_article.description for db_article in db_articles}

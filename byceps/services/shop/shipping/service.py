"""
byceps.services.shop.shipping.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterator, Sequence

from ..article.dbmodels.article import Article as DbArticle

from ....database import db

from ..article.transfer.models import ArticleNumber
from ..order.dbmodels.line_item import LineItem as DbLineItem
from ..order.dbmodels.order import Order as DbOrder
from ..order.transfer.order import PaymentState
from ..shop.transfer.models import ShopID

from .transfer.models import ArticleToShip


def get_articles_to_ship(shop_id: ShopID) -> Sequence[ArticleToShip]:
    """Return articles that need, or likely need, to be shipped soon."""
    relevant_order_payment_states = {
        PaymentState.open,
        PaymentState.paid,
    }

    line_item_quantities = list(
        _find_line_items(shop_id, relevant_order_payment_states)
    )

    article_numbers = {liq.article_number for liq in line_item_quantities}
    article_descriptions = _get_article_descriptions(article_numbers)

    articles_to_ship = list(
        _aggregate_ordered_article_quantites(
            line_item_quantities, article_descriptions
        )
    )

    articles_to_ship.sort(key=lambda a: a.article_number)

    return articles_to_ship


@dataclass(frozen=True)
class LineItemQuantity:
    article_number: ArticleNumber
    payment_state: PaymentState
    quantity: int


def _find_line_items(
    shop_id: ShopID, payment_states: set[PaymentState]
) -> Iterator[LineItemQuantity]:
    """Return article quantities for the given payment states."""
    payment_state_names = {ps.name for ps in payment_states}

    common_query = db.session \
        .query(DbLineItem) \
        .join(DbOrder) \
        .filter(DbOrder.shop_id == shop_id) \
        .options(db.joinedload(DbLineItem.order)) \
        .filter(DbLineItem.processing_required == True)

    definitive_line_items = common_query \
        .filter(DbOrder._payment_state == PaymentState.paid.name) \
        .filter(DbOrder.processed_at == None) \
        .all()

    potential_line_items = common_query \
        .filter(DbOrder._payment_state == PaymentState.open.name) \
        .all()

    db_line_items = definitive_line_items + potential_line_items

    for db_line_item in db_line_items:
        yield LineItemQuantity(
            article_number=db_line_item.article_number,
            payment_state=db_line_item.order.payment_state,
            quantity=db_line_item.quantity,
        )


def _aggregate_ordered_article_quantites(
    line_item_quantities: Sequence[LineItemQuantity],
    article_descriptions: dict[ArticleNumber, str],
) -> Iterator[ArticleToShip]:
    """Aggregate article quantities per payment state."""
    d: defaultdict[ArticleNumber, Counter] = defaultdict(Counter)

    for liq in line_item_quantities:
        d[liq.article_number][liq.payment_state] += liq.quantity

    for article_number, counter in d.items():
        description = article_descriptions[article_number]
        quantity_paid = counter[PaymentState.paid]
        quantity_open = counter[PaymentState.open]

        yield ArticleToShip(
            article_number=article_number,
            description=description,
            quantity_paid=quantity_paid,
            quantity_open=quantity_open,
            quantity_total=quantity_paid + quantity_open,
        )


def _get_article_descriptions(
    article_numbers: set[ArticleNumber],
) -> dict[ArticleNumber, str]:
    """Look up description texts of the specified articles."""
    if not article_numbers:
        return {}

    db_articles = db.session \
        .query(DbArticle) \
        .options(db.load_only('item_number', 'description')) \
        .filter(DbArticle.item_number.in_(article_numbers)) \
        .all()

    return {
        db_article.item_number: db_article.description
        for db_article in db_articles
    }

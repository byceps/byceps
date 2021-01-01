"""
byceps.services.shop.shipping.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, Iterator, Sequence, Set

from ..article.models.article import Article as DbArticle

from ....database import db

from ..article.transfer.models import ArticleNumber
from ..order.models.order import Order as DbOrder
from ..order.models.order_item import OrderItem as DbOrderItem
from ..order.transfer.models import PaymentState
from ..shop.transfer.models import ShopID

from .transfer.models import ArticleToShip


def get_articles_to_ship(shop_id: ShopID) -> Sequence[ArticleToShip]:
    """Return articles that need, or likely need, to be shipped soon."""
    relevant_order_payment_states = {
        PaymentState.open,
        PaymentState.paid,
    }

    order_item_quantities = list(
        _find_order_items(shop_id, relevant_order_payment_states)
    )

    article_numbers = {item.article_number for item in order_item_quantities}
    article_descriptions = _get_article_descriptions(article_numbers)

    articles_to_ship = list(
        _aggregate_ordered_article_quantites(
            order_item_quantities, article_descriptions
        )
    )

    articles_to_ship.sort(key=lambda a: a.article_number)

    return articles_to_ship


@dataclass(frozen=True)
class OrderItemQuantity:
    article_number: ArticleNumber
    payment_state: PaymentState
    quantity: int


def _find_order_items(
    shop_id: ShopID, payment_states: Set[PaymentState]
) -> Iterator[OrderItemQuantity]:
    """Return article quantities for the given payment states."""
    payment_state_names = {ps.name for ps in payment_states}

    common_query = DbOrderItem.query \
        .join(DbOrder) \
        .filter(DbOrder.shop_id == shop_id) \
        .options(db.joinedload('order')) \
        .filter(DbOrderItem.shipping_required == True)

    definitive_order_items = common_query \
        .filter(DbOrder._payment_state == PaymentState.paid.name) \
        .filter(DbOrder.shipped_at == None) \
        .all()

    potential_order_items = common_query \
        .filter(DbOrder._payment_state == PaymentState.open.name) \
        .all()

    order_items = definitive_order_items + potential_order_items

    for item in order_items:
        yield OrderItemQuantity(
            item.article_number,
            item.order.payment_state,
            item.quantity
        )


def _aggregate_ordered_article_quantites(
    order_item_quantities: Sequence[OrderItemQuantity],
    article_descriptions: Dict[ArticleNumber, str],
) -> Iterator[ArticleToShip]:
    """Aggregate article quantities per payment state."""
    d = defaultdict(Counter)

    for item in order_item_quantities:
        d[item.article_number][item.payment_state] += item.quantity

    for article_number, counter in d.items():
        description = article_descriptions[article_number]
        quantity_paid = counter[PaymentState.paid]
        quantity_open = counter[PaymentState.open]

        yield ArticleToShip(
            article_number,
            description,
            quantity_paid,
            quantity_open,
            quantity_total=quantity_paid + quantity_open,
        )


def _get_article_descriptions(
    article_numbers: Set[ArticleNumber],
) -> Dict[ArticleNumber, str]:
    """Look up description texts of the specified articles."""
    if not article_numbers:
        return []

    articles = DbArticle.query \
        .options(db.load_only('item_number', 'description')) \
        .filter(DbArticle.item_number.in_(article_numbers)) \
        .all()

    return {a.item_number: a.description for a in articles}

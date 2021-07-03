"""
byceps.services.shop.order.ordered_articles_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections import Counter
from typing import Sequence

from ....database import db

from ..article.transfer.models import ArticleNumber

from .dbmodels.order_item import OrderItem as DbOrderItem
from .service import order_item_to_transfer_object
from .transfer.models import OrderItem, PaymentState


def count_ordered_articles(
    article_number: ArticleNumber,
) -> dict[PaymentState, int]:
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    order_items = DbOrderItem.query \
        .filter_by(article_number=article_number) \
        .options(
            db.joinedload(DbOrderItem.order),
            db.joinedload(DbOrderItem.article),
        ) \
        .all()

    # Ensure every payment state is present in the resulting dictionary,
    # even if no orders of the corresponding payment state exist for the
    # article.
    counter = Counter({state: 0 for state in PaymentState})

    for order_item in order_items:
        counter[order_item.order.payment_state] += order_item.quantity

    return dict(counter)


def get_order_items_for_article(
    article_number: ArticleNumber,
) -> Sequence[OrderItem]:
    """Return all order items for that article."""
    order_items = DbOrderItem.query \
        .filter_by(article_number=article_number) \
        .all()

    return list(map(order_item_to_transfer_object, order_items))

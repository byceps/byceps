"""
byceps.services.shop.order.ordered_articles_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter
from typing import Dict, Sequence

from ....database import db

from ..article.transfer.models import ArticleNumber

from .models.order_item import OrderItem as DbOrderItem
from .transfer.models import OrderItem, PaymentState


def count_ordered_articles(
    article_number: ArticleNumber
) -> Dict[PaymentState, int]:
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    order_items = DbOrderItem.query \
        .filter_by(article_number=article_number) \
        .options(
            db.joinedload('order'),
            db.joinedload('article'),
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
    article_number: ArticleNumber
) -> Sequence[OrderItem]:
    """Return all order items for that article."""
    order_items = DbOrderItem.query \
        .filter_by(article_number=article_number) \
        .all()

    return [item.to_transfer_object() for item in order_items]

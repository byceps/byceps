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

from .dbmodels.line_item import LineItem as DbLineItem
from .service import line_item_to_transfer_object
from .transfer.models.order import LineItem, PaymentState


def count_ordered_articles(
    article_number: ArticleNumber,
) -> dict[PaymentState, int]:
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    line_items = db.session \
        .query(DbLineItem) \
        .filter_by(article_number=article_number) \
        .options(
            db.joinedload(DbLineItem.order),
            db.joinedload(DbLineItem.article),
        ) \
        .all()

    # Ensure every payment state is present in the resulting dictionary,
    # even if no orders of the corresponding payment state exist for the
    # article.
    counter = Counter({state: 0 for state in PaymentState})

    for line_item in line_items:
        counter[line_item.order.payment_state] += line_item.quantity

    return dict(counter)


def get_line_items_for_article(
    article_number: ArticleNumber,
) -> Sequence[LineItem]:
    """Return all line items for that article."""
    line_items = db.session \
        .query(DbLineItem) \
        .filter_by(article_number=article_number) \
        .all()

    return list(map(line_item_to_transfer_object, line_items))

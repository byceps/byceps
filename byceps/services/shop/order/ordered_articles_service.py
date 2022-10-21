"""
byceps.services.shop.order.ordered_articles_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter
from typing import Sequence

from sqlalchemy import select

from ....database import db

from ..article.transfer.models import ArticleID

from .dbmodels.line_item import DbLineItem
from . import order_service
from .transfer.order import LineItem, PaymentState


def count_ordered_articles(article_id: ArticleID) -> dict[PaymentState, int]:
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    db_line_items = db.session.scalars(
        select(DbLineItem)
        .filter_by(article_id=article_id)
        .options(
            db.joinedload(DbLineItem.order),
            db.joinedload(DbLineItem.article),
        )
    ).all()

    # Ensure every payment state is present in the resulting dictionary,
    # even if no orders of the corresponding payment state exist for the
    # article.
    counter = Counter({state: 0 for state in PaymentState})

    for db_line_item in db_line_items:
        counter[db_line_item.order.payment_state] += db_line_item.quantity

    return dict(counter)


def get_line_items_for_article(article_id: ArticleID) -> Sequence[LineItem]:
    """Return all line items for that article."""
    db_line_items = db.session.scalars(
        select(DbLineItem).filter_by(article_id=article_id)
    ).all()

    return list(map(order_service.line_item_to_transfer_object, db_line_items))

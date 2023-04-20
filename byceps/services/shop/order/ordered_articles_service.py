"""
byceps.services.shop.order.ordered_articles_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter
from typing import Optional

from sqlalchemy import select

from byceps.database import db
from byceps.services.shop.article.models import ArticleID

from . import order_service
from .dbmodels.line_item import DbLineItem
from .dbmodels.order import DbOrder
from .models.order import Order, PaymentState


def count_ordered_articles(article_id: ArticleID) -> dict[PaymentState, int]:
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    db_line_items = (
        db.session.scalars(
            select(DbLineItem)
            .filter_by(article_id=article_id)
            .options(
                db.joinedload(DbLineItem.order),
                db.joinedload(DbLineItem.article),
            )
        )
        .unique()
        .all()
    )

    # Ensure every payment state is present in the resulting dictionary,
    # even if no orders of the corresponding payment state exist for the
    # article.
    counter = Counter({state: 0 for state in PaymentState})

    for db_line_item in db_line_items:
        counter[db_line_item.order.payment_state] += db_line_item.quantity

    return dict(counter)


def get_orders_including_article(
    article_id: ArticleID, *, only_payment_state: Optional[PaymentState] = None
) -> list[Order]:
    """Return all orders that contain the article.

    Optionally limit to orders of a given payment state.
    """
    stmt = (
        select(DbOrder)
        .join(DbLineItem)
        .filter(DbLineItem.article_id == article_id)
        .options(db.joinedload(DbOrder.line_items))
    )

    if only_payment_state is not None:
        stmt = stmt.filter(DbOrder._payment_state == only_payment_state.name)

    db_orders = db.session.scalars(stmt).unique().all()

    return list(map(order_service._order_to_transfer_object, db_orders))

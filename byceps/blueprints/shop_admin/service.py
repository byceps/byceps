# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter

from ...database import db

from ..shop.models.order import OrderItem, PaymentState


def count_ordered_articles(article):
    """Count how often the article has been ordered, grouped by the
    order's payment state.
    """
    order_items = OrderItem.query \
        .options(
            db.joinedload('order'),
            db.joinedload('article'),
        ) \
        .filter_by(article=article) \
        .all()

    # Ensure every payment state is present in the resulting dictionary,
    # even if no orders of the corresponding payment state exist for the
    # article.
    counter = Counter({state: 0 for state in PaymentState})

    for order_item in order_items:
        counter[order_item.order.payment_state] += order_item.quantity

    return dict(counter)


def get_order_items_for_article(article):
    """Return all order items for that article."""
    return OrderItem.query \
        .filter_by(article=article) \
        .options(
            db.joinedload('order.placed_by').joinedload('detail'),
            db.joinedload('order').joinedload('party'),
        ) \
        .all()

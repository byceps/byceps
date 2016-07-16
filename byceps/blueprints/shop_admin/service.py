# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import Counter

from ...database import db

from ..party.models import Party
from ..shop.models.article import Article
from ..shop.models.order import Order, OrderItem, PaymentState


def get_article_counts_by_party_id():
    """Return article counts (including 0) per party, indexed by party ID."""

    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Article.party_id)
        ) \
        .outerjoin(Article) \
        .group_by(Party.id) \
        .all())


def get_parties_with_order_counts():
    """Yield (party, order count) pairs."""
    parties = Party.query.all()

    order_counts_by_party_id = get_order_counts_by_party_id()

    for party in parties:
        order_count = order_counts_by_party_id[party.id]
        yield party, order_count


def get_order_counts_by_party_id():
    """Return order counts (including 0) per party, indexed by party ID."""
    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Order.party_id)
        ) \
        .outerjoin(Order) \
        .group_by(Party.id) \
        .all())


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


def count_articles_for_party(party):
    """Return the number of articles that are assigned to that party."""
    return Article.query \
        .filter_by(party_id=party.id) \
        .count()


def count_open_orders_for_party(party):
    """Return the number of open orders for that party."""
    return Order.query \
        .filter_by(party_id=party.id) \
        .filter_by(_payment_state=PaymentState.open.name) \
        .count()

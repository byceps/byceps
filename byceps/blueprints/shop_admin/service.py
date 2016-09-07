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


def get_article_count_by_party_id():
    """Return article count (including 0) per party, indexed by party ID."""

    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Article.party_id)
        ) \
        .outerjoin(Article) \
        .group_by(Party.id) \
        .all())


def get_order_count_by_party_id():
    """Return order count (including 0) per party, indexed by party ID."""
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


def get_orders_for_party_paginated(party, page, per_page, *,
                                   only_payment_state=None):
    """Return all orders for that party, ordered by creation date.

    If a payment state is specified, only orders in that state are
    returned.
    """
    query = Order.query \
        .for_party(party) \
        .options(
            db.joinedload('placed_by'),
        ) \
        .order_by(Order.created_at.desc())

    if only_payment_state is not None:
        query = query.filter_by(_payment_state=only_payment_state.name)

    return query.paginate(page, per_page)


class OrderAlreadyCanceled(Exception):
    pass


class OrderAlreadyMarkedAsPaid(Exception):
    pass


def cancel_order(order, updated_by, reason):
    """Cancel the order.

    Reserved quantities of articles from that order are made available again.
    """
    if order.payment_state == PaymentState.canceled:
        raise OrderAlreadyCanceled()

    order.cancel(updated_by, reason)

    # Make the reserved quantity of articles available again.
    for item in order.items:
        item.article.quantity += item.quantity

    db.session.commit()


def mark_order_as_paid(order, updated_by):
    """Mark the order as paid."""
    if order.payment_state == PaymentState.paid:
        raise OrderAlreadyMarkedAsPaid()

    order.mark_as_paid(updated_by)
    db.session.commit()


def find_article_with_details(article_id):
    """Return the article with that ID, or `None` if not found."""
    return Article.query \
        .options(
            db.joinedload('party'),
            db.joinedload('articles_attached_to').joinedload('article'),
            db.joinedload('attached_articles').joinedload('article'),
        ) \
        .get(article_id)


def get_attachable_articles(article):
    """Return the articles that can be attached to that article."""
    attached_articles = {attached.article for attached in article.attached_articles}

    unattachable_articles = {article} | attached_articles

    unattachable_article_ids = {article.id for article in unattachable_articles}

    return Article.query \
        .for_party(article.party) \
        .filter(db.not_(Article.id.in_(unattachable_article_ids))) \
        .order_by(Article.item_number) \
        .all()


def get_order_items_for_article(article):
    """Return all order items for that article."""
    return OrderItem.query \
        .filter_by(article=article) \
        .options(
            db.joinedload('order.placed_by').joinedload('detail'),
            db.joinedload('order').joinedload('party'),
        ) \
        .all()

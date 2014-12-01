# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from .models import Article, Order


def get_orderable_articles():
    """Return the articles that can be ordered for the current party,
    less the ones that are only orderable in a dedicated order.
    """
    return Article.query \
        .for_current_party() \
        .filter_by(requires_separate_order=False) \
        .order_by(Article.description) \
        .all()


def get_orders_placed_by_user(user):
    """Return orders placed by the user."""
    return Order.query \
        .placed_by(user) \
        .order_by(Order.created_at.desc()) \
        .all()


def has_user_placed_orders(user):
    """Return `True` if the user has placed orders for the current party."""
    orders_total = Order.query \
        .for_current_party() \
        .filter_by(placed_by=user) \
        .count()
    return orders_total > 0

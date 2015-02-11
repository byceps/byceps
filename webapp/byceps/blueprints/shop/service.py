# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...database import db

from .models import Article, Order, OrderNumberSequence


def get_orderable_articles():
    """Return the articles that can be ordered for the current party,
    less the ones that are only orderable in a dedicated order.
    """
    return Article.query \
        .for_current_party() \
        .filter_by(requires_separate_order=False) \
        .currently_available() \
        .order_by(Article.description) \
        .all()


def generate_order_number(party, *, brand_order_serial_generator=None):
    """Generate and reserve an unused, unique order number for this party."""
    # Allow easy injection of custom generator callable to simplify testing.
    if not brand_order_serial_generator:
        brand_order_serial_generator = _get_next_available_brand_order_serial

    brand_order_serial = brand_order_serial_generator(party.brand)

    return '{}-{:02d}-B{:05d}'.format(
        party.brand.code,
        party.brand_party_serial,
        brand_order_serial)


def _get_next_available_brand_order_serial(brand):
    """Calculate and reserve the next sequential order serial number for the brand."""
    ons = OrderNumberSequence.query.filter_by(brand=brand).with_for_update().one()
    ons.value = OrderNumberSequence.value + 1
    db.session.commit()
    return ons.value


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

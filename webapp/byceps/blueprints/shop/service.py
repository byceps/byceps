# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ...database import db

from .models import Article, Order, PartySequence, PartySequencePurpose


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


def generate_order_number(party):
    """Generate and reserve an unused, unique order number for this party."""
    brand_code = party.brand.code
    party_serial_number = party.brand_party_serial
    order_serial_number = _get_next_serial_number(party,
                                                  PartySequencePurpose.order)

    return '{}-{:02d}-B{:05d}'.format(
        brand_code,
        party_serial_number,
        order_serial_number)


def _get_next_serial_number(party, purpose):
    """Calculate and reserve the next serial number for the party and purpose."""
    sequence = PartySequence.query \
        .filter_by(party=party) \
        .filter_by(_purpose=purpose.name) \
        .with_for_update() \
        .one()

    sequence.value = PartySequence.value + 1
    db.session.commit()
    return sequence.value


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

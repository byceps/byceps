# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.order_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..party.models import Party

from .models.order import Order, PaymentState
from .signals import order_placed
from .service import generate_order_number


def create_order(party, orderer, payment_method, cart):
    """Create an order of one or more articles."""
    order_number = generate_order_number(party)

    order = _build_order(party, order_number, orderer, payment_method)
    _add_items_from_cart_to_order(cart, order)
    db.session.commit()

    order_placed.send(None, order=order)

    return order


def _build_order(party, order_number, orderer, payment_method):
    """Create an order of one or more articles."""
    order = Order(
        party=party,
        order_number=order_number,
        placed_by=orderer.user,
        first_names=orderer.first_names,
        last_name=orderer.last_name,
        date_of_birth=orderer.date_of_birth,
        country=orderer.country,
        zip_code=orderer.zip_code,
        city=orderer.city,
        street=orderer.street,
        payment_method=payment_method,
    )
    db.session.add(order)
    return order


def _add_items_from_cart_to_order(cart, order):
    """Add the items from the cart to the order."""
    for article_item in cart.get_items():
        article = article_item.article
        quantity = article_item.quantity

        article.quantity -= quantity

        order_item = order.add_item(article, quantity)
        db.session.add(order_item)


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


def count_open_orders_for_party(party):
    """Return the number of open orders for that party."""
    return Order.query \
        .filter_by(party_id=party.id) \
        .filter_by(_payment_state=PaymentState.open.name) \
        .count()


def find_order(order_id):
    """Return the order with that id, or `None` if not found."""
    return Order.query.get(order_id)


def find_order_with_details(order_id):
    """Return the order with that id, or `None` if not found."""
    return Order.query \
        .options(
            db.joinedload('party'),
            db.joinedload('items'),
        ) \
        .get(order_id)


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


def get_orders_placed_by_user(user):
    """Return orders placed by the user."""
    return Order.query \
        .placed_by(user) \
        .order_by(Order.created_at.desc()) \
        .all()


def has_user_placed_orders(user, party):
    """Return `True` if the user has placed orders for that party."""
    orders_total = Order.query \
        .for_party(party) \
        .filter_by(placed_by=user) \
        .count()
    return orders_total > 0

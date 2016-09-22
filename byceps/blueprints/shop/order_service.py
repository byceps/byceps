# -*- coding: utf-8 -*-

"""
byceps.blueprints.shop.order_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from .models.order import Order
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

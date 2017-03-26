"""
byceps.services.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from ....blueprints.shop_order.signals import order_placed
from ....database import db

from ...party.models import Party

from ..sequence import service as sequence_service

from .models import Order, OrderEvent, OrderItem, PaymentMethod, PaymentState


def create_order(party_id, orderer, payment_method, cart):
    """Create an order of one or more articles."""
    order_number = sequence_service.generate_order_number(party_id)

    order = _build_order(party_id, order_number, orderer, payment_method)

    order_items = _add_items_from_cart_to_order(cart, order)

    order.shipping_required = any(item.shipping_required for item in order_items)

    db.session.add(order)
    db.session.add_all(order_items)
    db.session.commit()

    order_placed.send(None, order_id=order.id)

    return order


def _build_order(party_id, order_number, orderer, payment_method):
    """Create an order of one or more articles."""
    return Order(
        party_id,
        order_number,
        orderer.user,
        orderer.first_names,
        orderer.last_name,
        orderer.date_of_birth,
        orderer.country,
        orderer.zip_code,
        orderer.city,
        orderer.street,
        payment_method,
    )


def _add_items_from_cart_to_order(cart, order):
    """Add the items from the cart to the order.

    Reduce the article's quantity accordingly.

    Yield the created order items.
    """
    for article_item in cart.get_items():
        article = article_item.article
        quantity = article_item.quantity

        article.quantity -= quantity

        yield _add_article_to_order(order, article, quantity)


def _add_article_to_order(order, article, quantity):
    """Add an article as an item to this order.

    Return the resulting order item (so it can be added to the database
    session).
    """
    return OrderItem(order, article, quantity)


def set_invoiced_flag(order, initiator_id):
    """Record that the invoice for that order has been (externally) created."""
    now = datetime.utcnow()
    event_type = 'order-invoiced'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, **data)
    db.session.add(event)

    order.invoice_created_at = now

    db.session.commit()


def unset_invoiced_flag(order, initiator_id):
    """Withdraw record of the invoice for that order having been created."""
    now = datetime.utcnow()
    event_type = 'order-invoiced-withdrawn'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, **data)
    db.session.add(event)

    order.invoice_created_at = None

    db.session.commit()


def set_shipped_flag(order, initiator_id):
    """Mark the order as shipped."""
    if not order.shipping_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, **data)
    db.session.add(event)

    order.shipped_at = now

    db.session.commit()


def unset_shipped_flag(order, initiator_id):
    """Mark the order as not shipped."""
    if not order.shipping_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped-withdrawn'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, **data)
    db.session.add(event)

    order.shipped_at = None

    db.session.commit()


class OrderAlreadyCanceled(Exception):
    pass


class OrderAlreadyMarkedAsPaid(Exception):
    pass


def cancel_order(order, updated_by_id, reason):
    """Cancel the order.

    Reserved quantities of articles from that order are made available
    again.
    """
    if order.is_canceled:
        raise OrderAlreadyCanceled()

    updated_at = datetime.now()
    payment_state_from = order.payment_state
    payment_state_to = PaymentState.canceled

    _update_payment_state(order, payment_state_to, updated_at, updated_by_id)
    order.payment_method = PaymentMethod.bank_transfer
    order.cancelation_reason = reason

    now = datetime.utcnow()
    event_type = 'order-canceled'
    data = {
        'initiator_id': str(updated_by_id),
        'former_payment_state': payment_state_from.name,
        'reason': reason,
    }

    event = OrderEvent(now, event_type, order.id, **data)
    db.session.add(event)

    # Make the reserved quantity of articles available again.
    for item in order.items:
        item.article.quantity += item.quantity

    db.session.commit()


def mark_order_as_paid(order, payment_method, updated_by_id):
    """Mark the order as paid."""
    if order.is_paid:
        raise OrderAlreadyMarkedAsPaid()

    updated_at = datetime.now()
    payment_state_from = order.payment_state
    payment_state_to = PaymentState.paid

    order.payment_method = payment_method
    _update_payment_state(order, payment_state_to, updated_at, updated_by_id)

    now = datetime.utcnow()
    event_type = 'order-paid'
    data = {
        'initiator_id': str(updated_by_id),
        'former_payment_state': payment_state_from.name,
        'payment_method': payment_method.name,
    }

    event = OrderEvent(now, event_type, order.id, **data)
    db.session.add(event)

    db.session.commit()


def _update_payment_state(order, state, updated_at, updated_by_id):
    order.payment_state = state
    order.payment_state_updated_at = updated_at
    order.payment_state_updated_by_id = updated_by_id


def count_open_orders_for_party(party_id):
    """Return the number of open orders for that party."""
    return Order.query \
        .for_party_id(party_id) \
        .filter_by(_payment_state=PaymentState.open.name) \
        .count()


def find_order(order_id):
    """Return the order with that id, or `None` if not found."""
    return Order.query.get(order_id)


def find_order_with_details(order_id):
    """Return the order with that id, or `None` if not found."""
    return Order.query \
        .options(
            db.joinedload('items'),
        ) \
        .get(order_id)


def find_order_by_order_number(order_number):
    """Return the order with that order number, or `None` if not found."""
    return Order.query \
        .filter_by(order_number=order_number) \
        .one_or_none()


def find_orders_by_order_numbers(order_numbers):
    """Return the orders with those order numbers."""
    return Order.query \
        .filter(Order.order_number.in_(order_numbers)) \
        .all()


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


def get_orders_for_party_paginated(party_id, page, per_page, *,
                                   only_payment_state=None, only_shipped=None):
    """Return all orders for that party, ordered by creation date.

    If a payment state is specified, only orders in that state are
    returned.
    """
    query = Order.query \
        .for_party_id(party_id) \
        .order_by(Order.created_at.desc())

    if only_payment_state is not None:
        query = query.filter_by(_payment_state=only_payment_state.name)

    if only_shipped is not None:
        query = query.filter(Order.shipping_required == True)

        if only_shipped:
            query = query.filter(Order.shipped_at != None)
        else:
            query = query.filter(Order.shipped_at == None)

    return query.paginate(page, per_page)


def get_orders_placed_by_user(user_id):
    """Return orders placed by the user."""
    return Order.query \
        .placed_by_id(user_id) \
        .order_by(Order.created_at.desc()) \
        .all()


def has_user_placed_orders(user_id, party_id):
    """Return `True` if the user has placed orders for that party."""
    orders_total = Order.query \
        .for_party_id(party_id) \
        .placed_by_id(user_id) \
        .count()

    return orders_total > 0


def get_order_events(order_id):
    """Return the events for that order."""
    return OrderEvent.query \
        .filter_by(order_id=order_id) \
        .order_by(OrderEvent.occured_at) \
        .all()

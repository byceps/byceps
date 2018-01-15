"""
byceps.services.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Iterator, Optional, Sequence, Set

from flask import current_app
from flask_sqlalchemy import Pagination
from sqlalchemy.exc import IntegrityError

from ....blueprints.shop_order.signals import order_placed
from ....database import db
from ....typing import PartyID, UserID

from ...party.models.party import Party

from ..article.models.article import Article
from ..cart.models import Cart
from ..sequence import service as sequence_service

from .models.order import Order, OrderID, OrderNumber, OrderTuple
from .models.order_event import OrderEvent
from .models.order_item import OrderItem
from .models.orderer import Orderer
from .models.payment import PaymentMethod, PaymentState
from . import action_service


class OrderFailed(Exception):
    pass


def create_order(party_id: PartyID, orderer: Orderer,
                 payment_method: PaymentMethod, cart: Cart) -> OrderTuple:
    """Create an order of one or more articles."""
    order_number = sequence_service.generate_order_number(party_id)

    order = _build_order(party_id, order_number, orderer, payment_method)

    order_items = _add_items_from_cart_to_order(cart, order)

    order.shipping_required = any(item.shipping_required for item in order_items)

    db.session.add(order)
    db.session.add_all(order_items)

    try:
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error('Order %s failed: %s', order_number, e)
        db.session.rollback()
        raise OrderFailed()

    order_placed.send(None, order_id=order.id)

    return order.to_tuple()


def _build_order(party_id: PartyID, order_number: OrderNumber, orderer: Orderer,
                 payment_method: PaymentMethod) -> Order:
    """Create an order of one or more articles."""
    return Order(
        party_id,
        order_number,
        orderer.user,
        orderer.first_names,
        orderer.last_name,
        orderer.country,
        orderer.zip_code,
        orderer.city,
        orderer.street,
        payment_method,
    )


def _add_items_from_cart_to_order(cart: Cart, order: Order
                                 ) -> Iterator[OrderItem]:
    """Add the items from the cart to the order.

    Reduce the article's quantity accordingly.

    Yield the created order items.
    """
    for article_item in cart.get_items():
        article = article_item.article
        quantity = article_item.quantity

        article.quantity = Article.quantity - quantity

        yield _add_article_to_order(order, article, quantity)


def _add_article_to_order(order: Order, article: Article, quantity: int
                         ) -> OrderItem:
    """Add an article as an item to this order.

    Return the resulting order item (so it can be added to the database
    session).
    """
    return OrderItem(order, article, quantity)


def set_invoiced_flag(order: Order, initiator_id: UserID) -> None:
    """Record that the invoice for that order has been (externally) created."""
    now = datetime.utcnow()
    event_type = 'order-invoiced'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.invoice_created_at = now

    db.session.commit()


def unset_invoiced_flag(order: Order, initiator_id: UserID) -> None:
    """Withdraw record of the invoice for that order having been created."""
    now = datetime.utcnow()
    event_type = 'order-invoiced-withdrawn'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.invoice_created_at = None

    db.session.commit()


def set_shipped_flag(order: Order, initiator_id: UserID) -> None:
    """Mark the order as shipped."""
    if not order.shipping_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.shipped_at = now

    db.session.commit()


def unset_shipped_flag(order: Order, initiator_id: UserID) -> None:
    """Mark the order as not shipped."""
    if not order.shipping_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped-withdrawn'
    data = {
        'initiator_id': str(initiator_id),
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.shipped_at = None

    db.session.commit()


class OrderAlreadyCanceled(Exception):
    pass


class OrderAlreadyMarkedAsPaid(Exception):
    pass


def cancel_order(order: Order, updated_by_id: UserID, reason: str) -> None:
    """Cancel the order.

    Reserved quantities of articles from that order are made available
    again.
    """
    if order.is_canceled:
        raise OrderAlreadyCanceled()

    updated_at = datetime.now()
    payment_state_from = order.payment_state
    payment_state_to = PaymentState.canceled_after_paid if order.is_paid \
                  else PaymentState.canceled_before_paid

    _update_payment_state(order, payment_state_to, updated_at, updated_by_id)
    order.payment_method = PaymentMethod.bank_transfer
    order.cancelation_reason = reason

    now = datetime.utcnow()
    event_type = 'order-canceled-after-paid' if order.is_paid \
            else 'order-canceled-before-paid'
    data = {
        'initiator_id': str(updated_by_id),
        'former_payment_state': payment_state_from.name,
        'reason': reason,
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    # Make the reserved quantity of articles available again.
    for item in order.items:
        item.article.quantity = Article.quantity + item.quantity

    db.session.commit()

    action_service.execute_actions(order, payment_state_to)


def mark_order_as_paid(order_id: OrderID, payment_method: PaymentMethod,
                       updated_by_id: UserID) -> None:
    """Mark the order as paid."""
    order = find_order(order_id)

    if order is None:
        raise ValueError('Unknown order ID')

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

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    db.session.commit()

    action_service.execute_actions(order, payment_state_to)


def _update_payment_state(order: Order, state: PaymentState,
                          updated_at: datetime, updated_by_id: UserID) -> None:
    order.payment_state = state
    order.payment_state_updated_at = updated_at
    order.payment_state_updated_by_id = updated_by_id


def count_open_orders_for_party(party_id: PartyID) -> int:
    """Return the number of open orders for that party."""
    return Order.query \
        .for_party_id(party_id) \
        .filter_by(_payment_state=PaymentState.open.name) \
        .count()


def find_order(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    return Order.query.get(order_id)


def find_order_with_details(order_id: OrderID) -> Optional[OrderTuple]:
    """Return the order with that id, or `None` if not found."""
    order = Order.query \
        .options(
            db.joinedload('items'),
        ) \
        .get(order_id)

    if order is None:
        return None

    return order.to_tuple()


def find_order_by_order_number(order_number: OrderNumber) -> Optional[Order]:
    """Return the order with that order number, or `None` if not found."""
    return Order.query \
        .filter_by(order_number=order_number) \
        .one_or_none()


def find_orders_by_order_numbers(order_numbers: Set[OrderNumber]
                                ) -> Sequence[Order]:
    """Return the orders with those order numbers."""
    if not order_numbers:
        return []

    return Order.query \
        .filter(Order.order_number.in_(order_numbers)) \
        .all()


def get_order_count_by_party_id() -> Dict[PartyID, int]:
    """Return order count (including 0) per party, indexed by party ID."""
    return dict(db.session \
        .query(
            Party.id,
            db.func.count(Order.party_id)
        ) \
        .outerjoin(Order) \
        .group_by(Party.id) \
        .all())


def get_orders_for_party_paginated(party_id: PartyID, page: int, per_page: int, *,
                                   search_term=None,
                                   only_payment_state: Optional[PaymentState]=None,
                                   only_shipped: Optional[bool]=None
                                  ) -> Pagination:
    """Return all orders for that party, ordered by creation date.

    If a payment state is specified, only orders in that state are
    returned.
    """
    query = Order.query \
        .for_party_id(party_id) \
        .order_by(Order.created_at.desc())

    if search_term:
        ilike_pattern = '%{}%'.format(search_term)
        query = query \
            .filter(Order.order_number.ilike(ilike_pattern))

    if only_payment_state is not None:
        query = query.filter_by(_payment_state=only_payment_state.name)

    if only_shipped is not None:
        query = query.filter(Order.shipping_required == True)

        if only_shipped:
            query = query.filter(Order.shipped_at != None)
        else:
            query = query.filter(Order.shipped_at == None)

    return query.paginate(page, per_page)


def get_orders_placed_by_user(user_id: UserID) -> Sequence[Order]:
    """Return orders placed by the user."""
    return Order.query \
        .options(
            db.joinedload('items'),
        ) \
        .placed_by_id(user_id) \
        .order_by(Order.created_at.desc()) \
        .all()


def get_orders_placed_by_user_for_party(user_id: UserID, party_id: PartyID
                                       ) -> Sequence[OrderTuple]:
    """Return orders placed by the user for that party."""
    orders = Order.query \
        .options(
            db.joinedload('items'),
        ) \
        .for_party_id(party_id) \
        .placed_by_id(user_id) \
        .order_by(Order.created_at.desc()) \
        .all()

    return [order.to_tuple() for order in orders]


def has_user_placed_orders(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user has placed orders for that party."""
    orders_total = Order.query \
        .for_party_id(party_id) \
        .placed_by_id(user_id) \
        .count()

    return orders_total > 0

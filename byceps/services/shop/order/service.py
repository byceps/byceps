"""
byceps.services.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Dict, Iterator, Optional, Sequence, Set, Tuple

from flask import current_app
from sqlalchemy.exc import IntegrityError

from ....database import db, Pagination
from ....events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ....typing import UserID

from ..article.models.article import Article
from ..cart.models import Cart
from ..sequence import service as sequence_service
from ..shop.models import Shop
from ..shop import service as shop_service
from ..shop.transfer.models import ShopID

from .models.order import Order as DbOrder
from .models.order_event import OrderEvent
from .models.order_item import OrderItem as DbOrderItem
from .models.orderer import Orderer
from . import action_service
from .transfer.models import (
    Order,
    OrderID,
    OrderNumber,
    PaymentMethod,
    PaymentState,
)


class OrderFailed(Exception):
    pass


def place_order(
    shop_id: ShopID,
    orderer: Orderer,
    payment_method: PaymentMethod,
    cart: Cart,
    *,
    created_at: Optional[datetime] = None,
) -> Tuple[Order, ShopOrderPlaced]:
    """Place an order for one or more articles."""
    shop = shop_service.get_shop(shop_id)

    order_number = sequence_service.generate_order_number(shop.id)

    order = _build_order(
        shop.id, order_number, orderer, payment_method, created_at
    )

    order_items = list(_add_items_from_cart_to_order(cart, order))
    order.total_amount = cart.calculate_total_amount()

    order.shipping_required = any(
        item.shipping_required for item in order_items
    )

    db.session.add(order)
    db.session.add_all(order_items)

    try:
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error('Order %s failed: %s', order_number, e)
        db.session.rollback()
        raise OrderFailed()

    order_dto = order.to_transfer_object()

    event = ShopOrderPlaced(order_id=order.id)

    return order_dto, event


def _build_order(
    shop_id: ShopID,
    order_number: OrderNumber,
    orderer: Orderer,
    payment_method: PaymentMethod,
    created_at: datetime,
) -> DbOrder:
    """Create an order of one or more articles."""
    return DbOrder(
        shop_id,
        order_number,
        orderer.user_id,
        orderer.first_names,
        orderer.last_name,
        orderer.country,
        orderer.zip_code,
        orderer.city,
        orderer.street,
        payment_method,
        created_at=created_at,
    )


def _add_items_from_cart_to_order(
    cart: Cart, order: DbOrder
) -> Iterator[DbOrderItem]:
    """Add the items from the cart to the order.

    Reduce the article's quantity accordingly.

    Yield the created order items.
    """
    for cart_item in cart.get_items():
        article = cart_item.article
        quantity = cart_item.quantity
        line_amount = cart_item.line_amount

        article.quantity = Article.quantity - quantity

        yield DbOrderItem(
            order,
            article.item_number,
            article.description,
            article.price,
            article.tax_rate,
            quantity,
            line_amount,
            article.shipping_required,
        )


def set_invoiced_flag(order: DbOrder, initiator_id: UserID) -> None:
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


def unset_invoiced_flag(order: DbOrder, initiator_id: UserID) -> None:
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


def set_shipped_flag(order: DbOrder, initiator_id: UserID) -> None:
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


def unset_shipped_flag(order: DbOrder, initiator_id: UserID) -> None:
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


def cancel_order(
    order_id: OrderID, initiator_id: UserID, reason: str
) -> ShopOrderCanceled:
    """Cancel the order.

    Reserved quantities of articles from that order are made available
    again.
    """
    order = find_order(order_id)

    if order is None:
        raise ValueError('Unknown order ID')

    if order.is_canceled:
        raise OrderAlreadyCanceled()

    has_order_been_paid = order.is_paid

    now = datetime.utcnow()

    updated_at = now
    payment_state_from = order.payment_state
    payment_state_to = PaymentState.canceled_after_paid if has_order_been_paid \
                  else PaymentState.canceled_before_paid

    _update_payment_state(order, payment_state_to, updated_at, initiator_id)
    order.payment_method = PaymentMethod.bank_transfer
    order.cancelation_reason = reason

    event_type = 'order-canceled-after-paid' if has_order_been_paid \
            else 'order-canceled-before-paid'
    data = {
        'initiator_id': str(initiator_id),
        'former_payment_state': payment_state_from.name,
        'reason': reason,
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    # Make the reserved quantity of articles available again.
    for item in order.items:
        item.article.quantity = Article.quantity + item.quantity

    db.session.commit()

    action_service.execute_actions(
        order.to_transfer_object(), payment_state_to, initiator_id
    )

    return ShopOrderCanceled(order_id=order.id)


def mark_order_as_paid(
    order_id: OrderID, payment_method: PaymentMethod, initiator_id: UserID
) -> ShopOrderPaid:
    """Mark the order as paid."""
    order = find_order(order_id)

    if order is None:
        raise ValueError('Unknown order ID')

    if order.is_paid:
        raise OrderAlreadyMarkedAsPaid()

    now = datetime.utcnow()

    updated_at = now
    payment_state_from = order.payment_state
    payment_state_to = PaymentState.paid

    order.payment_method = payment_method
    _update_payment_state(order, payment_state_to, updated_at, initiator_id)

    event_type = 'order-paid'
    data = {
        'initiator_id': str(initiator_id),
        'former_payment_state': payment_state_from.name,
        'payment_method': payment_method.name,
    }

    event = OrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    db.session.commit()

    action_service.execute_actions(
        order.to_transfer_object(), payment_state_to, initiator_id
    )

    return ShopOrderPaid(order_id=order.id)


def _update_payment_state(
    order: DbOrder,
    state: PaymentState,
    updated_at: datetime,
    initiator_id: UserID,
) -> None:
    order.payment_state = state
    order.payment_state_updated_at = updated_at
    order.payment_state_updated_by_id = initiator_id


def count_open_orders(shop_id: ShopID) -> int:
    """Return the number of open orders for the shop."""
    return DbOrder.query \
        .for_shop(shop_id) \
        .filter_by(_payment_state=PaymentState.open.name) \
        .count()


def count_orders_per_payment_state(shop_id: ShopID) -> Dict[PaymentState, int]:
    """Count orders for the shop, grouped by payment state."""
    counts_by_payment_state = dict.fromkeys(PaymentState, 0)

    rows = db.session \
        .query(
            DbOrder._payment_state,
            db.func.count(DbOrder.id)
        ) \
        .filter(DbOrder.shop_id == shop_id) \
        .group_by(DbOrder._payment_state) \
        .all()

    for payment_state_str, count in rows:
        payment_state = PaymentState[payment_state_str]
        counts_by_payment_state[payment_state] = count

    return counts_by_payment_state


def find_order(order_id: OrderID) -> Optional[DbOrder]:
    """Return the order with that id, or `None` if not found."""
    return DbOrder.query.get(order_id)


def find_order_with_details(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    order = DbOrder.query \
        .options(
            db.joinedload('items'),
        ) \
        .get(order_id)

    if order is None:
        return None

    return order.to_transfer_object()


def find_order_by_order_number(order_number: OrderNumber) -> Optional[DbOrder]:
    """Return the order with that order number, or `None` if not found."""
    return DbOrder.query \
        .filter_by(order_number=order_number) \
        .one_or_none()


def find_orders_by_order_numbers(
    order_numbers: Set[OrderNumber]
) -> Sequence[DbOrder]:
    """Return the orders with those order numbers."""
    if not order_numbers:
        return []

    return DbOrder.query \
        .filter(DbOrder.order_number.in_(order_numbers)) \
        .all()


def get_order_count_by_shop_id() -> Dict[ShopID, int]:
    """Return order count (including 0) per shop, indexed by shop ID."""
    shop_ids_and_order_counts = db.session \
        .query(
            Shop.id,
            db.func.count(DbOrder.shop_id)
        ) \
        .outerjoin(DbOrder) \
        .group_by(Shop.id) \
        .all()

    return dict(shop_ids_and_order_counts)


def get_orders_for_shop_paginated(
    shop_id: ShopID,
    page: int,
    per_page: int,
    *,
    search_term=None,
    only_payment_state: Optional[PaymentState] = None,
    only_shipped: Optional[bool] = None,
) -> Pagination:
    """Return all orders for that shop, ordered by creation date.

    If a payment state is specified, only orders in that state are
    returned.
    """
    query = DbOrder.query \
        .for_shop(shop_id) \
        .order_by(DbOrder.created_at.desc())

    if search_term:
        ilike_pattern = f'%{search_term}%'
        query = query \
            .filter(DbOrder.order_number.ilike(ilike_pattern))

    if only_payment_state is not None:
        query = query.filter_by(_payment_state=only_payment_state.name)

    if only_shipped is not None:
        query = query.filter(DbOrder.shipping_required == True)

        if only_shipped:
            query = query.filter(DbOrder.shipped_at != None)
        else:
            query = query.filter(DbOrder.shipped_at == None)

    return query.paginate(page, per_page)


def get_orders_placed_by_user(user_id: UserID) -> Sequence[DbOrder]:
    """Return orders placed by the user."""
    return DbOrder.query \
        .options(
            db.joinedload('items'),
        ) \
        .placed_by(user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()


def get_orders_placed_by_user_for_shop(
    user_id: UserID, shop_id: ShopID
) -> Sequence[Order]:
    """Return orders placed by the user in that shop."""
    orders = DbOrder.query \
        .options(
            db.joinedload('items'),
        ) \
        .for_shop(shop_id) \
        .placed_by(user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()

    return [order.to_transfer_object() for order in orders]


def has_user_placed_orders(user_id: UserID, shop_id: ShopID) -> bool:
    """Return `True` if the user has placed orders in that shop."""
    orders_total = DbOrder.query \
        .for_shop(shop_id) \
        .placed_by(user_id) \
        .count()

    return orders_total > 0

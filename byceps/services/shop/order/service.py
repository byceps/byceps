"""
byceps.services.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Dict, Iterator, Mapping, Optional, Sequence, Set, Tuple

from flask import current_app
from sqlalchemy.exc import IntegrityError

from ....database import db, paginate, Pagination
from ....events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ....typing import UserID

from ...user import service as user_service

from ..article import service as article_service
from ..cart.models import Cart
from ..shop.models import Shop as DbShop
from ..shop import service as shop_service
from ..shop.transfer.models import ShopID
from ..storefront import service as storefront_service
from ..storefront.transfer.models import StorefrontID

from .models.order import Order as DbOrder
from .models.order_event import OrderEvent as DbOrderEvent
from .models.order_item import OrderItem as DbOrderItem
from .models.orderer import Orderer
from . import action_service, sequence_service
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
    storefront_id: StorefrontID,
    orderer: Orderer,
    cart: Cart,
    *,
    created_at: Optional[datetime] = None,
) -> Tuple[Order, ShopOrderPlaced]:
    """Place an order for one or more articles."""
    storefront = storefront_service.get_storefront(storefront_id)
    shop = shop_service.get_shop(storefront.shop_id)

    orderer_user = user_service.get_user(orderer.user_id)

    order_number_sequence = sequence_service.find_order_number_sequence(
        storefront.order_number_sequence_id
    )
    order_number = sequence_service.generate_order_number(
        order_number_sequence.id
    )

    order = _build_order(shop.id, order_number, orderer, created_at)
    order_items = list(_build_order_items(cart, order))
    order.total_amount = cart.calculate_total_amount()
    order.shipping_required = any(
        item.shipping_required for item in order_items
    )

    db.session.add(order)
    db.session.add_all(order_items)

    _reduce_article_stock(cart)

    try:
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error('Order %s failed: %s', order_number, e)
        db.session.rollback()
        raise OrderFailed()

    order_dto = order.to_transfer_object()

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        initiator_id=orderer_user.id,
        initiator_screen_name=orderer_user.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )

    return order_dto, event


def _build_order(
    shop_id: ShopID,
    order_number: OrderNumber,
    orderer: Orderer,
    created_at: Optional[datetime],
) -> DbOrder:
    """Build an order."""
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
        created_at=created_at,
    )


def _build_order_items(cart: Cart, order: DbOrder) -> Iterator[DbOrderItem]:
    """Build order items from the cart's content."""
    for cart_item in cart.get_items():
        article = cart_item.article
        quantity = cart_item.quantity
        line_amount = cart_item.line_amount

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


def _reduce_article_stock(cart: Cart) -> None:
    """Reduce article stock according to what is in the cart."""
    for cart_item in cart.get_items():
        article = cart_item.article
        quantity = cart_item.quantity

        article_service.decrease_quantity(article.id, quantity, commit=False)


def set_invoiced_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Record that the invoice for that order has been (externally) created."""
    order = _find_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    now = datetime.utcnow()
    event_type = 'order-invoiced'
    data = {
        'initiator_id': str(initiator.id),
    }

    event = DbOrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.invoice_created_at = now

    db.session.commit()


def unset_invoiced_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Withdraw record of the invoice for that order having been created."""
    order = _find_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    now = datetime.utcnow()
    event_type = 'order-invoiced-withdrawn'
    data = {
        'initiator_id': str(initiator.id),
    }

    event = DbOrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.invoice_created_at = None

    db.session.commit()


def set_shipped_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Mark the order as shipped."""
    order = _find_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    if not order.shipping_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped'
    data = {
        'initiator_id': str(initiator.id),
    }

    event = DbOrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    order.shipped_at = now

    db.session.commit()


def unset_shipped_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Mark the order as not shipped."""
    order = _find_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    if not order.shipping_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped-withdrawn'
    data = {
        'initiator_id': str(initiator.id),
    }

    event = DbOrderEvent(now, event_type, order.id, data)
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
    order = _find_order_entity(order_id)

    if order is None:
        raise ValueError('Unknown order ID')

    if order.is_canceled:
        raise OrderAlreadyCanceled()

    initiator = user_service.get_user(initiator_id)
    orderer_user = user_service.get_user(order.placed_by_id)

    has_order_been_paid = order.is_paid

    now = datetime.utcnow()

    updated_at = now
    payment_state_from = order.payment_state
    payment_state_to = (
        PaymentState.canceled_after_paid
        if has_order_been_paid
        else PaymentState.canceled_before_paid
    )

    _update_payment_state(order, payment_state_to, updated_at, initiator.id)
    order.cancelation_reason = reason

    event_type = (
        'order-canceled-after-paid'
        if has_order_been_paid
        else 'order-canceled-before-paid'
    )
    data = {
        'initiator_id': str(initiator.id),
        'former_payment_state': payment_state_from.name,
        'reason': reason,
    }

    event = DbOrderEvent(now, event_type, order.id, data)
    db.session.add(event)

    # Make the reserved quantity of articles available again.
    for item in order.items:
        article_service.increase_quantity(
            item.article.id, item.quantity, commit=False
        )

    db.session.commit()

    action_service.execute_actions(
        order.to_transfer_object(), payment_state_to, initiator.id
    )

    return ShopOrderCanceled(
        occurred_at=updated_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )


def mark_order_as_paid(
    order_id: OrderID,
    payment_method: PaymentMethod,
    initiator_id: UserID,
    *,
    additional_event_data: Optional[Mapping[str, str]] = None,
) -> ShopOrderPaid:
    """Mark the order as paid."""
    order = _find_order_entity(order_id)

    if order is None:
        raise ValueError('Unknown order ID')

    if order.is_paid:
        raise OrderAlreadyMarkedAsPaid()

    initiator = user_service.get_user(initiator_id)
    orderer_user = user_service.get_user(order.placed_by_id)

    now = datetime.utcnow()

    updated_at = now
    payment_state_from = order.payment_state
    payment_state_to = PaymentState.paid

    order.payment_method = payment_method
    _update_payment_state(order, payment_state_to, updated_at, initiator.id)

    event_type = 'order-paid'
    # Add required, internally set properties after given additional
    # ones to ensure the former are not overridden by the latter.
    event_data = {}
    if additional_event_data is not None:
        event_data.update(additional_event_data)
    event_data.update(
        {
            'initiator_id': str(initiator.id),
            'former_payment_state': payment_state_from.name,
            'payment_method': payment_method.name,
        }
    )

    event = DbOrderEvent(now, event_type, order.id, event_data)
    db.session.add(event)

    db.session.commit()

    action_service.execute_actions(
        order.to_transfer_object(), payment_state_to, initiator.id
    )

    return ShopOrderPaid(
        occurred_at=updated_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
        payment_method=payment_method,
    )


def _update_payment_state(
    order: DbOrder,
    state: PaymentState,
    updated_at: datetime,
    initiator_id: UserID,
) -> None:
    order.payment_state = state
    order.payment_state_updated_at = updated_at
    order.payment_state_updated_by_id = initiator_id


def delete_order(order_id: OrderID) -> None:
    """Delete an order."""
    order = find_order(order_id)

    db.session.query(DbOrderEvent) \
        .filter_by(order_id=order_id) \
        .delete()

    db.session.query(DbOrderItem) \
        .filter_by(order_number=order.order_number) \
        .delete()

    db.session.query(DbOrder) \
        .filter_by(id=order_id) \
        .delete()

    db.session.commit()


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


def _find_order_entity(order_id: OrderID) -> Optional[DbOrder]:
    """Return the order database entity with that id, or `None` if not
    found.
    """
    return DbOrder.query.get(order_id)


def find_order(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    order = _find_order_entity(order_id)

    if order is None:
        return None

    return order.to_transfer_object()


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


def find_order_by_order_number(order_number: OrderNumber) -> Optional[Order]:
    """Return the order with that order number, or `None` if not found."""
    order = DbOrder.query \
        .filter_by(order_number=order_number) \
        .one_or_none()

    if order is None:
        return None

    return order.to_transfer_object()


def find_orders_by_order_numbers(
    order_numbers: Set[OrderNumber],
) -> Sequence[Order]:
    """Return the orders with those order numbers."""
    if not order_numbers:
        return []

    orders = DbOrder.query \
        .filter(DbOrder.order_number.in_(order_numbers)) \
        .all()

    return [order.to_transfer_object() for order in orders]


def get_order_count_by_shop_id() -> Dict[ShopID, int]:
    """Return order count (including 0) per shop, indexed by shop ID."""
    shop_ids_and_order_counts = db.session \
        .query(
            DbShop.id,
            db.func.count(DbOrder.shop_id)
        ) \
        .outerjoin(DbOrder) \
        .group_by(DbShop.id) \
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

    return paginate(
        query,
        page,
        per_page,
        item_mapper=lambda order: order.to_transfer_object(),
    )


def get_orders_placed_by_user(user_id: UserID) -> Sequence[Order]:
    """Return orders placed by the user."""
    orders = DbOrder.query \
        .options(
            db.joinedload('items'),
        ) \
        .placed_by(user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()

    return [order.to_transfer_object() for order in orders]


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


PAYMENT_METHOD_LABELS = {
    PaymentMethod.bank_transfer: 'Überweisung',
    PaymentMethod.cash: 'Barzahlung',
    PaymentMethod.direct_debit: 'Lastschrift',
    PaymentMethod.free: 'kostenlos',
}


def find_payment_method_label(payment_method: PaymentMethod) -> Optional[str]:
    """Return a label for the payment method."""
    return PAYMENT_METHOD_LABELS.get(payment_method)


def get_payment_date(order_id: OrderID) -> Optional[datetime]:
    """Return the date the order has been marked as paid, or `None` if
    it has not been paid.
    """
    return db.session \
        .query(DbOrder.payment_state_updated_at) \
        .filter_by(id=order_id) \
        .scalar()

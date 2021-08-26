"""
byceps.services.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Iterator, Mapping, Optional, Sequence

from flask import current_app
from flask_babel import lazy_gettext
from sqlalchemy.exc import IntegrityError

from ....database import db, paginate, Pagination
from ....events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ....typing import UserID

from ...user import service as user_service

from ..article import service as article_service
from ..cart.models import Cart
from ..shop.dbmodels import Shop as DbShop
from ..shop import service as shop_service
from ..shop.transfer.models import ShopID
from ..storefront import service as storefront_service
from ..storefront.transfer.models import StorefrontID

from .dbmodels.line_item import LineItem as DbLineItem
from .dbmodels.order import Order as DbOrder
from .dbmodels.order_event import OrderEvent as DbOrderEvent, OrderEventData
from .models.orderer import Orderer
from . import action_service, event_service, sequence_service
from .transfer.models import (
    Address,
    Order,
    OrderID,
    LineItem,
    OrderNumber,
    OrderState,
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
) -> tuple[Order, ShopOrderPlaced]:
    """Place an order for one or more articles."""
    storefront = storefront_service.get_storefront(storefront_id)
    shop = shop_service.get_shop(storefront.shop_id)

    orderer_user = user_service.get_user(orderer.user_id)

    order_number_sequence = sequence_service.get_order_number_sequence(
        storefront.order_number_sequence_id
    )
    order_number = sequence_service.generate_order_number(
        order_number_sequence.id
    )

    order = _build_order(shop.id, order_number, orderer, created_at)
    line_items = list(_build_line_items(cart, order))
    order.total_amount = cart.calculate_total_amount()
    order.shipping_required = any(
        item.shipping_required for item in line_items
    )

    db.session.add(order)
    db.session.add_all(line_items)

    _reduce_article_stock(cart)

    try:
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error('Order %s failed: %s', order_number, e)
        db.session.rollback()
        raise OrderFailed()

    order_dto = _order_to_transfer_object(order)

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


def _build_line_items(cart: Cart, order: DbOrder) -> Iterator[DbLineItem]:
    """Build line items from the cart's content."""
    for cart_item in cart.get_items():
        article = cart_item.article
        quantity = cart_item.quantity
        line_amount = cart_item.line_amount

        yield DbLineItem(
            order,
            article.item_number,
            article.type_,
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


def add_note(order_id: OrderID, author_id: UserID, text: str) -> None:
    """Add a note to the order."""
    order = get_order(order_id)
    author = user_service.get_user(author_id)

    event_type = 'order-note-added'
    data = {
        'author_id': str(author.id),
        'text': text,
    }

    event_service.create_event(event_type, order.id, data)


def set_invoiced_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Record that the invoice for that order has been (externally) created."""
    order = _get_order_entity(order_id)
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
    order = _get_order_entity(order_id)
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
    order = _get_order_entity(order_id)
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
    order = _get_order_entity(order_id)
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
    order = _get_order_entity(order_id)

    if _is_canceled(order):
        raise OrderAlreadyCanceled()

    initiator = user_service.get_user(initiator_id)
    orderer_user = user_service.get_user(order.placed_by_id)

    has_order_been_paid = _is_paid(order)

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
        _order_to_transfer_object(order), payment_state_to, initiator.id
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
    payment_method: str,
    initiator_id: UserID,
    *,
    additional_event_data: Optional[Mapping[str, str]] = None,
) -> ShopOrderPaid:
    """Mark the order as paid."""
    order = _get_order_entity(order_id)

    if _is_paid(order):
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
    event_data: OrderEventData = {}
    if additional_event_data is not None:
        event_data.update(additional_event_data)
    event_data.update(
        {
            'initiator_id': str(initiator.id),
            'former_payment_state': payment_state_from.name,
            'payment_method': payment_method,
        }
    )

    event = DbOrderEvent(now, event_type, order.id, event_data)
    db.session.add(event)

    db.session.commit()

    action_service.execute_actions(
        _order_to_transfer_object(order), payment_state_to, initiator.id
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
    order = get_order(order_id)

    db.session.query(DbOrderEvent) \
        .filter_by(order_id=order.id) \
        .delete()

    db.session.query(DbLineItem) \
        .filter_by(order_number=order.order_number) \
        .delete()

    db.session.query(DbOrder) \
        .filter_by(id=order.id) \
        .delete()

    db.session.commit()


def count_open_orders(shop_id: ShopID) -> int:
    """Return the number of open orders for the shop."""
    return db.session \
        .query(DbOrder) \
        .filter_by(shop_id=shop_id) \
        .filter_by(_payment_state=PaymentState.open.name) \
        .count()


def count_orders_per_payment_state(shop_id: ShopID) -> dict[PaymentState, int]:
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
    return db.session.query(DbOrder).get(order_id)


def _get_order_entity(order_id: OrderID) -> DbOrder:
    """Return the order database entity with that id, or raise an
    exception.
    """
    order = _find_order_entity(order_id)

    if order is None:
        raise ValueError(f'Unknown order ID "{order_id}"')

    return order


def find_order(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    order = _find_order_entity(order_id)

    if order is None:
        return None

    return _order_to_transfer_object(order)


def get_order(order_id: OrderID) -> Order:
    """Return the order with that id, or raise an exception."""
    order = _get_order_entity(order_id)
    return _order_to_transfer_object(order)


def find_order_with_details(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    order = db.session.query(DbOrder) \
        .options(
            db.joinedload(DbOrder.items),
        ) \
        .get(order_id)

    if order is None:
        return None

    return _order_to_transfer_object(order)


def find_order_by_order_number(order_number: OrderNumber) -> Optional[Order]:
    """Return the order with that order number, or `None` if not found."""
    order = db.session \
        .query(DbOrder) \
        .filter_by(order_number=order_number) \
        .one_or_none()

    if order is None:
        return None

    return _order_to_transfer_object(order)


def find_orders_by_order_numbers(
    order_numbers: set[OrderNumber],
) -> Sequence[Order]:
    """Return the orders with those order numbers."""
    if not order_numbers:
        return []

    orders = db.session \
        .query(DbOrder) \
        .filter(DbOrder.order_number.in_(order_numbers)) \
        .all()

    return list(map(_order_to_transfer_object, orders))


def get_order_count_by_shop_id() -> dict[ShopID, int]:
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
    query = db.session \
        .query(DbOrder) \
        .filter_by(shop_id=shop_id) \
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
        item_mapper=lambda order: _order_to_transfer_object(order),
    )


def get_orders_placed_by_user(user_id: UserID) -> Sequence[Order]:
    """Return orders placed by the user."""
    orders = db.session \
        .query(DbOrder) \
        .options(
            db.joinedload(DbOrder.items),
        ) \
        .filter_by(placed_by_id=user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()

    return list(map(_order_to_transfer_object, orders))


def get_orders_placed_by_user_for_shop(
    user_id: UserID, shop_id: ShopID
) -> Sequence[Order]:
    """Return orders placed by the user in that shop."""
    orders = db.session \
        .query(DbOrder) \
        .options(
            db.joinedload(DbOrder.items),
        ) \
        .filter_by(shop_id=shop_id) \
        .filter_by(placed_by_id=user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()

    return list(map(_order_to_transfer_object, orders))


def has_user_placed_orders(user_id: UserID, shop_id: ShopID) -> bool:
    """Return `True` if the user has placed orders in that shop."""
    orders_total = db.session \
        .query(DbOrder) \
        .filter_by(shop_id=shop_id) \
        .filter_by(placed_by_id=user_id) \
        .count()

    return orders_total > 0


_PAYMENT_METHOD_LABELS = {
    'bank_transfer': lazy_gettext('bank transfer'),
    'cash': lazy_gettext('cash'),
    'direct_debit': lazy_gettext('direct debit'),
    'free': lazy_gettext('free'),
}


def find_payment_method_label(payment_method: str) -> Optional[str]:
    """Return a label for the payment method."""
    return _PAYMENT_METHOD_LABELS.get(payment_method)


def get_payment_date(order_id: OrderID) -> Optional[datetime]:
    """Return the date the order has been marked as paid, or `None` if
    it has not been paid.
    """
    return db.session \
        .query(DbOrder.payment_state_updated_at) \
        .filter_by(id=order_id) \
        .scalar()


def _order_to_transfer_object(order: DbOrder) -> Order:
    """Create transfer object from order database entity."""
    address = Address(
        country=order.country,
        zip_code=order.zip_code,
        city=order.city,
        street=order.street,
    )

    items = list(map(line_item_to_transfer_object, order.items))

    state = _get_order_state(order)
    is_open = order.payment_state == PaymentState.open
    is_canceled = _is_canceled(order)
    is_paid = _is_paid(order)
    is_invoiced = order.invoice_created_at is not None
    is_shipping_required = order.shipping_required
    is_shipped = order.shipped_at is not None

    return Order(
        id=order.id,
        shop_id=order.shop_id,
        order_number=order.order_number,
        created_at=order.created_at,
        placed_by_id=order.placed_by_id,
        first_names=order.first_names,
        last_name=order.last_name,
        address=address,
        total_amount=order.total_amount,
        items=items,
        payment_method=order.payment_method,
        payment_state=order.payment_state,
        state=state,
        is_open=is_open,
        is_canceled=is_canceled,
        is_paid=is_paid,
        is_invoiced=is_invoiced,
        is_shipping_required=is_shipping_required,
        is_shipped=is_shipped,
        cancelation_reason=order.cancelation_reason,
    )


def line_item_to_transfer_object(
    item: DbLineItem,
) -> LineItem:
    """Create transfer object from line item database entity."""
    return LineItem(
        order_number=item.order_number,
        article_number=item.article_number,
        article_type=item.article_type,
        description=item.description,
        unit_price=item.unit_price,
        tax_rate=item.tax_rate,
        quantity=item.quantity,
        line_amount=item.line_amount,
    )


def _get_order_state(order: DbOrder) -> OrderState:
    is_canceled = _is_canceled(order)
    is_paid = _is_paid(order)
    is_shipping_required = order.shipping_required
    is_shipped = order.shipped_at is not None

    if is_canceled:
        return OrderState.canceled

    if is_paid:
        if not is_shipping_required or is_shipped:
            return OrderState.complete

    return OrderState.open


def _is_canceled(order: DbOrder) -> bool:
    return order.payment_state in {
        PaymentState.canceled_before_paid,
        PaymentState.canceled_after_paid,
    }


def _is_paid(order: DbOrder) -> bool:
    return order.payment_state == PaymentState.paid

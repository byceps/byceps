"""
byceps.services.shop.order.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Iterator, Mapping, Optional, Sequence
from uuid import UUID

from flask import current_app
from flask_babel import lazy_gettext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ....database import db, paginate, Pagination
from ....events.shop import ShopOrderCanceled, ShopOrderPaid, ShopOrderPlaced
from ....typing import UserID

from ...ticketing.transfer.models import TicketCategoryID
from ...user import service as user_service

from ..article import service as article_service
from ..article.transfer.models import ArticleType
from ..cart.models import Cart, CartItem
from ..shop.dbmodels import Shop as DbShop
from ..shop import service as shop_service
from ..shop.transfer.models import ShopID
from ..storefront import service as storefront_service
from ..storefront.transfer.models import StorefrontID

from .actions import ticket as ticket_actions
from .actions import ticket_bundle as ticket_bundle_actions
from .dbmodels.line_item import LineItem as DbLineItem
from .dbmodels.log import OrderLogEntry as DbOrderLogEntry
from .dbmodels.order import Order as DbOrder
from . import action_service, log_service, sequence_service
from .transfer.log import OrderLogEntryData
from .transfer.number import OrderNumber
from .transfer.order import (
    Address,
    LineItemID,
    Order,
    OrderID,
    LineItem,
    Orderer,
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

    cart_items = cart.get_items()

    if created_at is None:
        created_at = datetime.utcnow()

    db_order = _build_order(
        created_at, shop.id, storefront.id, order_number, orderer
    )
    db_line_items = list(_build_line_items(cart_items, db_order))
    db_order.total_amount = cart.calculate_total_amount()
    db_order.processing_required = any(
        db_line_item.processing_required for db_line_item in db_line_items
    )

    db.session.add(db_order)
    db.session.add_all(db_line_items)

    _reduce_article_stock(cart_items)

    try:
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error('Order %s failed: %s', order_number, e)
        db.session.rollback()
        raise OrderFailed()

    order = _order_to_transfer_object(db_order)

    # Create log entry in separate step as order ID is not available earlier.
    log_entry_data = {'initiator_id': str(orderer_user.id)}
    log_service.create_entry('order-placed', order.id, log_entry_data)

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        initiator_id=orderer_user.id,
        initiator_screen_name=orderer_user.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )

    return order, event


def _build_order(
    created_at: datetime,
    shop_id: ShopID,
    storefront_id: StorefrontID,
    order_number: OrderNumber,
    orderer: Orderer,
) -> DbOrder:
    """Build an order."""
    return DbOrder(
        created_at,
        shop_id,
        storefront_id,
        order_number,
        orderer.user_id,
        orderer.first_name,
        orderer.last_name,
        orderer.country,
        orderer.zip_code,
        orderer.city,
        orderer.street,
    )


def _build_line_items(
    cart_items: list[CartItem], db_order: DbOrder
) -> Iterator[DbLineItem]:
    """Build line items from the cart's content."""
    for cart_item in cart_items:
        article = cart_item.article
        quantity = cart_item.quantity
        line_amount = cart_item.line_amount

        yield DbLineItem(
            db_order,
            article.item_number,
            article.type_,
            article.description,
            article.price,
            article.tax_rate,
            quantity,
            line_amount,
            article.processing_required,
        )


def _reduce_article_stock(cart_items: list[CartItem]) -> None:
    """Reduce article stock according to what is in the cart."""
    for cart_item in cart_items:
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

    log_service.create_entry(event_type, order.id, data)


def set_invoiced_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Record that the invoice for that order has been (externally) created."""
    db_order = _get_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    now = datetime.utcnow()
    event_type = 'order-invoiced'
    data = {
        'initiator_id': str(initiator.id),
    }

    log_entry = DbOrderLogEntry(now, event_type, db_order.id, data)
    db.session.add(log_entry)

    db_order.invoice_created_at = now

    db.session.commit()


def unset_invoiced_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Withdraw record of the invoice for that order having been created."""
    db_order = _get_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    now = datetime.utcnow()
    event_type = 'order-invoiced-withdrawn'
    data = {
        'initiator_id': str(initiator.id),
    }

    log_entry = DbOrderLogEntry(now, event_type, db_order.id, data)
    db.session.add(log_entry)

    db_order.invoice_created_at = None

    db.session.commit()


def set_shipped_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Mark the order as shipped."""
    db_order = _get_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    if not db_order.processing_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped'
    data = {
        'initiator_id': str(initiator.id),
    }

    log_entry = DbOrderLogEntry(now, event_type, db_order.id, data)
    db.session.add(log_entry)

    db_order.processed_at = now

    db.session.commit()


def unset_shipped_flag(order_id: OrderID, initiator_id: UserID) -> None:
    """Mark the order as not shipped."""
    db_order = _get_order_entity(order_id)
    initiator = user_service.get_user(initiator_id)

    if not db_order.processing_required:
        raise ValueError('Order contains no items that require shipping.')

    now = datetime.utcnow()
    event_type = 'order-shipped-withdrawn'
    data = {
        'initiator_id': str(initiator.id),
    }

    log_entry = DbOrderLogEntry(now, event_type, db_order.id, data)
    db.session.add(log_entry)

    db_order.processed_at = None

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
    db_order = _get_order_entity(order_id)

    if _is_canceled(db_order):
        raise OrderAlreadyCanceled()

    initiator = user_service.get_user(initiator_id)
    orderer_user = user_service.get_user(db_order.placed_by_id)

    has_order_been_paid = _is_paid(db_order)

    now = datetime.utcnow()

    updated_at = now
    payment_state_from = db_order.payment_state
    payment_state_to = (
        PaymentState.canceled_after_paid
        if has_order_been_paid
        else PaymentState.canceled_before_paid
    )

    _update_payment_state(db_order, payment_state_to, updated_at, initiator.id)
    db_order.cancelation_reason = reason

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

    log_entry = DbOrderLogEntry(now, event_type, db_order.id, data)
    db.session.add(log_entry)

    # Make the reserved quantity of articles available again.
    for db_line_item in db_order.line_items:
        article_service.increase_quantity(
            db_line_item.article.id, db_line_item.quantity, commit=False
        )

    db.session.commit()

    order = _order_to_transfer_object(db_order)

    if payment_state_to == PaymentState.canceled_after_paid:
        _execute_article_revocation_actions(order, initiator.id)

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
    additional_log_entry_data: Optional[Mapping[str, str]] = None,
) -> ShopOrderPaid:
    """Mark the order as paid."""
    db_order = _get_order_entity(order_id)

    if _is_paid(db_order):
        raise OrderAlreadyMarkedAsPaid()

    initiator = user_service.get_user(initiator_id)
    orderer_user = user_service.get_user(db_order.placed_by_id)

    now = datetime.utcnow()

    updated_at = now
    payment_state_from = db_order.payment_state
    payment_state_to = PaymentState.paid

    db_order.payment_method = payment_method
    _update_payment_state(db_order, payment_state_to, updated_at, initiator.id)

    event_type = 'order-paid'
    # Add required, internally set properties after given additional
    # ones to ensure the former are not overridden by the latter.
    log_entry_data: OrderLogEntryData = {}
    if additional_log_entry_data is not None:
        log_entry_data.update(additional_log_entry_data)
    log_entry_data.update(
        {
            'initiator_id': str(initiator.id),
            'former_payment_state': payment_state_from.name,
            'payment_method': payment_method,
        }
    )

    log_entry = DbOrderLogEntry(now, event_type, db_order.id, log_entry_data)
    db.session.add(log_entry)

    db.session.commit()

    order = _order_to_transfer_object(db_order)

    _execute_article_creation_actions(order, initiator.id)

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
    db_order: DbOrder,
    state: PaymentState,
    updated_at: datetime,
    initiator_id: UserID,
) -> None:
    db_order.payment_state = state
    db_order.payment_state_updated_at = updated_at
    db_order.payment_state_updated_by_id = initiator_id


def _execute_article_creation_actions(
    order: Order, initiator_id: UserID
) -> None:
    # based on article type
    for line_item in order.line_items:
        if line_item.article_type in (
            ArticleType.ticket,
            ArticleType.ticket_bundle,
        ):
            article = article_service.get_article_by_number(
                line_item.article_number
            )

            ticket_category_id = TicketCategoryID(
                UUID(str(article.type_params['ticket_category_id']))
            )

            if line_item.article_type == ArticleType.ticket:
                ticket_quantity = line_item.quantity

                ticket_actions.create_tickets(
                    order,
                    line_item,
                    ticket_category_id,
                    initiator_id,
                )
            elif line_item.article_type == ArticleType.ticket_bundle:
                ticket_quantity_per_bundle = int(
                    article.type_params['ticket_quantity']
                )
                bundle_quantity = line_item.quantity

                ticket_bundle_actions.create_ticket_bundles(
                    order,
                    line_item,
                    ticket_category_id,
                    ticket_quantity_per_bundle,
                    initiator_id,
                )

    # based on order action registered for article number
    action_service.execute_creation_actions(order, initiator_id)


def _execute_article_revocation_actions(
    order: Order, initiator_id: UserID
) -> None:
    # based on article type
    for line_item in order.line_items:
        if line_item.article_type == ArticleType.ticket:
            ticket_actions.revoke_tickets(order, line_item, initiator_id)
        elif line_item.article_type == ArticleType.ticket_bundle:
            ticket_bundle_actions.revoke_ticket_bundles(
                order, line_item, initiator_id
            )

    # based on order action registered for article number
    action_service.execute_revocation_actions(order, initiator_id)


def update_line_item_processing_result(
    line_item_id: LineItemID, data: dict[str, Any]
) -> None:
    """Update the line item's processing result data."""
    db_line_item = db.session.get(DbLineItem, line_item_id)

    if db_line_item is None:
        raise ValueError(f'Unknown line item ID "{line_item_id}"')

    db_line_item.processing_result = data
    db.session.commit()


def delete_order(order_id: OrderID) -> None:
    """Delete an order."""
    order = get_order(order_id)

    db.session.query(DbOrderLogEntry) \
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
    return db.session.get(DbOrder, order_id)


def _get_order_entity(order_id: OrderID) -> DbOrder:
    """Return the order database entity with that id, or raise an
    exception.
    """
    db_order = _find_order_entity(order_id)

    if db_order is None:
        raise ValueError(f'Unknown order ID "{order_id}"')

    return db_order


def find_order(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    db_order = _find_order_entity(order_id)

    if db_order is None:
        return None

    return _order_to_transfer_object(db_order)


def get_order(order_id: OrderID) -> Order:
    """Return the order with that id, or raise an exception."""
    db_order = _get_order_entity(order_id)
    return _order_to_transfer_object(db_order)


def find_order_with_details(order_id: OrderID) -> Optional[Order]:
    """Return the order with that id, or `None` if not found."""
    db_order = db.session.query(DbOrder) \
        .options(
            db.joinedload(DbOrder.line_items),
        ) \
        .get(order_id)

    if db_order is None:
        return None

    return _order_to_transfer_object(db_order)


def find_order_by_order_number(order_number: OrderNumber) -> Optional[Order]:
    """Return the order with that order number, or `None` if not found."""
    db_order = db.session \
        .query(DbOrder) \
        .filter_by(order_number=order_number) \
        .one_or_none()

    if db_order is None:
        return None

    return _order_to_transfer_object(db_order)


def get_orders_for_order_numbers(
    order_numbers: set[OrderNumber],
) -> Sequence[Order]:
    """Return the orders with those order numbers."""
    if not order_numbers:
        return []

    db_orders = db.session.execute(
        select(DbOrder)
        .options(db.joinedload(DbOrder.line_items))
        .filter(DbOrder.order_number.in_(order_numbers))
    ).scalars().unique().all()

    return list(map(_order_to_transfer_object, db_orders))


def get_order_ids_for_order_numbers(
    order_numbers: set[OrderNumber],
) -> dict[OrderNumber, OrderID]:
    """Return the order IDs for those order numbers."""
    if not order_numbers:
        return {}

    order_ids_and_numbers = db.session.execute(
        select(DbOrder.id, DbOrder.order_number)
        .filter(DbOrder.order_number.in_(order_numbers))
    ).all()

    return {
        order_number: order_id
        for order_id, order_number in order_ids_and_numbers
    }


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


def get_orders(order_ids: frozenset[OrderID]) -> list[Order]:
    """Return the orders with these ids."""
    if not order_ids:
        return []

    db_orders = db.session.execute(
        select(DbOrder)
        .options(db.joinedload(DbOrder.line_items))
        .filter(DbOrder.id.in_(order_ids))
    ).scalars().unique().all()

    return [_order_to_transfer_object(db_order) for db_order in db_orders]


def get_orders_for_shop_paginated(
    shop_id: ShopID,
    page: int,
    per_page: int,
    *,
    search_term=None,
    only_payment_state: Optional[PaymentState] = None,
    only_processed: Optional[bool] = None,
) -> Pagination:
    """Return all orders for that shop, ordered by creation date.

    If a payment state is specified, only orders in that state are
    returned.
    """
    items_query = select(DbOrder) \
        .options(db.joinedload(DbOrder.line_items)) \
        .filter_by(shop_id=shop_id) \
        .order_by(DbOrder.created_at.desc())

    count_query = select(db.func.count(DbOrder.id)) \
        .filter_by(shop_id=shop_id) \

    if search_term:
        ilike_pattern = f'%{search_term}%'
        items_query = items_query \
            .filter(DbOrder.order_number.ilike(ilike_pattern))
        count_query = count_query \
            .filter(DbOrder.order_number.ilike(ilike_pattern))

    if only_payment_state is not None:
        items_query = items_query.filter_by(_payment_state=only_payment_state.name)
        count_query = count_query.filter_by(_payment_state=only_payment_state.name)

    if only_processed is not None:
        items_query = items_query.filter(DbOrder.processing_required == True)
        count_query = count_query.filter(DbOrder.processing_required == True)

        if only_processed:
            items_query = items_query.filter(DbOrder.processed_at != None)
            count_query = count_query.filter(DbOrder.processed_at != None)
        else:
            items_query = items_query.filter(DbOrder.processed_at == None)
            count_query = count_query.filter(DbOrder.processed_at == None)

    return paginate(
        items_query,
        count_query,
        page,
        per_page,
        scalar_result=True,
        unique_result=True,
        item_mapper=_order_to_transfer_object,
    )


def get_orders_placed_by_user(user_id: UserID) -> Sequence[Order]:
    """Return orders placed by the user."""
    db_orders = db.session \
        .query(DbOrder) \
        .options(
            db.joinedload(DbOrder.line_items),
        ) \
        .filter_by(placed_by_id=user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()

    return list(map(_order_to_transfer_object, db_orders))


def get_orders_placed_by_user_for_storefront(
    user_id: UserID, storefront_id: StorefrontID
) -> list[Order]:
    """Return orders placed by the user through that storefront."""
    db_orders = db.session \
        .query(DbOrder) \
        .options(
            db.joinedload(DbOrder.line_items),
        ) \
        .filter_by(storefront_id=storefront_id) \
        .filter_by(placed_by_id=user_id) \
        .order_by(DbOrder.created_at.desc()) \
        .all()

    return list(map(_order_to_transfer_object, db_orders))


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

    line_items = list(map(line_item_to_transfer_object, order.line_items))

    state = _get_order_state(order)
    is_open = order.payment_state == PaymentState.open
    is_canceled = _is_canceled(order)
    is_paid = _is_paid(order)
    is_invoiced = order.invoice_created_at is not None
    is_processing_required = order.processing_required
    is_processed = order.processed_at is not None

    return Order(
        id=order.id,
        created_at=order.created_at,
        shop_id=order.shop_id,
        storefront_id=order.storefront_id,
        order_number=order.order_number,
        placed_by_id=order.placed_by_id,
        first_name=order.first_name,
        last_name=order.last_name,
        address=address,
        total_amount=order.total_amount,
        line_items=line_items,
        payment_method=order.payment_method,
        payment_state=order.payment_state,
        state=state,
        is_open=is_open,
        is_canceled=is_canceled,
        is_paid=is_paid,
        is_invoiced=is_invoiced,
        is_processing_required=is_processing_required,
        is_processed=is_processed,
        cancelation_reason=order.cancelation_reason,
    )


def line_item_to_transfer_object(
    db_line_item: DbLineItem,
) -> LineItem:
    """Create transfer object from line item database entity."""
    return LineItem(
        id=db_line_item.id,
        order_number=db_line_item.order_number,
        article_number=db_line_item.article_number,
        article_type=db_line_item.article_type,
        description=db_line_item.description,
        unit_price=db_line_item.unit_price,
        tax_rate=db_line_item.tax_rate,
        quantity=db_line_item.quantity,
        line_amount=db_line_item.line_amount,
        processing_result=db_line_item.processing_result or {},
    )


def _get_order_state(db_order: DbOrder) -> OrderState:
    is_canceled = _is_canceled(db_order)
    is_paid = _is_paid(db_order)
    is_processing_required = db_order.processing_required
    is_processed = db_order.processed_at is not None

    if is_canceled:
        return OrderState.canceled

    if is_paid:
        if not is_processing_required or is_processed:
            return OrderState.complete

    return OrderState.open


def _is_canceled(db_order: DbOrder) -> bool:
    return db_order.payment_state in {
        PaymentState.canceled_before_paid,
        PaymentState.canceled_after_paid,
    }


def _is_paid(db_order: DbOrder) -> bool:
    return db_order.payment_state == PaymentState.paid

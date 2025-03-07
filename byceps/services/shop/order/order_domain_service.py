"""
byceps.services.shop.order.order_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import datetime, timedelta
import dataclasses

from moneyed import Currency, Money

from byceps.services.core.events import EventUser
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.product import product_domain_service
from byceps.services.shop.product.models import ProductWithQuantity
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .errors import (
    CartEmptyError,
    OrderAlreadyCanceledError,
    OrderAlreadyMarkedAsPaidError,
)
from .events import ShopOrderCanceledEvent, ShopOrderPaidEvent
from .models.checkout import IncomingLineItem, IncomingOrder
from .models.log import OrderLogEntry, OrderLogEntryData
from .models.order import (
    Address,
    LineItemID,
    Order,
    Orderer,
    OrderID,
    PaymentState,
)
from .models.payment import AdditionalPaymentData, Payment


OVERDUE_THRESHOLD = timedelta(days=14)


def place_order(
    created_at: datetime,
    shop_id: ShopID,
    storefront_id: StorefrontID,
    orderer: Orderer,
    currency: Currency,
    cart: Cart,
) -> Result[tuple[IncomingOrder, OrderLogEntry], CartEmptyError]:
    """Place an order."""
    cart_items = cart.get_items()
    if not cart_items:
        return Err(CartEmptyError())

    line_items = list(_build_incoming_line_items(cart_items))

    total_amount = product_domain_service.calculate_total_amount(cart_items)

    processing_required = any(
        line_item.processing_required for line_item in line_items
    )

    incoming_order = IncomingOrder(
        id=OrderID(generate_uuid7()),
        created_at=created_at,
        shop_id=shop_id,
        storefront_id=storefront_id,
        orderer=orderer,
        line_items=line_items,
        total_amount=total_amount,
        processing_required=processing_required,
    )

    log_entry = _build_order_placed_log_entry(incoming_order)

    return Ok((incoming_order, log_entry))


def _build_incoming_line_items(
    cart_items: list[ProductWithQuantity],
) -> Iterator[IncomingLineItem]:
    """Build incoming line item objects from the cart's content."""
    for cart_item in cart_items:
        product = cart_item.product
        quantity = cart_item.quantity
        line_amount = cart_item.amount

        yield IncomingLineItem(
            id=LineItemID(generate_uuid7()),
            product_id=product.id,
            product_number=product.item_number,
            product_type=product.type_,
            name=product.name,
            unit_price=product.price,
            tax_rate=product.tax_rate,
            quantity=quantity,
            line_amount=line_amount,
            processing_required=product.processing_required,
        )


def _build_order_placed_log_entry(
    incoming_order: IncomingOrder,
) -> OrderLogEntry:
    data = {
        'initiator_id': str(incoming_order.orderer.user.id),
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=incoming_order.created_at,
        event_type='order-placed',
        order_id=incoming_order.id,
        data=data,
    )


def update_orderer(
    original_order: Order,
    new_orderer: Orderer,
    has_payments: bool,
    initiator: User,
) -> Result[tuple[Order, OrderLogEntry], str]:
    """Update the order's orderer."""
    if not original_order.is_open:
        return Err('Orderer can only be updated on open orders.')

    if has_payments:
        return Err('Orderer can only be updated on orders without payments.')

    if not all(
        [
            new_orderer.first_name,
            new_orderer.last_name,
            new_orderer.country,
            new_orderer.zip_code,
            new_orderer.city,
            new_orderer.street,
        ]
    ):
        return Err("New orderer's info is incomplete.")

    updated_order = dataclasses.replace(
        original_order,
        placed_by=new_orderer.user,
        company=new_orderer.company,
        first_name=new_orderer.first_name,
        last_name=new_orderer.last_name,
        address=Address(
            country=new_orderer.country,
            zip_code=new_orderer.zip_code,
            city=new_orderer.city,
            street=new_orderer.street,
        ),
    )

    log_entry = _build_orderer_updated_log_entry(
        original_order, updated_order, initiator
    )

    return Ok((updated_order, log_entry))


def _build_orderer_updated_log_entry(
    original_order: Order,
    updated_order: Order,
    initiator: User,
) -> OrderLogEntry:
    fields = {
        'placed_by_id': {
            'old': str(original_order.placed_by.id),
            'new': str(updated_order.placed_by.id),
        },
        'placed_by_screen_name': {
            'old': original_order.placed_by.screen_name,
            'new': updated_order.placed_by.screen_name,
        },
        'company': {
            'old': original_order.company,
            'new': updated_order.company,
        },
        'first_name': {
            'old': original_order.first_name,
            'new': updated_order.first_name,
        },
        'last_name': {
            'old': original_order.last_name,
            'new': updated_order.last_name,
        },
        'country': {
            'old': original_order.address.country,
            'new': updated_order.address.country,
        },
        'zip_code': {
            'old': original_order.address.zip_code,
            'new': updated_order.address.zip_code,
        },
        'city': {
            'old': original_order.address.city,
            'new': updated_order.address.city,
        },
        'street': {
            'old': original_order.address.street,
            'new': updated_order.address.street,
        },
    }

    data = {
        'fields': fields,
        'initiator_id': str(initiator.id),
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=datetime.utcnow(),
        event_type='order-orderer-updated',
        order_id=original_order.id,
        data=data,
    )


def add_note(order: Order, author: User, text: str) -> OrderLogEntry:
    log_entry = _build_note_log_entry(order.id, author, text)

    return log_entry


def _build_note_log_entry(
    order_id: OrderID,
    author: User,
    text: str,
) -> OrderLogEntry:
    data = {
        'author_id': str(author.id),
        'text': text,
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=datetime.utcnow(),
        event_type='order-note-added',
        order_id=order_id,
        data=data,
    )


def set_shipped_flag(
    order: Order, initiator: User
) -> Result[OrderLogEntry, str]:
    if not order.is_processing_required:
        return Err('Order contains no items that require shipping.')

    log_entry = _build_set_shipped_flag_log_entry(order.id, initiator)

    return Ok(log_entry)


def _build_set_shipped_flag_log_entry(
    order_id: OrderID, initiator: User
) -> OrderLogEntry:
    data = {
        'initiator_id': str(initiator.id),
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=datetime.utcnow(),
        event_type='order-shipped',
        order_id=order_id,
        data=data,
    )


def unset_shipped_flag(
    order: Order, initiator: User
) -> Result[OrderLogEntry, str]:
    if not order.is_processing_required:
        return Err('Order contains no items that require shipping.')

    log_entry = _build_unset_shipped_flag_log_entry(order.id, initiator)

    return Ok(log_entry)


def _build_unset_shipped_flag_log_entry(
    order_id: OrderID, initiator: User
) -> OrderLogEntry:
    data = {
        'initiator_id': str(initiator.id),
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=datetime.utcnow(),
        event_type='order-shipped-withdrawn',
        order_id=order_id,
        data=data,
    )


def create_payment(
    order: Order,
    created_at: datetime,
    method: str,
    amount: Money,
    initiator: User,
    additional_data: AdditionalPaymentData,
) -> tuple[Payment, OrderLogEntry]:
    payment = _build_payment(
        order.id, created_at, method, amount, additional_data
    )
    log_entry = _build_payment_log_entry(payment, initiator)

    return payment, log_entry


def _build_payment(
    order_id: OrderID,
    created_at: datetime,
    method: str,
    amount: Money,
    additional_data: AdditionalPaymentData,
) -> Payment:
    return Payment(
        id=generate_uuid7(),
        order_id=order_id,
        created_at=created_at,
        method=method,
        amount=amount,
        additional_data=additional_data,
    )


def _build_payment_log_entry(
    payment: Payment, initiator: User
) -> OrderLogEntry:
    data = {
        'payment_id': str(payment.id),
        'initiator_id': str(initiator.id),
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=payment.created_at,
        event_type='order-payment-created',
        order_id=payment.order_id,
        data=data,
    )


def mark_order_as_paid(
    order: Order,
    orderer_user: User,
    occurred_at: datetime,
    payment_method: str,
    additional_payment_data: AdditionalPaymentData | None,
    initiator: User,
) -> Result[
    tuple[ShopOrderPaidEvent, OrderLogEntry],
    OrderAlreadyMarkedAsPaidError,
]:
    if _is_paid(order):
        return Err(OrderAlreadyMarkedAsPaidError())

    payment_state_from = order.payment_state

    event = _build_order_paid_event(
        occurred_at, order, orderer_user, payment_method, initiator
    )

    log_entry = _build_order_paid_log_entry(
        occurred_at,
        order.id,
        payment_state_from,
        payment_method,
        additional_payment_data,
        initiator,
    )

    return Ok((event, log_entry))


def _build_order_paid_event(
    occurred_at: datetime,
    order: Order,
    orderer_user: User,
    payment_method: str,
    initiator: User,
) -> ShopOrderPaidEvent:
    return ShopOrderPaidEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        order_id=order.id,
        order_number=order.order_number,
        orderer=EventUser.from_user(orderer_user),
        payment_method=payment_method,
    )


def _build_order_paid_log_entry(
    occurred_at: datetime,
    order_id: OrderID,
    payment_state_from: PaymentState,
    payment_method: str,
    additional_payment_data: AdditionalPaymentData | None,
    initiator: User,
) -> OrderLogEntry:
    data: OrderLogEntryData = {}

    # Add required, internally set properties after given additional
    # ones to ensure the former are not overridden by the latter.

    if additional_payment_data is not None:
        data.update(additional_payment_data)

    data.update(
        {
            'former_payment_state': payment_state_from.name,
            'payment_method': payment_method,
            'initiator_id': str(initiator.id),
        }
    )

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type='order-paid',
        order_id=order_id,
        data=data,
    )


def cancel_order(
    order: Order,
    orderer_user: User,
    occurred_at: datetime,
    reason: str,
    initiator: User,
) -> Result[
    tuple[ShopOrderCanceledEvent, OrderLogEntry],
    OrderAlreadyCanceledError,
]:
    if _is_canceled(order):
        return Err(OrderAlreadyCanceledError())

    has_order_been_paid = _is_paid(order)

    payment_state_from = order.payment_state

    event = _build_order_canceled_event(
        occurred_at, order, orderer_user, initiator
    )

    log_entry = _build_order_canceled_log_entry(
        occurred_at,
        order.id,
        has_order_been_paid,
        payment_state_from,
        reason,
        initiator,
    )

    return Ok((event, log_entry))


def _build_order_canceled_event(
    occurred_at: datetime,
    order: Order,
    orderer_user: User,
    initiator: User,
) -> ShopOrderCanceledEvent:
    return ShopOrderCanceledEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(initiator),
        order_id=order.id,
        order_number=order.order_number,
        orderer=EventUser.from_user(orderer_user),
    )


def _build_order_canceled_log_entry(
    occurred_at: datetime,
    order_id: OrderID,
    has_order_been_paid: bool,
    payment_state_from: PaymentState,
    reason: str,
    initiator: User,
) -> OrderLogEntry:
    event_type = (
        'order-canceled-after-paid'
        if has_order_been_paid
        else 'order-canceled-before-paid'
    )

    data = {
        'former_payment_state': payment_state_from.name,
        'reason': reason,
        'initiator_id': str(initiator.id),
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=occurred_at,
        event_type=event_type,
        order_id=order_id,
        data=data,
    )


def _is_paid(order: Order) -> bool:
    return order.payment_state == PaymentState.paid


def _is_canceled(order: Order) -> bool:
    return order.payment_state in {
        PaymentState.canceled_before_paid,
        PaymentState.canceled_after_paid,
    }


def is_overdue(created_at: datetime, payment_state: PaymentState) -> bool:
    """Return `True` if payment of the order is overdue."""
    if payment_state != PaymentState.open:
        return False

    return datetime.utcnow() >= (created_at + OVERDUE_THRESHOLD)

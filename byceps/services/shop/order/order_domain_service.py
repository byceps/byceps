"""
byceps.services.shop.order.order_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime

from moneyed import Money

from byceps.database import generate_uuid7
from byceps.events.shop import ShopOrderCanceledEvent, ShopOrderPaidEvent
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from .errors import OrderAlreadyCanceledError, OrderAlreadyMarkedAsPaidError
from .models.log import OrderLogEntry, OrderLogEntryData
from .models.order import Order, OrderID, PaymentState
from .models.payment import AdditionalPaymentData, Payment


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
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
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
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
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

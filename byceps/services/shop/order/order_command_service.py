"""
byceps.services.shop.order.order_command_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Any
from uuid import UUID

import structlog

from byceps.database import db
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import ProductType
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.ticketing import ticket_category_service
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result

from . import (
    order_action_service,
    order_domain_service,
    order_log_service,
    order_payment_service,
)
from .actions import (
    ticket as ticket_actions,
    ticket_bundle as ticket_bundle_actions,
)
from .dbmodels.line_item import DbLineItem
from .dbmodels.order import DbOrder
from .errors import (
    OrderActionFailedError,
    OrderAlreadyCanceledError,
    OrderAlreadyMarkedAsPaidError,
)
from .events import ShopOrderCanceledEvent, ShopOrderPaidEvent
from .models.log import OrderLogEntry
from .models.order import (
    LineItemID,
    Order,
    Orderer,
    OrderID,
    PaidOrder,
    PaymentState,
)
from .models.payment import AdditionalPaymentData
from .order_helper_service import to_order, to_paid_order, _is_paid
from .order_service import get_db_order


log = structlog.get_logger()


def update_orderer(
    order_id: OrderID, new_orderer: Orderer, initiator: User
) -> Result[Order, str]:
    """Update the order's orderer."""
    db_order = get_db_order(order_id)

    original_orderer_user = user_service.get_user(db_order.placed_by_id)
    original_order = to_order(db_order, original_orderer_user)

    payments = order_payment_service.get_payments_for_order(original_order.id)
    has_payments = bool(payments)

    update_result = order_domain_service.update_orderer(
        original_order, new_orderer, has_payments, initiator
    )

    if update_result.is_err():
        return Err(update_result.unwrap_err())

    updated_order, log_entry = update_result.unwrap()

    db_order.placed_by_id = updated_order.placed_by.id
    db_order.company = updated_order.company
    db_order.first_name = updated_order.first_name
    db_order.last_name = updated_order.last_name
    db_order.country = updated_order.address.country
    db_order.postal_code = updated_order.address.postal_code
    db_order.city = updated_order.address.city
    db_order.street = updated_order.address.street

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    return Ok(updated_order)


def add_note(order: Order, author: User, text: str) -> None:
    """Add a note to the order."""
    log_entry = order_domain_service.add_note(order, author, text)

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)
    db.session.commit()


def set_shipped_flag(order: Order, initiator: User) -> Result[None, str]:
    """Mark the order as shipped."""
    set_shipped_flag_result = order_domain_service.set_shipped_flag(
        order, initiator
    )

    if set_shipped_flag_result.is_err():
        return Err(set_shipped_flag_result.unwrap_err())

    log_entry = set_shipped_flag_result.unwrap()

    _persist_shipped_flag(log_entry, log_entry.occurred_at)

    return Ok(None)


def unset_shipped_flag(order: Order, initiator: User) -> Result[None, str]:
    """Mark the order as not shipped."""
    unset_shipped_flag_result = order_domain_service.unset_shipped_flag(
        order, initiator
    )

    if unset_shipped_flag_result.is_err():
        return Err(unset_shipped_flag_result.unwrap_err())

    log_entry = unset_shipped_flag_result.unwrap()

    _persist_shipped_flag(log_entry, None)

    return Ok(None)


def _persist_shipped_flag(
    log_entry: OrderLogEntry, processed_at: datetime | None
) -> None:
    db_order = get_db_order(log_entry.order_id)

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db_order.processed_at = processed_at

    db.session.commit()


def cancel_order(
    order_id: OrderID, initiator: User, reason: str
) -> Result[
    tuple[Order, ShopOrderCanceledEvent],
    OrderActionFailedError | OrderAlreadyCanceledError,
]:
    """Cancel the order.

    Reserved quantities of products from that order are made available
    again.
    """
    db_order = get_db_order(order_id)

    orderer_user = user_service.get_user(db_order.placed_by_id)
    order = to_order(db_order, orderer_user)

    occurred_at = datetime.utcnow()

    cancel_order_result = order_domain_service.cancel_order(
        order,
        orderer_user,
        occurred_at,
        reason,
        initiator,
    )
    if cancel_order_result.is_err():
        return Err(cancel_order_result.unwrap_err())

    event, log_entry = cancel_order_result.unwrap()

    payment_state_to = (
        PaymentState.canceled_after_paid
        if _is_paid(db_order)
        else PaymentState.canceled_before_paid
    )

    _update_payment_state(db_order, payment_state_to, occurred_at, initiator)
    db_order.cancellation_reason = reason

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    # Make the reserved quantity of products available again.
    for db_line_item in db_order.line_items:
        product_service.increase_quantity(
            db_line_item.product.id, db_line_item.quantity, commit=False
        )

    db.session.commit()

    canceled_order = to_order(db_order, orderer_user)

    if payment_state_to == PaymentState.canceled_after_paid:
        match _execute_product_revocation_actions(canceled_order, initiator):
            case Err(e):
                return Err(e)

    log.info('Order canceled', shop_order_canceled_event=event)

    return Ok((canceled_order, event))


def mark_order_as_paid(
    order_id: OrderID,
    payment_method: str,
    initiator: User,
    *,
    additional_payment_data: AdditionalPaymentData | None = None,
) -> Result[
    tuple[PaidOrder, ShopOrderPaidEvent],
    OrderActionFailedError | OrderAlreadyMarkedAsPaidError,
]:
    """Mark the order as paid."""
    db_order = get_db_order(order_id)

    orderer_user = user_service.get_user(db_order.placed_by_id)
    order = to_order(db_order, orderer_user)

    payment_added_at = datetime.utcnow()

    order_payment_service.add_payment(
        order,
        payment_added_at,
        payment_method,
        order.total_amount,
        initiator,
        additional_payment_data if additional_payment_data is not None else {},
    )

    # Use separate timestamp so that log events are properly ordered.
    marked_as_paid_at = datetime.utcnow()

    mark_order_as_paid_result = order_domain_service.mark_order_as_paid(
        order,
        orderer_user,
        marked_as_paid_at,
        payment_method,
        additional_payment_data,
        initiator,
    )
    if mark_order_as_paid_result.is_err():
        return Err(mark_order_as_paid_result.unwrap_err())

    event, log_entry = mark_order_as_paid_result.unwrap()

    db_order.payment_method = payment_method
    _update_payment_state(
        db_order, PaymentState.paid, marked_as_paid_at, initiator
    )

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()

    paid_order = to_paid_order(db_order, orderer_user)

    match _execute_product_creation_actions(paid_order, initiator):
        case Err(e):
            return Err(e)

    log.info('Order paid', shop_order_paid_event=event)

    return Ok((paid_order, event))


def _update_payment_state(
    db_order: DbOrder,
    state: PaymentState,
    updated_at: datetime,
    initiator: User,
) -> None:
    db_order.payment_state = state
    db_order.payment_state_updated_at = updated_at
    db_order.payment_state_updated_by_id = initiator.id


def _execute_product_creation_actions(
    order: PaidOrder, initiator: User
) -> Result[None, OrderActionFailedError]:
    # based on product type
    for line_item in order.line_items:
        match line_item.product_type:
            case ProductType.ticket:
                product = product_service.get_product(line_item.product_id)

                ticket_category_id = TicketCategoryID(
                    UUID(str(product.type_params['ticket_category_id']))
                )
                ticket_category = ticket_category_service.get_category(
                    ticket_category_id
                )

                ticket_actions.create_tickets(
                    order,
                    line_item,
                    ticket_category,
                    initiator,
                )
            case ProductType.ticket_bundle:
                product = product_service.get_product(line_item.product_id)

                ticket_category_id = TicketCategoryID(
                    UUID(str(product.type_params['ticket_category_id']))
                )
                ticket_category = ticket_category_service.get_category(
                    ticket_category_id
                )

                ticket_quantity_per_bundle = int(
                    product.type_params['ticket_quantity']
                )

                ticket_bundle_actions.create_ticket_bundles(
                    order,
                    line_item,
                    ticket_category,
                    ticket_quantity_per_bundle,
                    initiator,
                )

    # based on order action registered for product number
    return order_action_service.execute_creation_actions(order, initiator)


def _execute_product_revocation_actions(
    order: Order, initiator: User
) -> Result[None, OrderActionFailedError]:
    # based on product type
    for line_item in order.line_items:
        match line_item.product_type:
            case ProductType.ticket:
                ticket_actions.revoke_tickets(order, line_item, initiator)
            case ProductType.ticket_bundle:
                match ticket_bundle_actions.revoke_ticket_bundles(
                    order, line_item, initiator
                ):
                    case Err(e):
                        return Err(OrderActionFailedError(e))

    # based on order action registered for product number
    return order_action_service.execute_revocation_actions(order, initiator)


def update_line_item_processing_result(
    line_item_id: LineItemID, data: dict[str, Any]
) -> None:
    """Update the line item's processing result data."""
    db_line_item = db.session.get(DbLineItem, line_item_id)

    if db_line_item is None:
        raise ValueError(f'Unknown line item ID "{line_item_id}"')

    db_line_item.processing_result = data
    db_line_item.processed_at = datetime.utcnow()
    db.session.commit()

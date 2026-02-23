"""
byceps.services.shop.order.order_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import datetime, timedelta
import dataclasses

from moneyed import Money

from byceps.services.shop.cart.models import Cart
from byceps.services.shop.product import product_domain_service
from byceps.services.shop.product.models import ProductWithQuantity
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.models import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .errors import (
    CartEmptyError,
    OrderAlreadyCanceledError,
    OrderAlreadyMarkedAsPaidError,
)
from .events import ShopOrderCanceledEvent, ShopOrderPaidEvent
from .log import order_log_domain_service
from .log.models import OrderLogEntry
from .models.checkout import IncomingLineItem, IncomingOrder
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

    log_entry = order_log_domain_service.build_order_placed_entry(
        incoming_order.created_at,
        incoming_order.id,
        incoming_order.orderer.user,
    )

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
            new_orderer.postal_code,
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
            postal_code=new_orderer.postal_code,
            city=new_orderer.city,
            street=new_orderer.street,
        ),
    )

    match _build_orderer_updated_log_entry(
        original_order, updated_order, initiator
    ):
        case Ok(value):
            log_entry = value
        case Err(e):
            return Err(e)

    return Ok((updated_order, log_entry))


def _build_orderer_updated_log_entry(
    original_order: Order,
    updated_order: Order,
    initiator: User,
) -> Result[OrderLogEntry, str]:
    fields: dict[str, dict[str, str | None]] = {}

    def _add_if_different(
        property_key: str,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        if old_value != new_value:
            fields[property_key] = {'old': old_value, 'new': new_value}

    placed_by_id_old = str(original_order.placed_by.id)
    placed_by_id_new = str(updated_order.placed_by.id)
    _add_if_different('placed_by_id', placed_by_id_old, placed_by_id_new)

    placed_by_screen_name_old = original_order.placed_by.screen_name
    placed_by_screen_name_new = updated_order.placed_by.screen_name
    _add_if_different(
        'placed_by_screen_name',
        placed_by_screen_name_old,
        placed_by_screen_name_new,
    )

    company_old = original_order.company
    company_new = updated_order.company
    _add_if_different('company', company_old, company_new)

    first_name_old = original_order.first_name
    first_name_new = updated_order.first_name
    _add_if_different('first_name', first_name_old, first_name_new)

    last_name_old = original_order.last_name
    last_name_new = updated_order.last_name
    _add_if_different('last_name', last_name_old, last_name_new)

    country_old = original_order.address.country
    country_new = updated_order.address.country
    _add_if_different('country', country_old, country_new)

    postal_code_old = original_order.address.postal_code
    postal_code_new = updated_order.address.postal_code
    _add_if_different('postal_code', postal_code_old, postal_code_new)

    city_old = original_order.address.city
    city_new = updated_order.address.city
    _add_if_different('city', city_old, city_new)

    street_old = original_order.address.street
    street_new = updated_order.address.street
    _add_if_different('street', street_old, street_new)

    if not fields:
        return Err('No orderer fields have changed.')

    log_entry = order_log_domain_service.build_orderer_updated_entry(
        original_order.id, fields, initiator
    )

    return Ok(log_entry)


def add_note(order: Order, author: User, text: str) -> OrderLogEntry:
    return order_log_domain_service.build_note_added_entry(
        order.id, author, text
    )


def set_shipped_flag(
    order: Order, initiator: User
) -> Result[OrderLogEntry, str]:
    if not order.is_processing_required:
        return Err('Order contains no items that require shipping.')

    log_entry = order_log_domain_service.build_set_shipped_flag_entry(
        order.id, initiator
    )

    return Ok(log_entry)


def unset_shipped_flag(
    order: Order, initiator: User
) -> Result[OrderLogEntry, str]:
    if not order.is_processing_required:
        return Err('Order contains no items that require shipping.')

    log_entry = order_log_domain_service.build_unset_shipped_flag_entry(
        order.id, initiator
    )

    return Ok(log_entry)


def create_payment(
    order: Order,
    created_at: datetime,
    method: str,
    amount: Money,
    initiator: User,
    additional_data: AdditionalPaymentData,
) -> Result[tuple[Payment, OrderLogEntry], OrderAlreadyCanceledError]:
    if _is_canceled(order):
        return Err(OrderAlreadyCanceledError())

    payment = _build_payment(
        order.id, created_at, method, amount, additional_data
    )

    log_entry = order_log_domain_service.build_payment_created_entry(
        payment, initiator
    )

    return Ok((payment, log_entry))


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


def mark_order_as_paid(
    order: Order,
    orderer_user: User,
    occurred_at: datetime,
    payment_method: str,
    additional_payment_data: AdditionalPaymentData | None,
    initiator: User,
) -> Result[
    tuple[ShopOrderPaidEvent, OrderLogEntry],
    OrderAlreadyCanceledError | OrderAlreadyMarkedAsPaidError,
]:
    if _is_canceled(order):
        return Err(OrderAlreadyCanceledError())

    if _is_paid(order):
        return Err(OrderAlreadyMarkedAsPaidError())

    payment_state_from = order.payment_state

    event = _build_order_paid_event(
        occurred_at, order, orderer_user, payment_method, initiator
    )

    log_entry = order_log_domain_service.build_order_paid_entry(
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
        initiator=initiator,
        order_id=order.id,
        order_number=order.order_number,
        orderer=orderer_user,
        payment_method=payment_method,
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

    log_entry = order_log_domain_service.build_order_canceled_entry(
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
        initiator=initiator,
        order_id=order.id,
        order_number=order.order_number,
        orderer=orderer_user,
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

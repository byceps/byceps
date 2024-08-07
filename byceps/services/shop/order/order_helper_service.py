"""
byceps.services.shop.order.order_helper_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from moneyed import Currency, Money

from byceps.services.user.models.user import User, UserID

from . import order_domain_service
from .dbmodels.line_item import DbLineItem
from .dbmodels.order import DbOrder
from .models.detailed_order import DetailedOrder
from .models.order import (
    AdminOrderListItem,
    Address,
    LineItem,
    LineItemProcessingState,
    Order,
    OrderState,
    PaymentState,
    SiteOrderListItem,
)


def to_detailed_order(db_order: DbOrder, placed_by: User) -> DetailedOrder:
    """Create detailed order transfer object from database entity."""
    return DetailedOrder(
        id=db_order.id,
        created_at=db_order.created_at,
        shop_id=db_order.shop_id,
        storefront_id=db_order.storefront_id,
        order_number=db_order.order_number,
        placed_by=placed_by,
        company=db_order.company,
        first_name=db_order.first_name,
        last_name=db_order.last_name,
        address=_get_address(db_order),
        total_amount=db_order.total_amount,
        line_items=_get_line_items(db_order),
        payment_method=db_order.payment_method,
        payment_state=db_order.payment_state,
        state=_get_order_state(db_order),
        is_open=_is_open(db_order),
        is_canceled=_is_canceled(db_order),
        is_paid=_is_paid(db_order),
        is_invoiced=_is_invoiced(db_order),
        is_overdue=_is_overdue(db_order),
        is_processing_required=db_order.processing_required,
        is_processed=_is_processed(db_order),
        cancellation_reason=db_order.cancellation_reason,
    )


def to_order(db_order: DbOrder, placed_by: User) -> Order:
    """Create order transfer object from database entity."""
    return Order(
        id=db_order.id,
        created_at=db_order.created_at,
        shop_id=db_order.shop_id,
        storefront_id=db_order.storefront_id,
        order_number=db_order.order_number,
        placed_by=placed_by,
        company=db_order.company,
        first_name=db_order.first_name,
        last_name=db_order.last_name,
        address=_get_address(db_order),
        total_amount=db_order.total_amount,
        line_items=_get_line_items(db_order),
        payment_method=db_order.payment_method,
        payment_state=db_order.payment_state,
        state=_get_order_state(db_order),
        is_open=_is_open(db_order),
        is_canceled=_is_canceled(db_order),
        is_paid=_is_paid(db_order),
        is_invoiced=_is_invoiced(db_order),
        is_overdue=_is_overdue(db_order),
        is_processing_required=db_order.processing_required,
        is_processed=_is_processed(db_order),
        cancellation_reason=db_order.cancellation_reason,
    )


def to_admin_order_list_item(
    db_order: DbOrder, orderers_by_id: dict[UserID, User]
) -> AdminOrderListItem:
    """Create admin order list item transfer object from database entity."""
    placed_by = orderers_by_id[db_order.placed_by_id]

    return AdminOrderListItem(
        id=db_order.id,
        created_at=db_order.created_at,
        order_number=db_order.order_number,
        placed_by=placed_by,
        first_name=db_order.first_name,
        last_name=db_order.last_name,
        total_amount=db_order.total_amount,
        payment_state=db_order.payment_state,
        state=_get_order_state(db_order),
        is_open=_is_open(db_order),
        is_canceled=_is_canceled(db_order),
        is_paid=_is_paid(db_order),
        is_invoiced=_is_invoiced(db_order),
        is_overdue=_is_overdue(db_order),
        is_processing_required=db_order.processing_required,
        is_processed=_is_processed(db_order),
    )


def to_site_order_list_item(
    db_order: DbOrder, orderers_by_id: dict[UserID, User]
) -> SiteOrderListItem:
    """Create site order list item transfer object from database entity."""
    placed_by = orderers_by_id[db_order.placed_by_id]

    return SiteOrderListItem(
        id=db_order.id,
        created_at=db_order.created_at,
        order_number=db_order.order_number,
        placed_by=placed_by,
        total_amount=db_order.total_amount,
        payment_state=db_order.payment_state,
        state=_get_order_state(db_order),
        is_open=_is_open(db_order),
        is_canceled=_is_canceled(db_order),
        is_paid=_is_paid(db_order),
        is_overdue=_is_overdue(db_order),
    )


def _get_address(db_order: DbOrder) -> Address:
    return Address(
        country=db_order.country,
        zip_code=db_order.zip_code,
        city=db_order.city,
        street=db_order.street,
    )


def _get_line_items(db_order: DbOrder) -> list[LineItem]:
    is_order_canceled = _is_canceled(db_order)

    line_items = [
        _line_item_to_transfer_object(
            db_line_item, db_order.currency, is_order_canceled
        )
        for db_line_item in db_order.line_items
    ]

    line_items.sort(key=lambda li: li.article_id)

    return line_items


def _is_overdue(db_order: DbOrder) -> bool:
    """Return `True` if payment of the order is overdue."""
    return order_domain_service.is_overdue(
        db_order.created_at, db_order.payment_state
    )


def _line_item_to_transfer_object(
    db_line_item: DbLineItem, currency: Currency, is_order_canceled: bool
) -> LineItem:
    """Create transfer object from line item database entity."""
    return LineItem(
        id=db_line_item.id,
        order_number=db_line_item.order_number,
        article_id=db_line_item.article_id,
        article_number=db_line_item.article_number,
        article_type=db_line_item.article_type,
        name=db_line_item.name,
        unit_price=Money(db_line_item.unit_price, currency),
        tax_rate=db_line_item.tax_rate,
        quantity=db_line_item.quantity,
        line_amount=Money(db_line_item.line_amount, currency),
        processing_required=db_line_item.processing_required,
        processing_result=db_line_item.processing_result or {},
        processed_at=db_line_item.processed_at,
        processing_state=_get_line_item_processing_state(
            db_line_item, is_order_canceled
        ),
    )


def _get_line_item_processing_state(
    db_line_item: DbLineItem, is_order_canceled: bool
) -> LineItemProcessingState:
    if not db_line_item.processing_required:
        return LineItemProcessingState.not_applicable

    if is_order_canceled:
        return LineItemProcessingState.canceled

    if db_line_item.processed_at is not None:
        return LineItemProcessingState.complete
    else:
        return LineItemProcessingState.pending


def _get_order_state(db_order: DbOrder) -> OrderState:
    is_canceled = _is_canceled(db_order)
    is_paid = _is_paid(db_order)
    is_processing_required = db_order.processing_required
    is_processed = _is_processed(db_order)

    if is_canceled:
        return OrderState.canceled

    if is_paid:
        if not is_processing_required or is_processed:
            return OrderState.complete

    return OrderState.open


def _is_open(db_order: DbOrder) -> bool:
    return db_order.payment_state == PaymentState.open


def _is_canceled(db_order: DbOrder) -> bool:
    return db_order.payment_state in {
        PaymentState.canceled_before_paid,
        PaymentState.canceled_after_paid,
    }


def _is_paid(db_order: DbOrder) -> bool:
    return db_order.payment_state == PaymentState.paid


def _is_invoiced(db_order: DbOrder) -> bool:
    return db_order.invoice_created_at is not None


def _is_processed(db_order: DbOrder) -> bool:
    return db_order.processed_at is not None

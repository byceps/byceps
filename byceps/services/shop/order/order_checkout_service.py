"""
byceps.services.shop.order.order_checkout_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterator
from datetime import datetime

from sqlalchemy.exc import IntegrityError
import structlog

from byceps.database import db
from byceps.services.core.events import EventUser
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.product import product_service
from byceps.services.shop.shop import shop_service
from byceps.services.shop.storefront.models import Storefront
from byceps.util.result import Err, Ok, Result

from . import (
    order_domain_service,
    order_helper_service,
    order_log_service,
    order_sequence_service,
)
from .dbmodels.line_item import DbLineItem
from .dbmodels.order import DbOrder
from .events import ShopOrderPlacedEvent
from .models.checkout import IncomingLineItem, IncomingOrder
from .models.number import OrderNumber
from .models.order import Order, Orderer


log = structlog.get_logger()


def place_order(
    storefront: Storefront,
    orderer: Orderer,
    cart: Cart,
    *,
    created_at: datetime | None = None,
) -> Result[tuple[Order, ShopOrderPlacedEvent], None]:
    """Place an order for one or more products."""
    shop = shop_service.get_shop(storefront.shop_id)

    order_number_sequence = order_sequence_service.get_order_number_sequence(
        storefront.order_number_sequence_id
    )
    order_number_generation_result = (
        order_sequence_service.generate_order_number(order_number_sequence.id)
    )
    if order_number_generation_result.is_err():
        error_message = order_number_generation_result.unwrap_err()
        log.error('Order placement failed', error_message=error_message)
        return Err(None)

    order_number = order_number_generation_result.unwrap()

    if created_at is None:
        created_at = datetime.utcnow()

    place_order_result = order_domain_service.place_order(
        created_at, shop.id, storefront.id, orderer, shop.currency, cart
    )
    if place_order_result.is_err():
        error_message = 'Cart must not be empty'
        log.error('Order placement failed', error_message=error_message)
        return Err(None)

    incoming_order, log_entry = place_order_result.unwrap()

    db_order = _build_db_order(incoming_order, order_number)

    db_line_items = list(
        _build_db_line_items(incoming_order.line_items, db_order)
    )

    db.session.add(db_order)
    db.session.add_all(db_line_items)

    _reduce_product_stock(incoming_order)

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    try:
        db.session.commit()
    except IntegrityError as e:
        log.error('Order placement failed', order_number=order_number, exc=e)
        db.session.rollback()
        return Err(None)

    order = order_helper_service.to_order(db_order, orderer.user)

    occurred_at = order.created_at

    event = ShopOrderPlacedEvent(
        occurred_at=occurred_at,
        initiator=EventUser.from_user(orderer.user),
        order_id=order.id,
        order_number=order.order_number,
        orderer=EventUser.from_user(orderer.user),
    )

    log.info('Order placed', shop_order_placed_event=event)

    return Ok((order, event))


def _build_db_order(
    incoming_order: IncomingOrder, order_number: OrderNumber
) -> DbOrder:
    """Build an order."""
    orderer = incoming_order.orderer

    return DbOrder(
        order_id=incoming_order.id,
        created_at=incoming_order.created_at,
        shop_id=incoming_order.shop_id,
        storefront_id=incoming_order.storefront_id,
        order_number=order_number,
        placed_by_id=orderer.user.id,
        company=orderer.company,
        first_name=orderer.first_name,
        last_name=orderer.last_name,
        country=orderer.country,
        zip_code=orderer.zip_code,
        city=orderer.city,
        street=orderer.street,
        total_amount=incoming_order.total_amount,
        processing_required=incoming_order.processing_required,
    )


def _build_db_line_items(
    incoming_line_items: list[IncomingLineItem], db_order: DbOrder
) -> Iterator[DbLineItem]:
    """Build line items from the cart's content."""
    for incoming_line_item in incoming_line_items:
        yield DbLineItem(
            line_item_id=incoming_line_item.id,
            order=db_order,
            product_id=incoming_line_item.product_id,
            product_number=incoming_line_item.product_number,
            product_type=incoming_line_item.product_type,
            name=incoming_line_item.name,
            unit_price=incoming_line_item.unit_price.amount,
            tax_rate=incoming_line_item.tax_rate,
            quantity=incoming_line_item.quantity,
            line_amount=incoming_line_item.line_amount.amount,
            processing_required=incoming_line_item.processing_required,
        )


def _reduce_product_stock(incoming_order: IncomingOrder) -> None:
    """Reduce product stock according to what is in the cart."""
    for line_item in incoming_order.line_items:
        product_service.decrease_quantity(
            line_item.product_id, line_item.quantity, commit=False
        )

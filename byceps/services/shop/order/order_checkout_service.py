"""
byceps.services.shop.order.order_checkout_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

from moneyed import Currency
from sqlalchemy.exc import IntegrityError
import structlog

from byceps.database import db
from byceps.events.shop import ShopOrderPlacedEvent
from byceps.services.shop.article import article_service
from byceps.services.shop.cart.models import Cart, CartItem
from byceps.services.shop.shop import shop_service
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront import storefront_service
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user import user_service
from byceps.util.result import Err, Ok, Result

from . import (
    order_log_service,
    order_sequence_service,
    order_service,
)
from .dbmodels.line_item import DbLineItem
from .dbmodels.order import DbOrder
from .models.checkout import IncomingLineItem, IncomingOrder
from .models.number import OrderNumber
from .models.order import (
    Order,
    Orderer,
)


log = structlog.get_logger()


def place_order(
    storefront_id: StorefrontID,
    orderer: Orderer,
    cart: Cart,
    *,
    created_at: datetime | None = None,
) -> Result[tuple[Order, ShopOrderPlacedEvent], None]:
    """Place an order for one or more articles."""
    storefront = storefront_service.get_storefront(storefront_id)
    shop = shop_service.get_shop(storefront.shop_id)

    orderer_user = user_service.get_user(orderer.user_id)

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

    incoming_order = build_incoming_order(
        created_at, shop.id, storefront.id, orderer, shop.currency, cart
    )

    db_order = _build_db_order(incoming_order, order_number)

    db_line_items = list(
        _build_db_line_items(incoming_order.line_items, db_order)
    )
    db_order._total_amount = incoming_order.total_amount.amount
    db_order.processing_required = incoming_order.processing_required

    db.session.add(db_order)
    db.session.add_all(db_line_items)

    _reduce_article_stock(incoming_order)

    try:
        db.session.commit()
    except IntegrityError as e:
        log.error('Order placement failed', order_number=order_number, exc=e)
        db.session.rollback()
        return Err(None)

    order = order_service._order_to_transfer_object(db_order)

    occurred_at = order.created_at

    # Create log entry in separate step as order ID is not available earlier.
    log_entry_data = {'initiator_id': str(orderer_user.id)}
    order_log_service.create_entry(
        'order-placed', order.id, log_entry_data, occurred_at=occurred_at
    )

    event = ShopOrderPlacedEvent(
        occurred_at=occurred_at,
        initiator_id=orderer_user.id,
        initiator_screen_name=orderer_user.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer_user.id,
        orderer_screen_name=orderer_user.screen_name,
    )

    log.info('Order placed', shop_order_placed_event=event)

    return Ok((order, event))


def build_incoming_order(
    created_at: datetime,
    shop_id: ShopID,
    storefront_id: StorefrontID,
    orderer: Orderer,
    currency: Currency,
    cart: Cart,
) -> IncomingOrder:
    """Build an incoming order object."""
    line_items = list(_build_incoming_line_items(cart.get_items()))

    total_amount = cart.calculate_total_amount()

    processing_required = any(
        line_item.processing_required for line_item in line_items
    )

    return IncomingOrder(
        created_at=created_at,
        shop_id=shop_id,
        storefront_id=storefront_id,
        orderer=orderer,
        line_items=line_items,
        total_amount=total_amount,
        processing_required=processing_required,
    )


def _build_incoming_line_items(
    cart_items: list[CartItem],
) -> Iterator[IncomingLineItem]:
    """Build incoming line item objects from the cart's content."""
    for cart_item in cart_items:
        article = cart_item.article
        quantity = cart_item.quantity
        line_amount = cart_item.line_amount

        yield IncomingLineItem(
            article_id=article.id,
            article_number=article.item_number,
            article_type=article.type_,
            description=article.description,
            unit_price=article.price,
            tax_rate=article.tax_rate,
            quantity=quantity,
            line_amount=line_amount,
            processing_required=article.processing_required,
        )


def _build_db_order(
    incoming_order: IncomingOrder, order_number: OrderNumber
) -> DbOrder:
    """Build an order."""
    orderer = incoming_order.orderer

    return DbOrder(
        incoming_order.created_at,
        incoming_order.shop_id,
        incoming_order.storefront_id,
        order_number,
        orderer.user_id,
        orderer.company,
        orderer.first_name,
        orderer.last_name,
        orderer.country,
        orderer.zip_code,
        orderer.city,
        orderer.street,
        incoming_order.total_amount.currency,
    )


def _build_db_line_items(
    incoming_line_items: list[IncomingLineItem], db_order: DbOrder
) -> Iterator[DbLineItem]:
    """Build line items from the cart's content."""
    for incoming_line_item in incoming_line_items:
        yield DbLineItem(
            db_order,
            incoming_line_item.article_id,
            incoming_line_item.article_number,
            incoming_line_item.article_type,
            incoming_line_item.description,
            incoming_line_item.unit_price.amount,
            incoming_line_item.tax_rate,
            incoming_line_item.quantity,
            incoming_line_item.line_amount.amount,
            incoming_line_item.processing_required,
        )


def _reduce_article_stock(incoming_order: IncomingOrder) -> None:
    """Reduce article stock according to what is in the cart."""
    for line_item in incoming_order.line_items:
        article_service.decrease_quantity(
            line_item.article_id, line_item.quantity, commit=False
        )

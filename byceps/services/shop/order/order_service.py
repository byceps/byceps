"""
byceps.services.shop.order.order_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
import dataclasses
from datetime import datetime, timedelta

from flask_babel import lazy_gettext
from sqlalchemy import select

from byceps.database import db, paginate, Pagination
from byceps.services.shop.invoice import order_invoice_service
from byceps.services.shop.shop.dbmodels import DbShop
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user import user_service
from byceps.services.user.models.user import UserID
from byceps.util.result import Err, Ok, Result

from . import (
    order_payment_service,
)
from .dbmodels.order import DbOrder
from .errors import (
    OrderNotPaidError,
)
from .models.detailed_order import AdminDetailedOrder, DetailedOrder
from .models.number import OrderNumber
from .models.order import (
    AdminOrderListItem,
    Order,
    OrderID,
    PaymentState,
    SiteOrderListItem,
)
from .order_domain_service import OVERDUE_THRESHOLD
from .order_helper_service import (
    to_admin_order_list_item,
    to_detailed_order,
    to_order,
    to_site_order_list_item,
)


def count_open_orders(shop_id: ShopID) -> int:
    """Return the number of open orders for the shop."""
    return (
        db.session.scalar(
            select(db.func.count(DbOrder.id))
            .filter_by(shop_id=shop_id)
            .filter_by(_payment_state=PaymentState.open.name)
        )
        or 0
    )


def count_orders_per_payment_state(shop_id: ShopID) -> dict[PaymentState, int]:
    """Count orders for the shop, grouped by payment state."""
    counts_by_payment_state = dict.fromkeys(PaymentState, 0)

    rows = db.session.execute(
        select(DbOrder._payment_state, db.func.count(DbOrder.id))
        .filter(DbOrder.shop_id == shop_id)
        .group_by(DbOrder._payment_state)
    ).all()

    for payment_state_str, count in rows:
        payment_state = PaymentState[payment_state_str]
        counts_by_payment_state[payment_state] = count

    return counts_by_payment_state


def count_orders_per_payment_state_via_order_prefix(
    order_number_prefix: str,
) -> dict[PaymentState, int]:
    """Count orders with the order number prefix, grouped by payment state."""
    counts_by_payment_state = dict.fromkeys(PaymentState, 0)

    rows = db.session.execute(
        select(DbOrder._payment_state, db.func.count(DbOrder.id))
        .filter(DbOrder.order_number.like(order_number_prefix + '%'))
        .group_by(DbOrder._payment_state)
    ).all()

    for payment_state_str, count in rows:
        payment_state = PaymentState[payment_state_str]
        counts_by_payment_state[payment_state] = count

    return counts_by_payment_state


def _find_db_order(order_id: OrderID) -> DbOrder | None:
    """Return the order database entity with that id, or `None` if not
    found.
    """
    return db.session.get(DbOrder, order_id)


def get_db_order(order_id: OrderID) -> DbOrder:
    """Return the order database entity with that id, or raise an
    exception.
    """
    db_order = _find_db_order(order_id)

    if db_order is None:
        raise ValueError(f'Unknown order ID "{order_id}"')

    return db_order


def find_order(order_id: OrderID) -> Order | None:
    """Return the order with that id, or `None` if not found."""
    db_order = _find_db_order(order_id)

    if db_order is None:
        return None

    orderer_user = user_service.get_user(db_order.placed_by_id)
    return to_order(db_order, orderer_user)


def get_order(order_id: OrderID) -> Order:
    """Return the order with that id, or raise an exception."""
    db_order = get_db_order(order_id)
    orderer_user = user_service.get_user(db_order.placed_by_id)
    return to_order(db_order, orderer_user)


def find_order_with_details(order_id: OrderID) -> DetailedOrder | None:
    """Return the order with that id, or `None` if not found."""
    db_order = (
        db.session.scalars(
            select(DbOrder)
            .options(
                db.joinedload(DbOrder.line_items),
            )
            .filter_by(id=order_id)
        )
        .unique()
        .one_or_none()
    )

    if db_order is None:
        return None

    placed_by = user_service.get_user(
        db_order.placed_by_id, include_avatar=True
    )

    return to_detailed_order(db_order, placed_by)


def find_order_with_details_for_admin(
    order_id: OrderID,
) -> AdminDetailedOrder | None:
    """Return the order with that id, or `None` if not found."""
    detailed_order = find_order_with_details(order_id)

    if detailed_order is None:
        return None

    invoices = order_invoice_service.get_invoices_for_order(detailed_order.id)
    payments = order_payment_service.get_payments_for_order(detailed_order.id)

    # Copy other attributes from `DetailedOrder` object.
    detailed_order_attributes = {
        field.name: getattr(detailed_order, field.name)
        for field in dataclasses.fields(detailed_order)
    }

    return AdminDetailedOrder(
        invoices=invoices,
        payments=payments,
        **detailed_order_attributes,
    )


def find_order_by_order_number(order_number: OrderNumber) -> Order | None:
    """Return the order with that order number, or `None` if not found."""
    db_order = db.session.execute(
        select(DbOrder).filter_by(order_number=order_number)
    ).scalar_one_or_none()

    if db_order is None:
        return None

    orderer_user = user_service.get_user(db_order.placed_by_id)
    return to_order(db_order, orderer_user)


def get_orders_for_order_numbers(
    order_numbers: set[OrderNumber],
) -> list[Order]:
    """Return the orders with those order numbers."""
    if not order_numbers:
        return []

    db_orders = (
        db.session.scalars(
            select(DbOrder)
            .options(db.joinedload(DbOrder.line_items))
            .filter(DbOrder.order_number.in_(order_numbers))
        )
        .unique()
        .all()
    )

    return _db_orders_to_transfer_objects_with_orderer_users(db_orders)


def get_order_ids_for_order_numbers(
    order_numbers: set[OrderNumber],
) -> dict[OrderNumber, OrderID]:
    """Return the order IDs for those order numbers."""
    if not order_numbers:
        return {}

    order_ids_and_numbers = db.session.execute(
        select(DbOrder.id, DbOrder.order_number).filter(
            DbOrder.order_number.in_(order_numbers)
        )
    ).all()

    return {
        order_number: order_id
        for order_id, order_number in order_ids_and_numbers
    }


def get_order_count_by_shop_id() -> dict[ShopID, int]:
    """Return order count (including 0) per shop, indexed by shop ID."""
    shop_ids_and_order_counts = (
        db.session.execute(
            select(DbShop.id, db.func.count(DbOrder.shop_id))
            .outerjoin(DbOrder)
            .group_by(DbShop.id)
        )
        .unique()
        .tuples()
        .all()
    )

    return dict(shop_ids_and_order_counts)


def get_orders(order_ids: frozenset[OrderID]) -> list[Order]:
    """Return the orders with these ids."""
    if not order_ids:
        return []

    db_orders = (
        db.session.scalars(
            select(DbOrder)
            .options(db.joinedload(DbOrder.line_items))
            .filter(DbOrder.id.in_(order_ids))
        )
        .unique()
        .all()
    )

    return _db_orders_to_transfer_objects_with_orderer_users(db_orders)


def get_orders_for_shop_paginated(
    shop_id: ShopID,
    page: int,
    per_page: int,
    *,
    search_term=None,
    only_payment_state: PaymentState | None = None,
    only_overdue: bool | None = None,
    only_processed: bool | None = None,
) -> Pagination:
    """Return all orders for that shop, ordered by creation date.

    If a payment state is specified, only orders in that state are
    returned.
    """
    stmt = (
        select(DbOrder)
        .options(db.joinedload(DbOrder.line_items))
        .filter_by(shop_id=shop_id)
        .order_by(DbOrder.created_at.desc())
    )

    if search_term:
        ilike_pattern = f'%{search_term}%'
        stmt = stmt.filter(DbOrder.order_number.ilike(ilike_pattern))

    if only_payment_state is not None:
        stmt = stmt.filter_by(_payment_state=only_payment_state.name)

        if (only_payment_state == PaymentState.open) and (
            only_overdue is not None
        ):
            now = datetime.utcnow()

            if only_overdue:
                stmt = stmt.filter(DbOrder.created_at + OVERDUE_THRESHOLD < now)
            else:
                stmt = stmt.filter(
                    DbOrder.created_at + OVERDUE_THRESHOLD >= now
                )

    if only_processed is not None:
        stmt = stmt.filter(DbOrder.processing_required == True)  # noqa: E712

        if only_processed:
            stmt = stmt.filter(DbOrder.processed_at.is_not(None))
        else:
            stmt = stmt.filter(DbOrder.processed_at.is_(None))

    paginated_orders = paginate(stmt, page, per_page)

    paginated_orders.items = _to_admin_order_list_items(paginated_orders.items)

    return paginated_orders


def _to_admin_order_list_items(
    db_orders: list[DbOrder],
) -> list[AdminOrderListItem]:
    orderer_ids = {db_order.placed_by_id for db_order in db_orders}
    orderers_by_id = user_service.get_users_indexed_by_id(
        orderer_ids, include_avatars=True
    )

    return [
        to_admin_order_list_item(db_order, orderers_by_id)
        for db_order in db_orders
    ]


def get_overdue_orders(
    shop_id: ShopID, older_than: timedelta, *, limit: int | None = None
) -> list[Order]:
    """Return all overdue orders for that shop, ordered by creation date."""
    now = datetime.utcnow()

    db_orders = (
        db.session.scalars(
            select(DbOrder)
            .options(db.joinedload(DbOrder.line_items))
            .filter_by(shop_id=shop_id)
            .filter_by(_payment_state=PaymentState.open.name)
            .filter(DbOrder.created_at + older_than < now)
            .order_by(DbOrder.created_at)
            .limit(limit)
        )
        .unique()
        .all()
    )

    orderer_ids = {db_order.placed_by_id for db_order in db_orders}
    orderers_by_id = user_service.get_users_indexed_by_id(orderer_ids)

    return [
        to_order(db_order, orderers_by_id[db_order.placed_by_id])
        for db_order in db_orders
    ]


def get_orders_placed_by_user(user_id: UserID) -> list[Order]:
    """Return orders placed by the user."""
    db_orders = (
        db.session.scalars(
            select(DbOrder)
            .options(
                db.joinedload(DbOrder.line_items),
            )
            .filter_by(placed_by_id=user_id)
            .order_by(DbOrder.created_at.desc())
        )
        .unique()
        .all()
    )

    return _db_orders_to_transfer_objects_with_orderer_users(db_orders)


def get_orders_placed_by_user_for_storefront(
    user_id: UserID, storefront_id: StorefrontID
) -> list[SiteOrderListItem]:
    """Return orders placed by the user through that storefront."""
    db_orders = (
        db.session.scalars(
            select(DbOrder)
            .options(
                db.joinedload(DbOrder.line_items),
            )
            .filter_by(storefront_id=storefront_id)
            .filter_by(placed_by_id=user_id)
            .order_by(DbOrder.created_at.desc())
        )
        .unique()
        .all()
    )

    orderer_ids = {db_order.placed_by_id for db_order in db_orders}
    orderers_by_id = user_service.get_users_indexed_by_id(orderer_ids)

    return [
        to_site_order_list_item(db_order, orderers_by_id)
        for db_order in db_orders
    ]


def has_user_placed_orders(user_id: UserID, shop_id: ShopID) -> bool:
    """Return `True` if the user has placed orders in that shop."""
    orders_total = (
        db.session.scalar(
            select(db.func.count(DbOrder.id))
            .filter_by(shop_id=shop_id)
            .filter_by(placed_by_id=user_id)
        )
        or 0
    )

    return orders_total > 0


_PAYMENT_METHOD_LABELS = {
    'bank_transfer': lazy_gettext('bank transfer'),
    'cash': lazy_gettext('cash'),
    'direct_debit': lazy_gettext('direct debit'),
    'free': lazy_gettext('free'),
}


def find_payment_method_label(payment_method: str) -> str | None:
    """Return a label for the payment method."""
    label = _PAYMENT_METHOD_LABELS.get(payment_method)
    return label or payment_method


def get_payment_date(order_id: OrderID) -> Result[datetime, OrderNotPaidError]:
    """Return the date the order has been marked as paid."""
    paid_at = db.session.scalar(
        select(DbOrder.payment_state_updated_at).filter_by(id=order_id)
    )

    if not paid_at:
        return Err(OrderNotPaidError())

    return Ok(paid_at)


def _db_orders_to_transfer_objects_with_orderer_users(
    db_orders: Sequence[DbOrder], *, include_avatars: bool = False
) -> list[Order]:
    orderer_ids = {db_order.placed_by_id for db_order in db_orders}
    orderers_by_id = user_service.get_users_indexed_by_id(
        orderer_ids, include_avatars=True
    )

    return [
        to_order(db_order, orderers_by_id[db_order.placed_by_id])
        for db_order in db_orders
    ]

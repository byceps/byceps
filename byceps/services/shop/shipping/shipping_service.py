"""
byceps.services.shop.shipping.shipping_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import Counter, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass

from sqlalchemy import select

from byceps.database import db
from byceps.services.shop.order.dbmodels.line_item import DbLineItem
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.product.dbmodels.product import DbProduct
from byceps.services.shop.product.models import ProductID
from byceps.services.shop.shop.models import ShopID

from .models import ProductToShip


def get_products_to_ship(shop_id: ShopID) -> list[ProductToShip]:
    """Return products that need, or likely need, to be shipped soon."""
    line_item_quantities = list(_find_line_items(shop_id))

    product_ids = {liq.product_id for liq in line_item_quantities}
    product_names = _get_product_names(product_ids)

    return list(
        _aggregate_ordered_product_quantites(
            line_item_quantities, product_names
        )
    )


@dataclass(frozen=True)
class LineItemQuantity:
    product_id: ProductID
    payment_state: PaymentState
    quantity: int


def _find_line_items(shop_id: ShopID) -> Iterator[LineItemQuantity]:
    """Return relevant line items with quantities."""
    common_stmt = (
        select(DbLineItem)
        .join(DbOrder)
        .filter(DbOrder.shop_id == shop_id)
        .options(db.joinedload(DbLineItem.order))
        .filter(DbLineItem.processing_required == True)  # noqa: E712
    )

    definitive_line_items = (
        db.session.scalars(
            common_stmt.filter(
                DbOrder._payment_state == PaymentState.paid.name
            ).filter(DbOrder.processed_at.is_(None))
        )
        .unique()
        .all()
    )

    potential_line_items = (
        db.session.scalars(
            common_stmt.filter(DbOrder._payment_state == PaymentState.open.name)
        )
        .unique()
        .all()
    )

    db_line_items = list(definitive_line_items) + list(potential_line_items)

    for db_line_item in db_line_items:
        yield LineItemQuantity(
            product_id=db_line_item.product_id,
            payment_state=db_line_item.order.payment_state,
            quantity=db_line_item.quantity,
        )


def _aggregate_ordered_product_quantites(
    line_item_quantities: list[LineItemQuantity],
    product_names: dict[ProductID, str],
) -> Iterator[ProductToShip]:
    """Aggregate product quantities per payment state."""
    d: defaultdict[ProductID, Counter] = defaultdict(Counter)

    for liq in line_item_quantities:
        d[liq.product_id][liq.payment_state] += liq.quantity

    for product_id, counter in d.items():
        name = product_names[product_id]
        quantity_paid = counter[PaymentState.paid]
        quantity_open = counter[PaymentState.open]

        yield ProductToShip(
            product_id=product_id,
            name=name,
            quantity_paid=quantity_paid,
            quantity_open=quantity_open,
            quantity_total=quantity_paid + quantity_open,
        )


def _get_product_names(product_ids: set[ProductID]) -> dict[ProductID, str]:
    """Look up names of the specified products."""
    if not product_ids:
        return {}

    db_products = db.session.scalars(
        select(DbProduct)
        .options(db.load_only(DbProduct.id, DbProduct.name))
        .filter(DbProduct.id.in_(product_ids))
    ).all()

    return {db_product.id: db_product.name for db_product in db_products}

"""
byceps.services.shop.order.paid_products_report_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import TypeAlias

from flask_babel import lazy_gettext

from byceps.services.party.models import Party, PartyID
from byceps.services.shop.order import ordered_products_service
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import Order, OrderID, PaymentState
from byceps.services.shop.product.models import Product, ProductNumber
from byceps.services.user import user_service
from byceps.services.user.models.user import UserForAdmin, UserID
from byceps.util.export import serialize_tuples_to_csv
from byceps.util.iterables import find


@dataclass(frozen=True, slots=True)
class ProductQuantity:
    item_number: ProductNumber
    quantity: int


@dataclass(frozen=True, slots=True)
class OrderSummary:
    order_id: OrderID
    order_number: OrderNumber
    orderer: UserForAdmin
    product_quantities: list[ProductQuantity]


@dataclass(frozen=True, slots=True)
class PaidProductsReport:
    products: list[Product]
    order_summaries: list[OrderSummary]


CsvRow: TypeAlias = tuple[str, ...]


def get_paid_products_report(
    party: Party, products: list[Product]
) -> PaidProductsReport:
    orders = list(_select_unique_orders(_collect_product_orders(products)))

    orderers_by_id = _get_orderers_by_id(orders)

    order_summaries = [
        _assemble_order_summary(party.id, order, orderers_by_id, products)
        for order in orders
    ]

    order_summaries.sort(key=lambda summary: summary.order_number)

    return PaidProductsReport(
        products=products,
        order_summaries=order_summaries,
    )


def _collect_product_orders(products: list[Product]) -> Iterator[Order]:
    for product in products:
        yield from ordered_products_service.get_orders_including_product(
            product.id, only_payment_state=PaymentState.paid
        )


def _select_unique_orders(orders: Iterable[Order]) -> Iterator[Order]:
    unique_order_ids = set()

    for order in orders:
        if order.id in unique_order_ids:
            continue

        unique_order_ids.add(order.id)
        yield order


def _get_orderers_by_id(orders: Iterable[Order]) -> dict[UserID, UserForAdmin]:
    orderer_ids = {order.placed_by.id for order in orders}
    orderers = user_service.get_users_for_admin(orderer_ids)
    return {orderer.id: orderer for orderer in orderers}


def _assemble_order_summary(
    party_id: PartyID,
    order: Order,
    orderers_by_id: dict[UserID, UserForAdmin],
    products: list[Product],
) -> OrderSummary:
    orderer = orderers_by_id[order.placed_by.id]

    product_quantities = [
        ProductQuantity(
            item_number=product.item_number,
            quantity=get_product_quantity(product.item_number, order),
        )
        for product in products
    ]

    return OrderSummary(
        order_id=order.id,
        order_number=order.order_number,
        orderer=orderer,
        product_quantities=product_quantities,
    )


def get_product_quantity(product_number: ProductNumber, order: Order) -> int:
    product_line_item = find(
        order.line_items,
        lambda line_item: line_item.product_number == product_number,
    )

    if not product_line_item:
        return 0

    return product_line_item.quantity


def export_paid_products_report_as_csv(report: PaidProductsReport) -> str:
    header_row = _assemble_csv_header_row(report.products)
    data_rows = _assemble_csv_data_rows(report.order_summaries)
    all_rows = [header_row] + data_rows

    lines = serialize_tuples_to_csv(all_rows)
    return ''.join(lines)


def _assemble_csv_header_row(products: list[Product]) -> CsvRow:
    fixed_column_names = (
        lazy_gettext('Order number'),
        lazy_gettext('Username'),
        lazy_gettext('Name'),
    )
    product_names = tuple(product.name for product in products)
    return fixed_column_names + product_names


def _assemble_csv_data_rows(
    order_summaries: list[OrderSummary],
) -> list[CsvRow]:
    return [
        tuple(_assemble_data_row(order_summary))
        for order_summary in order_summaries
    ]


def _assemble_data_row(order_summary: OrderSummary) -> Iterator[str]:
    yield from (
        str(order_summary.order_number),
        order_summary.orderer.screen_name or lazy_gettext('unknown'),
        order_summary.orderer.detail.full_name or lazy_gettext('unknown'),
    )

    for product_quantity in order_summary.product_quantities:
        yield str(product_quantity.quantity)

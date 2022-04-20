"""
byceps.services.shop.order.invoice_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from ....database import db

from .dbmodels.invoice import Invoice as DbInvoice
from . import log_service
from .transfer.invoice import Invoice
from .transfer.order import OrderID


def add_invoice(
    order_id: OrderID,
    number: str,
    *,
    url: Optional[str] = None,
) -> Invoice:
    """Add an invoice to an order."""
    db_invoice = DbInvoice(order_id, number, url=url)
    db.session.add(db_invoice)

    invoice = _db_entity_to_invoice(db_invoice)

    log_entry_data = {'invoice_number': invoice.number}
    db_log_entry = log_service.build_log_entry(
        'order-invoice-created', invoice.order_id, log_entry_data
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return invoice


def get_invoices_for_order(order_id: OrderID) -> list[Invoice]:
    """Return the invoices for that order."""
    db_invoices = db.session.scalars(
        select(DbInvoice)
        .filter_by(order_id=order_id)
    ).all()

    return [_db_entity_to_invoice(db_invoice) for db_invoice in db_invoices]


def _db_entity_to_invoice(db_invoice: DbInvoice) -> Invoice:
    return Invoice(
        id=db_invoice.id,
        order_id=db_invoice.order_id,
        number=db_invoice.number,
        url=db_invoice.url,
    )

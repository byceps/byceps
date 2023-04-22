"""
byceps.services.shop.order.order_invoice_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import select

from byceps.database import db

from . import order_log_service
from .dbmodels.invoice import DbInvoice
from .models.invoice import Invoice
from .models.order import OrderID


def add_invoice(
    order_id: OrderID,
    number: str,
    *,
    url: str | None = None,
) -> Invoice:
    """Add an invoice to an order."""
    db_invoice = DbInvoice(order_id, number, url=url)
    db.session.add(db_invoice)
    db.session.commit()

    invoice = _db_entity_to_invoice(db_invoice)

    log_entry_data = {'invoice_number': invoice.number}
    order_log_service.create_entry(
        'order-invoice-created', invoice.order_id, log_entry_data
    )

    return invoice


def get_invoices_for_order(order_id: OrderID) -> list[Invoice]:
    """Return the invoices for that order."""
    db_invoices = db.session.scalars(
        select(DbInvoice).filter_by(order_id=order_id)
    ).all()

    return [_db_entity_to_invoice(db_invoice) for db_invoice in db_invoices]


def _db_entity_to_invoice(db_invoice: DbInvoice) -> Invoice:
    return Invoice(
        id=db_invoice.id,
        order_id=db_invoice.order_id,
        number=db_invoice.number,
        url=db_invoice.url,
    )

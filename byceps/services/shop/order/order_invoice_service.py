"""
byceps.services.shop.order.order_invoice_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.models.user import UserID

from . import order_log_service
from .dbmodels.invoice import DbInvoice
from .models.invoice import Invoice
from .models.order import OrderID


def add_invoice(
    order_id: OrderID,
    initiator_id: UserID,
    number: str,
    *,
    url: str | None = None,
) -> Invoice:
    """Add an invoice to an order."""
    db_invoice = DbInvoice(order_id, number, url=url)
    db.session.add(db_invoice)

    log_entry_data = {
        'initiator_id': str(initiator_id),
        'invoice_number': db_invoice.number,
    }
    db_log_entry = order_log_service.build_db_entry(
        'order-invoice-created', db_invoice.order_id, log_entry_data
    )
    db.session.add(db_log_entry)

    db.session.commit()

    return _db_entity_to_invoice(db_invoice)


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

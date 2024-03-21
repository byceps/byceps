"""
byceps.services.shop.order.order_invoice_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy import select

from byceps.database import db
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from . import order_log_service
from .dbmodels.invoice import DbInvoice
from .dbmodels.order import DbOrder
from .models.invoice import Invoice
from .models.log import OrderLogEntry
from .models.order import OrderID


def add_invoice(
    order_id: OrderID,
    initiator: User,
    number: str,
    *,
    url: str | None = None,
) -> Invoice:
    """Add an invoice to an order."""
    db_order = db.session.get(DbOrder, order_id)
    if db_order is None:
        raise ValueError(f'Unknown order ID "{order_id}"')

    db_invoice = DbInvoice(order_id, number, url=url)
    db.session.add(db_invoice)

    log_entry = _build_order_invoice_created_log_entry(
        order_id, initiator, number
    )
    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db_order.invoice_created_at = log_entry.occurred_at

    db.session.commit()

    return _db_entity_to_invoice(db_invoice)


def _build_order_invoice_created_log_entry(
    order_id: OrderID,
    initiator: User,
    invoice_number: str,
) -> OrderLogEntry:
    data = {
        'initiator_id': str(initiator.id),
        'invoice_number': invoice_number,
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=datetime.utcnow(),
        event_type='order-invoice-created',
        order_id=order_id,
        data=data,
    )


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

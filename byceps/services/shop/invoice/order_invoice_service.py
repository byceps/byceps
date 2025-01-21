"""
byceps.services.shop.invoice.order_invoice_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import select

from byceps.database import db
from byceps.services.shop.invoice.errors import InvoiceError
from byceps.services.shop.invoice.models import DownloadableInvoice
from byceps.services.shop.order import order_log_service
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.detailed_order import AdminDetailedOrder
from byceps.services.shop.order.models.order import OrderID
from byceps.services.user.models.user import User
from byceps.util.result import Result

from . import invoiceninja_service, order_invoice_domain_service
from .dbmodels import DbInvoice
from .models import Invoice


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

    invoice, log_entry = order_invoice_domain_service.create_invoice(
        order_id, initiator, number, url=url
    )

    db_invoice = DbInvoice(
        invoice.id, invoice.order_id, invoice.number, url=invoice.url
    )
    db.session.add(db_invoice)

    db_log_entry = order_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db_order.invoice_created_at = log_entry.occurred_at

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


def get_downloadable_invoice_for_order(
    order: AdminDetailedOrder, draft: bool, initiator: User
) -> Result[DownloadableInvoice, InvoiceError]:
    """Get a downloadable invoice for the order.

    Create it if it does not exist.
    """
    return invoiceninja_service.get_downloadable_invoice_for_order(
        order, draft, initiator
    )

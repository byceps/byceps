"""
byceps.services.shop.order.invoice.order_invoice_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.services.shop.order.models.log import OrderLogEntry
from byceps.services.shop.order.models.order import OrderID
from byceps.services.user.models.user import User
from byceps.util.uuid import generate_uuid7

from .models import Invoice


def create_invoice(
    order_id: OrderID,
    initiator: User,
    number: str,
    *,
    url: str | None = None,
) -> tuple[Invoice, OrderLogEntry]:
    """Create an invoice for an order."""
    invoice = Invoice(
        id=generate_uuid7(),
        order_id=order_id,
        number=number,
        url=url,
    )

    log_entry = _build_order_invoice_created_log_entry(invoice, initiator)

    return invoice, log_entry


def _build_order_invoice_created_log_entry(
    invoice: Invoice, initiator: User
) -> OrderLogEntry:
    data = {
        'initiator_id': str(initiator.id),
        'invoice_number': invoice.number,
    }

    return OrderLogEntry(
        id=generate_uuid7(),
        occurred_at=datetime.utcnow(),
        event_type='order-invoice-created',
        order_id=invoice.order_id,
        data=data,
    )

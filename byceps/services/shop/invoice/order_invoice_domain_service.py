"""
byceps.services.shop.invoice.order_invoice_domain_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.order.log import order_log_domain_service
from byceps.services.shop.order.log.models import OrderLogEntry
from byceps.services.shop.order.models.order import OrderID
from byceps.services.user.models import User
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

    log_entry = order_log_domain_service.build_invoice_created_entry(
        invoice, initiator
    )

    return invoice, log_entry

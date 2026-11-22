"""
byceps.services.shop.invoice.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy.types import UnicodeText, Uuid

from byceps.database import db
from byceps.services.shop.order.models.order import OrderID


class DbInvoice(db.Model):
    """An invoice for an order.

    Currently used to link numbers and URLs of externally managed
    invoices to orders.
    """

    __tablename__ = 'shop_order_invoices'
    __table_args__ = (UniqueConstraint('order_id', 'number'),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    order_id: Mapped[OrderID] = mapped_column(
        Uuid, ForeignKey('shop_orders.id'), index=True
    )
    number: Mapped[str] = mapped_column(UnicodeText, index=True)
    url: Mapped[str | None] = mapped_column(UnicodeText)

    def __init__(
        self,
        invoice_id: UUID,
        order_id: OrderID,
        number: str,
        *,
        url: str | None = None,
    ) -> None:
        self.id = invoice_id
        self.order_id = order_id
        self.number = number
        self.url = url

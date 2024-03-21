"""
byceps.services.shop.order.dbmodels.invoice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.shop.order.models.order import OrderID


class DbInvoice(db.Model):
    """An invoice for an order.

    Currently used to link numbers and URLs of externally managed
    invoices to orders.
    """

    __tablename__ = 'shop_order_invoices'
    __table_args__ = (db.UniqueConstraint('order_id', 'number'),)

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    order_id: Mapped[OrderID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True
    )
    number: Mapped[str] = mapped_column(db.UnicodeText, index=True)
    url: Mapped[str | None] = mapped_column(db.UnicodeText)

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

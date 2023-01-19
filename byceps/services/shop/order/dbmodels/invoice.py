"""
byceps.services.shop.order.dbmodels.invoice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from .....database import db, generate_uuid

from ..models.order import OrderID


class DbInvoice(db.Model):
    """An invoice for an order.

    Currently used to link numbers and URLs of externally managed
    invoices to orders.
    """

    __tablename__ = 'shop_order_invoices'
    __table_args__ = (
        db.UniqueConstraint('order_id', 'number'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_id = db.Column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False
    )
    number = db.Column(db.UnicodeText, index=True, nullable=False)
    url = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        order_id: OrderID,
        number: str,
        *,
        url: Optional[str] = None,
    ) -> None:
        self.order_id = order_id
        self.number = number
        self.url = url

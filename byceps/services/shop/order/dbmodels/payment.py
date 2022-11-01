"""
byceps.services.shop.order.dbmodels.payment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from .....database import db, generate_uuid

from ..transfer.order import OrderID
from ..transfer.payment import AdditionalPaymentData


class DbPayment(db.Model):
    """A payment related to an order."""

    __tablename__ = 'shop_payments'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    order_id = db.Column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False)
    method = db.Column(db.UnicodeText, nullable=True)
    amount = db.Column(db.Numeric(7, 2), nullable=False)
    additional_data = db.Column(db.JSONB)

    def __init__(
        self,
        order_id: OrderID,
        created_at: datetime,
        method: str,
        amount: Decimal,
        additional_data: AdditionalPaymentData,
    ) -> None:
        self.order_id = order_id
        self.created_at = created_at
        self.method = method
        self.amount = amount
        self.additional_data = additional_data

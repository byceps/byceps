"""
byceps.services.shop.order.dbmodels.payment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import TYPE_CHECKING

from moneyed import Currency, get_currency, Money

if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db, generate_uuid7
from byceps.services.shop.order.models.order import OrderID
from byceps.services.shop.order.models.payment import AdditionalPaymentData


class DbPayment(db.Model):
    """A payment related to an order."""

    __tablename__ = 'shop_payments'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    order_id = db.Column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True, nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False)
    method = db.Column(db.UnicodeText, nullable=True)
    amount = db.Column(db.Numeric(7, 2), nullable=False)
    _currency = db.Column('currency', db.UnicodeText, nullable=False)
    additional_data = db.Column(db.JSONB)

    def __init__(
        self,
        order_id: OrderID,
        created_at: datetime,
        method: str,
        amount: Money,
        additional_data: AdditionalPaymentData,
    ) -> None:
        self.order_id = order_id
        self.created_at = created_at
        self.method = method
        self.amount = amount.amount
        self.currency = amount.currency
        self.additional_data = additional_data

    @hybrid_property
    def currency(self) -> Currency:
        return get_currency(self._currency)

    @currency.setter
    def currency(self, currency: Currency) -> None:
        self._currency = currency.code

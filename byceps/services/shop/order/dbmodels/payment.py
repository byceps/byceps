"""
byceps.services.shop.order.dbmodels.payment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from moneyed import Currency, get_currency, Money
from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.order.models.order import OrderID
from byceps.services.shop.order.models.payment import AdditionalPaymentData


class DbPayment(db.Model):
    """A payment related to an order."""

    __tablename__ = 'shop_payments'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    order_id: Mapped[OrderID] = mapped_column(
        db.Uuid, db.ForeignKey('shop_orders.id'), index=True
    )
    created_at: Mapped[datetime] = mapped_column(db.DateTime)
    method: Mapped[Optional[str]] = mapped_column(db.UnicodeText)
    amount: Mapped[Decimal] = mapped_column(db.Numeric(7, 2))
    _currency: Mapped[str] = mapped_column('currency', db.UnicodeText)
    additional_data: Mapped[AdditionalPaymentData] = mapped_column(db.JSONB)

    def __init__(
        self,
        payment_id: UUID,
        order_id: OrderID,
        created_at: datetime,
        method: str,
        amount: Money,
        additional_data: AdditionalPaymentData,
    ) -> None:
        self.id = payment_id
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

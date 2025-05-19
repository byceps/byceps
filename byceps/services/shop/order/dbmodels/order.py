"""
byceps.services.shop.order.dbmodels.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from moneyed import Currency, get_currency, Money
from sqlalchemy.orm import Mapped, mapped_column, relationship


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import OrderID, PaymentState
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.dbmodels import DbStorefront
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder


class DbOrder(db.Model):
    """An order for products, placed by a user."""

    __tablename__ = 'shop_orders'

    id: Mapped[OrderID] = mapped_column(db.Uuid, primary_key=True)
    created_at: Mapped[datetime]
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    storefront_id: Mapped[StorefrontID] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_storefronts.id'),
        index=True,
    )
    storefront: Mapped[DbStorefront] = relationship(DbStorefront)
    order_number: Mapped[OrderNumber] = mapped_column(
        db.UnicodeText, unique=True
    )
    placed_by_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    placed_by: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[placed_by_id]
    )
    company: Mapped[str | None] = mapped_column(db.UnicodeText)
    first_name: Mapped[str] = mapped_column(db.UnicodeText)
    last_name: Mapped[str] = mapped_column(db.UnicodeText)
    country: Mapped[str] = mapped_column(db.UnicodeText)
    postal_code: Mapped[str] = mapped_column(db.UnicodeText)
    city: Mapped[str] = mapped_column(db.UnicodeText)
    street: Mapped[str] = mapped_column(db.UnicodeText)
    _currency: Mapped[str] = mapped_column('currency', db.UnicodeText)
    _total_amount: Mapped[Decimal] = mapped_column(
        'total_amount', db.Numeric(7, 2)
    )
    invoice_created_at: Mapped[datetime | None]
    payment_method: Mapped[str | None] = mapped_column(db.UnicodeText)
    _payment_state: Mapped[str] = mapped_column(
        'payment_state', db.UnicodeText, index=True
    )
    payment_state_updated_at: Mapped[datetime | None]
    payment_state_updated_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    payment_state_updated_by: Mapped[DbUser] = relationship(
        DbUser, foreign_keys=[payment_state_updated_by_id]
    )
    cancellation_reason: Mapped[str | None] = mapped_column(db.UnicodeText)
    processing_required: Mapped[bool]
    processed_at: Mapped[datetime | None]

    def __init__(
        self,
        order_id: OrderID,
        created_at: datetime,
        shop_id: ShopID,
        storefront_id: StorefrontID,
        order_number: OrderNumber,
        placed_by_id: UserID,
        company: str | None,
        first_name: str,
        last_name: str,
        country: str,
        postal_code: str,
        city: str,
        street: str,
        total_amount: Money,
        processing_required: bool,
    ) -> None:
        self.id = order_id
        self.created_at = created_at
        self.shop_id = shop_id
        self.storefront_id = storefront_id
        self.order_number = order_number
        self.placed_by_id = placed_by_id
        self.company = company
        self.first_name = first_name
        self.last_name = last_name
        self.country = country
        self.postal_code = postal_code
        self.city = city
        self.street = street
        self.currency = total_amount.currency
        self._total_amount = total_amount.amount
        self.payment_state = PaymentState.open
        self.processing_required = processing_required

    @hybrid_property
    def currency(self) -> Currency:
        return get_currency(self._currency)

    @currency.setter
    def currency(self, currency: Currency) -> None:
        self._currency = currency.code

    @property
    def total_amount(self) -> Money:
        return Money(self._total_amount, self.currency)

    @hybrid_property
    def payment_state(self) -> PaymentState:
        return PaymentState[self._payment_state]

    @payment_state.setter
    def payment_state(self, state: PaymentState) -> None:
        self._payment_state = state.name

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('order_number')
            .add_custom(self.payment_state.name)
            .build()
        )

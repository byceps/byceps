"""
byceps.services.shop.order.dbmodels.order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from moneyed import Currency, get_currency, Money


if TYPE_CHECKING:
    hybrid_property = property
else:
    from sqlalchemy.ext.hybrid import hybrid_property

from byceps.database import db, generate_uuid7
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder


class DbOrder(db.Model):
    """An order for articles, placed by a user."""

    __tablename__ = 'shop_orders'

    id = db.Column(db.Uuid, default=generate_uuid7, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    shop_id = db.Column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False
    )
    storefront_id = db.Column(
        db.UnicodeText,
        db.ForeignKey('shop_storefronts.id'),
        index=True,
        nullable=False,
    )
    order_number = db.Column(db.UnicodeText, unique=True, nullable=False)
    placed_by_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    placed_by = db.relationship(DbUser, foreign_keys=[placed_by_id])
    company = db.Column(db.UnicodeText, nullable=True)
    first_name = db.Column(db.UnicodeText, nullable=False)
    last_name = db.Column(db.UnicodeText, nullable=False)
    country = db.Column(db.UnicodeText, nullable=False)
    zip_code = db.Column(db.UnicodeText, nullable=False)
    city = db.Column(db.UnicodeText, nullable=False)
    street = db.Column(db.UnicodeText, nullable=False)
    _currency = db.Column('currency', db.UnicodeText, nullable=False)
    _total_amount = db.Column('total_amount', db.Numeric(7, 2), nullable=False)
    invoice_created_at = db.Column(db.DateTime, nullable=True)
    payment_method = db.Column(db.UnicodeText, nullable=True)
    _payment_state = db.Column(
        'payment_state', db.UnicodeText, index=True, nullable=False
    )
    payment_state_updated_at = db.Column(db.DateTime, nullable=True)
    payment_state_updated_by_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), nullable=True
    )
    payment_state_updated_by = db.relationship(
        DbUser, foreign_keys=[payment_state_updated_by_id]
    )
    cancelation_reason = db.Column(db.UnicodeText, nullable=True)
    processing_required = db.Column(db.Boolean, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)

    def __init__(
        self,
        created_at: datetime,
        shop_id: ShopID,
        storefront_id: StorefrontID,
        order_number: OrderNumber,
        placed_by_id: UserID,
        company: str | None,
        first_name: str,
        last_name: str,
        country: str,
        zip_code: str,
        city: str,
        street: str,
        total_amount: Money,
        processing_required: bool,
    ) -> None:
        self.created_at = created_at
        self.shop_id = shop_id
        self.storefront_id = storefront_id
        self.order_number = order_number
        self.placed_by_id = placed_by_id
        self.company = company
        self.first_name = first_name
        self.last_name = last_name
        self.country = country
        self.zip_code = zip_code
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
